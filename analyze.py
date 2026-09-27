"""Print a short analysis of data/applications.csv.

Run parse_to_csv.py first to (re)generate the CSV from applications.txt.
Pass a different CSV to analyze that instead:
    py analyze.py data/applications.sample.csv
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).parent
DEFAULT_CSV_FILE = BASE_DIR / "data" / "applications.csv"

# Chart colours: one blue for the bars, near-black for text.
BAR_COLOR = "#2a78d6"
TEXT_COLOR = "#0b0b0b"

# Many dates are just a month name ("July", "may"). We assume those are in this year.
DEFAULT_YEAR = 2026


def print_heading(title: str) -> None:
    print(f"\n=== {title} ===")


def outcome_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    print_heading("Outcome breakdown")

    # value_counts() finds every distinct status in the data and counts it.
    counts = df["status"].value_counts()

    # Same thing again, but normalize=True gives fractions (0-1) instead of counts.
    percentages = df["status"].value_counts(normalize=True) * 100

    # Put both Series side by side in one table.
    summary = pd.DataFrame({"count": counts, "percent": percentages.round(1)})
    print(summary.to_string())

    # Return the table so plot_outcomes() can reuse it instead of recounting.
    return summary


def plot_outcomes(summary: pd.DataFrame, path: Path) -> None:
    """Save a horizontal bar chart of the outcome breakdown as a PNG."""
    # A matplotlib chart has two main objects:
    #   fig = the whole image (the "canvas" that gets saved to a file)
    #   ax  = one chart area inside it (the bars, axis labels, title all live here)
    # subplots() creates both at once. figsize is (width, height) in inches.
    fig, ax = plt.subplots(figsize=(7, 3))

    # barh() = horizontal bars. First argument: the label for each bar,
    # second: how long each bar is. Horizontal bars leave room for long labels.
    ax.barh(summary.index, summary["count"], height=0.6, color=BAR_COLOR)

    # By default the first row is drawn at the bottom. Flip it so the biggest
    # outcome (value_counts() sorts largest first) is at the top, like the table.
    ax.invert_yaxis()

    # Write "22 (71.0%)" just past the end of each bar.
    # zip() walks through the three columns together, one row at a time.
    for status, count, percent in zip(summary.index, summary["count"], summary["percent"]):
        ax.text(
            count + 0.3,             # x position: slightly right of the bar's end
            status,                  # y position: same row as the bar
            f"{count} ({percent}%)",
            va="center",             # vertically centred on the bar
            color=TEXT_COLOR,
        )

    # Every bar already has its number written on it, so the x-axis ticks
    # would just repeat that. Hide them, and the box lines (spines) around the chart.
    ax.xaxis.set_visible(False)
    for side in ["top", "right", "bottom"]:
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0, colors=TEXT_COLOR)  # no little tick marks

    ax.set_title("Application outcomes", loc="left", color=TEXT_COLOR)

    # Leave space on the right so the longest bar's label isn't cut off.
    ax.set_xlim(0, summary["count"].max() * 1.25)

    # tight_layout() shrinks the margins so nothing overlaps or gets clipped.
    fig.tight_layout()

    # Write the image to disk. dpi = dots per inch; 150 gives a sharp image.
    fig.savefig(path, dpi=150)

    # Free the memory used by the figure (matters if you make many charts).
    plt.close(fig)

    print(f"\nSaved chart to {path}")


def parse_month(date_text: pd.Series) -> pd.Series:
    """Turn loose text like '~March 2026', 'september', 'applied May' into year-month periods.

    Returns NaT (pandas' "missing date") for anything that can't be parsed.
    """
    # Normalise: lowercase and drop characters/words that aren't part of the date.
    cleaned = (
        date_text.fillna("")
        .str.lower()
        .str.replace("~", "", regex=False)
        .str.replace("applied", "", regex=False)
        .str.strip()
    )

    # Pull out a word (the month name) and an optional 4-digit year.
    # extract() returns a DataFrame with one column per (...) group.
    parts = cleaned.str.extract(r"^([a-z]+)\s*(\d{4})?$")
    month_name = parts[0]
    year = parts[1].fillna(str(DEFAULT_YEAR))  # no year given -> assume DEFAULT_YEAR

    # Let pandas convert "march 2026" into a real date. %B means full month name.
    # errors="coerce" turns anything it can't read into NaT instead of crashing.
    dates = pd.to_datetime(month_name.str.title() + " " + year, format="%B %Y", errors="coerce")

    # Keep only year + month (e.g. 2026-07), since we don't have days.
    return dates.dt.to_period("M")


def applications_by_month(df: pd.DataFrame) -> None:
    print_heading("Applications by month")

    df = df.assign(month=parse_month(df["date"]))

    # Rows where parsing failed have a missing month -> show them instead of dropping them.
    failed = df[df["month"].isna()]
    if not failed.empty:
        print(f"Could not parse the date in {len(failed)} row(s):")
        print(failed[["company", "role", "date"]].to_string())
        print()

    # Count rows per month, then sort by month (not by count) so it reads like a timeline.
    per_month = df["month"].value_counts().sort_index()
    print(per_month.to_string())


def repeat_companies(df: pd.DataFrame) -> None:
    print_heading("Companies applied to more than once")

    # Compare names case-insensitively so "Acme" and "acme" count as the same company.
    company_key = df["company"].str.strip().str.lower()

    # Count how many applications each company got.
    counts = company_key.value_counts()

    # Keep only companies that appear more than once.
    repeats = counts[counts > 1]

    if repeats.empty:
        print("None.")
    else:
        print(repeats.to_string())


def main():
    csv_file = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV_FILE
    # The chart is saved next to the CSV, e.g. data/applications_outcomes.png.
    chart_file = csv_file.with_name(f"{csv_file.stem}_outcomes.png")

    df = pd.read_csv(csv_file, encoding="utf-8-sig")
    print(f"Loaded {len(df)} applications from {csv_file}")

    summary = outcome_breakdown(df)
    plot_outcomes(summary, chart_file)
    applications_by_month(df)
    repeat_companies(df)


if __name__ == "__main__":
    main()
