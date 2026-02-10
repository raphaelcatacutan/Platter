"""
Predict Set Generator

Reads a TSV where:
- Column A: non-terminals (dict keys), e.g. <program>
- Column B: predict set text, e.g. { piece, sip, flag, chars }

Parsing rules implemented:
- Outer { } defines the set.
- Inner '{' or '}' inside the set are treated as literal elements.
- Comma ',' is normally a separator, BUT if it appears where an element is expected
  (e.g., "{ , ,, ) }"), then ',' is treated as an element.
- When merging: same non-terminal keys merged, no duplicates, preserve insertion order (unsorted).
- When NOT merging: repeated non-terminals get suffix _1, _2, ...
- Output dict is ordered with <program> first if present, then in discovery order.
"""

from __future__ import annotations

import csv
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

# =========================
# CONFIG (edit these)
# =========================

# ---- Bulletproof project-root anchoring (ignores `cd`) ----
# This file is expected to live at:
#   <project_root>/static/python/app/utils/PredictSetTransformer.py
# So:
#   parents[0] = .../app/utils
#   parents[1] = .../app
#   parents[2] = .../python
#   parents[3] = .../static
#   parents[4] = <project_root>
PROJECT_ROOT = Path(__file__).resolve().parents[4]

# Where to search for the TSV
SEARCH_ROOT = PROJECT_ROOT / "static/python/app/utils/sources"   # <--- your TSV folder
TSV_NAME = "predict_set.tsv"

# Merge behavior
MERGE_NONTERMINALS = False  # True => merge duplicates, False => suffix _1, _2, ...

# Output
# PREDICT_SET_HEADER = "PREDICT_SET_M" if MERGE_NONTERMINALS else "PREDICT_SET"
# OUTPUT_PY_NAME = "predict_set_m.py" if MERGE_NONTERMINALS else "predict_set.py"
OUTPUT_PY_PATH = PROJECT_ROOT / "static/python/app/parser"       # <--- your parser folder

HAS_HEADER = False
ENCODING = "utf-8-sig"

# =========================


MULTI_CHAR_TOKENS = {
    "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "%=",
    "&&", "||", "::",
}

SINGLE_CHAR_TOKENS = set("{}()[];:+-*/%<>=!:")


@dataclass
class RowItem:
    key: str
    raw_set: str


def find_tsv(root: Path, filename: str) -> Path:
    """Traverse root recursively and return the first matching TSV path."""
    for p in root.rglob(filename):
        if p.is_file():
            return p
    raise FileNotFoundError(f"Could not find '{filename}' under '{root.resolve()}'.")


