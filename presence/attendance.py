"""Daily attendance records stored in a CSV file."""

from datetime import datetime

import pandas as pd

from presence import config, students

COLUMNS = ["Date", "Name", "Status", "Time"]
PRESENT, ABSENT = "Present", "Absent"


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load() -> pd.DataFrame:
    if not config.ATTENDANCE_CSV.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(config.ATTENDANCE_CSV, dtype=str, keep_default_na=False)


def _save(df: pd.DataFrame) -> None:
    config.ensure_dirs()
    df.to_csv(config.ATTENDANCE_CSV, index=False)


def _key(name: str) -> str:
    return name.strip().casefold()


def open_today() -> None:
    """Add an 'Absent' row for each student who has no record today yet."""
    df = load()
    date = today()
    recorded = {_key(n) for n in df.loc[df["Date"] == date, "Name"]}
    missing = [n for n in students.names() if _key(n) not in recorded]
    if missing:
        rows = pd.DataFrame([[date, n, ABSENT, ""] for n in missing], columns=COLUMNS)
        _save(pd.concat([df, rows], ignore_index=True))


def mark_present(name: str) -> tuple[str, bool]:
    """Record `name` as present today.

    Returns the recorded time and whether this call marked it (False if already present).
    """
    df = load()
    date, now = today(), datetime.now().strftime("%H:%M:%S")
    mask = (df["Date"] == date) & (df["Name"].map(_key) == _key(name))
    if mask.any():
        already = df.loc[mask & (df["Status"] == PRESENT), "Time"]
        if not already.empty:
            return already.iloc[0], False
        df.loc[mask, ["Status", "Time"]] = [PRESENT, now]
    else:
        df = pd.concat([df, pd.DataFrame([[date, name, PRESENT, now]], columns=COLUMNS)],
                       ignore_index=True)
    _save(df)
    return now, True


def dates() -> list[str]:
    return sorted(load()["Date"].unique(), reverse=True)


def for_date(date: str) -> pd.DataFrame:
    df = load()
    return df[df["Date"] == date].sort_values("Name").reset_index(drop=True)
