"""
Generate a Python test script list from a CSV.

CSV format requirements:
- Column A: Number
- Column B: Code
- Column C: Expected Output
- Column D: Actual Output
- Column E: Test Result

The CSV should have headers. This script will locate the CSV in a folder (traverse),
then generate a Python file containing:

SYNTAX_TSCRIPTS = [
  {
    "number": ...,
    "actual_output": "...",
    "expected_output": "...",
    "code":

  },
  ...
]
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# =========================
# CONFIG (edit these)
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[4]
ROOT_DIR = PROJECT_ROOT / "static/python/app/utils/sources"

ROOT_FOLDER: str = "."                  # Folder to traverse
CSV_FILENAME: str = "testscript.csv"  # Target CSV name to find
OUTPUT_FOLDER: Optional[str] = PROJECT_ROOT / "static/python/app/utils/sources"     # None => write into the folder containing the CSV
OUTPUT_FILENAME: str = "testscript.py"  # Output .py file name
LIST_VARIABLE_NAME: str = "SYNTAX_TSCRIPTS"  # Name of the python list variable


# CSV column meanings by header name or by position fallback.
# If you want strict header matching, keep these as-is.
HEADER_NUMBER = "Number"
HEADER_CODE = "Test Case/Test Scenario"
HEADER_EXPECTED = "Expected Output"
HEADER_ACTUAL = "Actual Output"
HEADER_RESULT = "Test Result"


# =========================
# Implementation
# =========================

def find_file_by_name(root: Path, filename: str) -> Optional[Path]:
    """Traverse root and return the first matching file path."""
    for dirpath, _, files in os.walk(root):
        if filename in files:
            return Path(dirpath) / filename
    return None


def normalize_newlines(text: str) -> str:
    """Normalize Windows/Mac line endings to Unix LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def escape_triple_quotes(text: str) -> str:
    """
    If code contains triple quotes, escape them so our output file stays valid.
    This is rare, but makes the exporter robust.
    """
    return text.replace('"""', r'\"\"\"')


def read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    """
    Read CSV with headers. Returns list of dict rows.
    Raises ValueError if required headers are missing.
    """
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no headers.")

        fieldnames = set(reader.fieldnames)

        required = {HEADER_NUMBER, HEADER_CODE, HEADER_EXPECTED, HEADER_ACTUAL, HEADER_RESULT}
        missing = [h for h in required if h not in fieldnames]
        if missing:
            raise ValueError(
                "CSV is missing required headers: "
                + ", ".join(missing)
                + f"\nFound headers: {reader.fieldnames}"
            )

        return list(reader)


def format_entry(number: int, actual: str, expected: str, code: str) -> str:
    """
    Format one test entry exactly like the user’s template.
    """
    # Normalize and protect output file formatting
    actual = normalize_newlines(actual).strip("\n")
    expected = normalize_newlines(expected).strip("\n")
    code = normalize_newlines(code).rstrip()  # preserve internal newlines, remove trailing whitespace

    # Escape triple-quotes if they ever appear inside code
    code = escape_triple_quotes(code)

    # Escape backslashes/quotes for the single-line strings
    # We'll use repr() but force double quotes style visually by replacing outer quotes if needed.
    # (repr is safest; your outputs are normal strings.)
    actual_repr = repr(actual)
    expected_repr = repr(expected)

    # Ensure those use double quotes in appearance (optional aesthetic)
    if actual_repr.startswith("'") and actual_repr.endswith("'"):
        actual_repr = '"' + actual_repr[1:-1].replace('"', r"\"") + '"'
    if expected_repr.startswith("'") and expected_repr.endswith("'"):
        expected_repr = '"' + expected_repr[1:-1].replace('"', r"\"") + '"'

    
    if (number == 9): print(f"{code}")
    return (
        "  {\n" +
        f'    "number": {number},\n'+
        f'    "actual_output": {actual_repr},\n'+
        f'    "expected_output": {expected_repr},\n'+
        '    "code":  \n'+
        f"    \"\"\"{code}\"\"\""+
        "  }"
    )


def build_python_file(rows: List[Dict[str, str]], variable_name: str) -> str:
    entries: List[str] = []

    for row in rows:
        # Robust int parsing
        raw_num = (row.get(HEADER_NUMBER) or "").strip()
        if not raw_num:
            # Skip empty number rows
            continue
        try:
            number = int(raw_num)
        except ValueError:
            # If it's not int, keep it as-is? But your spec expects number.
            raise ValueError(f"Invalid Number value: {raw_num!r}")

        code = row.get(HEADER_CODE, "")
        expected = row.get(HEADER_EXPECTED, "")
        actual = row.get(HEADER_ACTUAL, "")

        entries.append(format_entry(number, actual, expected, code))

    content = (
        "# Auto-generated from CSV. Do not edit manually.\n"
        f"{variable_name} = [\n"
        + ",\n".join(entries)
        + "\n]\n"
    )
    return content


def main() -> int:
    root = Path(ROOT_FOLDER).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"ROOT_FOLDER does not exist: {root}")

    csv_path = find_file_by_name(root, CSV_FILENAME)
    if not csv_path:
        raise FileNotFoundError(f"Could not find {CSV_FILENAME!r} under {root}")

    rows = read_csv_rows(csv_path)

    output_dir = Path(OUTPUT_FOLDER).expanduser().resolve() if OUTPUT_FOLDER else csv_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    out_path = output_dir / OUTPUT_FILENAME
    py_content = build_python_file(rows, LIST_VARIABLE_NAME)

    out_path.write_text(py_content, encoding="utf-8")

    print(f"Found CSV: {csv_path}")
    print(f"Wrote Python file: {out_path}")
    print(f"Entries written: {sum(1 for r in rows if (r.get(HEADER_NUMBER) or '').strip())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