def read_tsv_rows(tsv_path: Path, has_header: bool) -> List[RowItem]:
    rows: List[RowItem] = []
    with tsv_path.open("r", encoding=ENCODING, newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        if has_header:
            next(reader, None)

        for cols in reader:
            if not cols or len(cols) < 2:
                continue

            key = (cols[0] or "").strip()
            raw_set = (cols[1] or "").strip() or "{}"

            if not key:
                continue

            rows.append(RowItem(key=key, raw_set=raw_set))

    return rows


def extract_outer_set_text(s: str) -> str:
    first = s.find("{")
    last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        return s[first + 1:last]
    return s.strip()


def parse_set_elements(raw_set: str) -> List[str]:
    inner = extract_outer_set_text(raw_set)
    elements: List[str] = []

    i = 0
    n = len(inner)
    expecting_element = True

    def skip_ws(j: int) -> int:
        while j < n and inner[j].isspace():
            j += 1
        return j

    i = skip_ws(i)
    while i < n:
        ch = inner[i]

        # Comma handling (separator vs literal element)
        if ch == ",":
            if expecting_element:
                elements.append(",")
            expecting_element = True
            i = skip_ws(i + 1)
            continue

        # Inner braces as literal elements
        if ch in "{}":
            elements.append(ch)
            expecting_element = False
            i = skip_ws(i + 1)
            continue

        # Multi-char operators
        if i + 1 < n:
            two = inner[i:i + 2]
            if two in MULTI_CHAR_TOKENS:
                elements.append(two)
                expecting_element = False
                i = skip_ws(i + 2)
                continue

        # Single-char tokens
        if ch in SINGLE_CHAR_TOKENS:
            elements.append(ch)
            expecting_element = False
            i = skip_ws(i + 1)
            continue

        # Read token until whitespace or delimiter
        j = i
        while j < n:
            c = inner[j]
            if c.isspace() or c == "," or c in "{}":
                break
            j += 1

        token = inner[i:j].strip()
        if token:
            elements.append(token)
            expecting_element = False

        i = skip_ws(j)

    return elements


def merge_preserve_order(existing: List[str], new_items: List[str]) -> List[str]:
    seen = set(existing)
    for item in new_items:
        if item not in seen:
            existing.append(item)
            seen.add(item)
    return existing


def build_predict_set(rows: List[RowItem], merge_nonterminals: bool) -> "OrderedDict[str, List[str]]":
    out: "OrderedDict[str, List[str]]" = OrderedDict()
    dup_counter: Dict[str, int] = {}

    for r in rows:
        key = r.key
        elems = parse_set_elements(r.raw_set)

        if merge_nonterminals:
            if key not in out:
                out[key] = []
            out[key] = merge_preserve_order(out[key], elems)
        else:
            if key not in dup_counter:
                dup_counter[key] = 0
                out[key] = elems
            else:
                dup_counter[key] += 1
                out[f"{key}_{dup_counter[key]}"] = elems

    # Reorder to start at <program> if it exists
    if "<program>" in out:
        reordered: "OrderedDict[str, List[str]]" = OrderedDict()
        reordered["<program>"] = out["<program>"]
        for k, v in out.items():
            if k != "<program>":
                reordered[k] = v
        out = reordered

    return out


def format_py_dict(d: "OrderedDict[str, List[str]]") -> str:    
    PREDICT_SET_HEADER = "PREDICT_SET_M" if MERGE_NONTERMINALS else "FIRST_SET"
    lines: List[str] = []
    lines.append("# Auto-generated by predict set generator. Do not edit by hand.\n")
    lines.append(f"{PREDICT_SET_HEADER} = {{\n")
    for k, v in d.items():
        items = ", ".join(repr(x) for x in v)
        lines.append(f"    {repr(k)}: [{items}],\n")
    lines.append("}\n")
    return "".join(lines)


def write_predict_set_py(tsv_path: Path, predict_set: "OrderedDict[str, List[str]]") -> Path:
    # OUTPUT_PY_PATH is now absolute (anchored to PROJECT_ROOT),
    # but this also supports relative paths safely if you change it later.
    if OUTPUT_PY_PATH:
        OUTPUT_PY_NAME = "predict_set_m.py" if MERGE_NONTERMINALS else "first_set.py"
        out_dir = Path(OUTPUT_PY_PATH).expanduser()
        if not out_dir.is_absolute():
            out_dir = (PROJECT_ROOT / out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / OUTPUT_PY_NAME
    else:
        out_path = tsv_path.parent / OUTPUT_PY_NAME

    out_path.write_text(format_py_dict(predict_set), encoding="utf-8")
    return out_path


def main() -> None:
    # Allow: python -m ... m
    global MERGE_NONTERMINALS
    if len(sys.argv) > 1 and sys.argv[1].lower() in {"m", "merged"}:
        MERGE_NONTERMINALS = True
    else:
        MERGE_NONTERMINALS = False
        

    root = Path(SEARCH_ROOT)
    if not root.exists():
        raise RuntimeError(f"[ERROR] SEARCH_ROOT does not exist: {root}\n[DEBUG] PROJECT_ROOT: {PROJECT_ROOT}")

    tsv_path = find_tsv(root, TSV_NAME)

    rows = read_tsv_rows(tsv_path, HAS_HEADER)
    if not rows:
        raise RuntimeError(f"No usable rows found in TSV: {tsv_path}")

    predict_set = build_predict_set(rows, MERGE_NONTERMINALS)
    out_path = write_predict_set_py(tsv_path, predict_set)

    print(f"Found TSV: {tsv_path}")
    print(f"MERGE_NONTERMINALS={MERGE_NONTERMINALS}")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
