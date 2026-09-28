"""Ask a local Ollama model for a short plain-English summary of the job search.

The pipeline is: CSV -> pandas aggregations -> small dict of numbers -> prompt
-> Ollama -> printed summary. Only the aggregated stats are sent to the model,
never the raw application rows.

Needs Ollama running locally (https://ollama.com) with the model pulled:
    ollama run llama3.2
    py llm_readout.py                                  # data/applications.csv
    py llm_readout.py data/applications.sample.csv     # any other CSV

Set the OLLAMA_MODEL environment variable to use a different model, e.g. llama3.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

from analyze import DEFAULT_CSV_FILE, parse_month

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# Local models can be slow on the first call while they load into memory.
TIMEOUT_SECONDS = 120


def collect_stats(df: pd.DataFrame) -> dict:
    """Run the same aggregations as analyze.py, but return plain Python data."""
    status_counts = df["status"].value_counts()

    # Months with no parseable date are left out; value_counts() skips NaT.
    per_month = parse_month(df["date"]).value_counts().sort_index()

    company_counts = df["company"].str.strip().str.lower().value_counts()
    repeats = company_counts[company_counts > 1]

    # int() / str() turn numpy and pandas types into plain ones that json can handle.
    return {
        "total_applications": len(df),
        "outcomes": {status: int(n) for status, n in status_counts.items()},
        "applications_by_month": {str(month): int(n) for month, n in per_month.items()},
        "repeat_companies": {company: int(n) for company, n in repeats.items()},
    }


def build_prompt(stats: dict) -> str:
    return (
        "Here are aggregated statistics about someone's job search, as JSON:\n\n"
        f"{json.dumps(stats, indent=2)}\n\n"
        "Write a 2-3 sentence plain-English summary of the job search so far. "
        "Mention the overall outcome rate (e.g. share of interviews or rejections), "
        "whether applications per month are speeding up or slowing down, and any "
        "notable companies applied to more than once. Use only the numbers above; "
        "do not invent details. Reply with the summary only."
    )


def ask_ollama(prompt: str) -> str:
    """Send the prompt to Ollama and return the model's reply.

    Raises RuntimeError with a readable message if Ollama can't be reached.
    """
    # stream=False makes Ollama send one JSON object instead of a token stream.
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            reply = json.load(response)
    except urllib.error.HTTPError as err:
        # The server is up but refused the request, most often because the model isn't pulled.
        detail = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Ollama returned HTTP {err.code}: {detail}\n"
            f"Is the model pulled? Try: ollama pull {MODEL}"
        ) from err
    except urllib.error.URLError as err:
        # Nothing listening on the port (Ollama not started), or it timed out.
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_URL} ({err.reason}).\n"
            "Is it running? Start the Ollama app or run: ollama serve"
        ) from err
    except TimeoutError as err:
        raise RuntimeError(f"Ollama did not answer within {TIMEOUT_SECONDS} seconds.") from err

    return reply["response"].strip()


def main():
    csv_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV_FILE
    df = pd.read_csv(csv_file, encoding="utf-8-sig")

    stats = collect_stats(df)
    print("Stats sent to the model:")
    print(json.dumps(stats, indent=2))

    print(f"\nAsking {MODEL}...\n")
    try:
        summary = ask_ollama(build_prompt(stats))
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    print(summary)


if __name__ == "__main__":
    main()
