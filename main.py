from collections import Counter
from pathlib import Path

from src.loader import load_applications

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "applications.txt"


def main():
    applications = load_applications(DATA_FILE)
    print(f"Total applications: {len(applications)}\n")

    status_counts = Counter(app.status for app in applications)
    for status, count in status_counts.most_common():
        print(f"  {status:<12} {count}")


if __name__ == "__main__":
    main()
