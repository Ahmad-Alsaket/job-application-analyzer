"""Convert data/applications.txt into data/applications.csv.

Pass a different input file to convert that instead; the CSV is written next to it:
    py parse_to_csv.py data/applications.sample.txt   # -> data/applications.sample.csv
"""

import csv
import sys
from dataclasses import asdict, fields
from pathlib import Path

from src.loader import Application, load_applications

BASE_DIR = Path(__file__).parent
DEFAULT_INPUT_FILE = BASE_DIR / "data" / "applications.txt"


def write_csv(applications: list[Application], path: Path) -> None:
    # utf-8-sig so Excel shows umlauts (ä, ü, ...) correctly
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[field.name for field in fields(Application)])
        writer.writeheader()
        writer.writerows(asdict(app) for app in applications)


def main():
    input_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT_FILE
    output_file = input_file.with_suffix(".csv")

    applications = load_applications(input_file)
    write_csv(applications, output_file)
    print(f"Wrote {len(applications)} rows to {output_file}")


if __name__ == "__main__":
    main()
