"""Load and parse job applications from the raw text file."""

import re
from dataclasses import dataclass
from pathlib import Path

# Fields are separated by a dash (hyphen, en dash or em dash) with spaces around it.
SEPARATOR = re.compile(r"\s+[-–—]\s+")


@dataclass
class Application:
    company: str
    role: str
    date: str
    status: str


def parse_line(line: str) -> Application | None:
    """Parse one line like 'Company - Role - Month - status'. Returns None for blank lines."""
    line = line.strip().strip('"').rstrip(".").strip()
    if not line:
        return None

    parts = [p.strip() for p in SEPARATOR.split(line)]
    if len(parts) < 4:
        raise ValueError(f"Could not parse line: {line!r}")

    # Company is first, date and status are last; everything in between is the role
    # (some role titles contain their own ' - ').
    company, *role_parts, date, status = parts
    return Application(
        company=company,
        role=" - ".join(role_parts),
        date=date.replace("applied", "").strip(),
        status=status.lower(),
    )


def load_applications(path: Path) -> list[Application]:
    applications = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            app = parse_line(line)
            if app:
                applications.append(app)
    return applications
