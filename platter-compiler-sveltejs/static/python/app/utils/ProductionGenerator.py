"""
Generate parser production functions from a TSV file.

- Input:  TSV like new_prods.tsv (columns: prod_no, <lhs>, =>, rhs1, rhs2, ...)
- Output: A .py file containing one function per unique <lhs> production

It intentionally does NOT try to "fix" or validate the produced code; it just emits
code in the requested format.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import keyword
import re
from typing import List, Dict, Tuple

# hehe

# =========================
# Config (edit these)
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[4]

TSV_REL_PATH = PROJECT_ROOT / "static/python/app/utils/sources"
TSV_NAME = "new_prods.tsv"

OUTPUT_DIR_REL = PROJECT_ROOT / "static/python/app/utils/sources"
OUTPUT_FILENAME = "productions.py"
# =========================


ANGLE_RE = re.compile(r"^<(.+)>$")


@dataclass(frozen=True)
class ProductionAlt:
    prod_no: str
    lhs: str               # e.g. "<strict_piece_factor>"
    rhs: List[str]         # e.g. ["(", "<strict_piece_expr>", ")"]


def _strip_angle(sym: str) -> str:
    m = ANGLE_RE.match(sym.strip())
    return m.group(1) if m else sym.strip()


def _is_nonterminal(sym: str) -> bool:
    sym = sym.strip()
    return sym.startswith("<") and sym.endswith(">")


def _safe_func_name(nonterminal: str) -> str:
    """
    Convert a nonterminal like "<id>" -> "id_"/"id" etc.
    Rules:
      - remove < >
      - replace non [A-Za-z0-9_] with _
      - if it starts with digit, prefix _
      - if it is a Python keyword or builtin-ish name, append _
    """
    name = _strip_angle(nonterminal)
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not name:
        name = "_"
    if name[0].isdigit():
        name = "_" + name
    # match your sample behavior for <id> -> id_ (builtin name)
    if keyword.iskeyword(name) or name in dir(__builtins__):
        name = name + "_"
    return name


def _format_prod_doc(prod_no: str, lhs: str, rhs: List[str]) -> str:
    # match the style: """ 16 <lhs>\t=>\t... """
    rhs_part = "\t".join(rhs) if rhs else ""
    return f'"""    {prod_no} {lhs}\t=>\t{rhs_part}    """'


def _parse_tsv(tsv_path: Path) -> List[ProductionAlt]:
    alts: List[ProductionAlt] = []
    for raw in tsv_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            continue

        parts = line.split("\t")
        # drop trailing empty columns
        while parts and parts[-1] == "":
            parts.pop()

        if len(parts) < 3:
            continue

        prod_no = parts[0].strip()
        lhs = parts[1].strip()

        # parts[2] is expected to be "=>", but we won't enforce it
        rhs = [p.strip() for p in parts[3:] if p.strip()]

        alts.append(ProductionAlt(prod_no=prod_no, lhs=lhs, rhs=rhs))
    return alts


def _group_by_lhs(alts: List[ProductionAlt]) -> Tuple[Dict[str, List[ProductionAlt]], List[str]]:
    grouped: Dict[str, List[ProductionAlt]] = {}
    lhs_order: List[str] = []
    seen = set()

    for alt in alts:
        if alt.lhs not in seen:
            seen.add(alt.lhs)
            lhs_order.append(alt.lhs)
        grouped.setdefault(alt.lhs, []).append(alt)

    return grouped, lhs_order



def _emit_rhs_actions(rhs: List[str], indent: str = " " * 8) -> str:
    """
    Emit the body actions for a RHS:
      - nonterminal: self.<func>()
      - terminal:    self.parse_token("<terminal>")
      - empty RHS:   pass
    """
    if not rhs:
        return indent + "pass"

    lines: List[str] = []
    for sym in rhs:
        if _is_nonterminal(sym):
            lines.append(f"{indent}self.{_safe_func_name(sym)}()")
        else:
            # terminal
            lines.append(f'{indent}self.parse_token("{sym}")')
    return "\n".join(lines)


def _emit_function(lhs: str, alts: List[ProductionAlt]) -> str:
    func_name = _safe_func_name(lhs)

    out: List[str] = []
    out.append(f"def {func_name}(self):")
    out.append('    log.info("Enter: " + self.tokens[self.pos].type) # J')
    out.append("")

    if len(alts) == 1:
        alt = alts[0]
        out.append(f"    {_format_prod_doc(alt.prod_no, alt.lhs, alt.rhs)}")
        out.append(f'    if self.tokens[self.pos].type in PREDICT_SET["{lhs}"]:')
        out.append(_emit_rhs_actions(alt.rhs, indent=" " * 8))
        out.append(f'    else: self.parse_token(PREDICT_SET_M["{lhs}"])')
    else:
        # first alternative uses base key: PREDICT_SET["<lhs>"]
        first = alts[0]
        out.append(f"    {_format_prod_doc(first.prod_no, first.lhs, first.rhs)}")
        out.append(f'    if self.tokens[self.pos].type in PREDICT_SET["{lhs}"]:')
        out.append(_emit_rhs_actions(first.rhs, indent=" " * 8))
        out.append("")

        # remaining alternatives use suffixed keys: <lhs>_1, <lhs>_2, ...
        for i, alt in enumerate(alts[1:], start=1):
            out.append(f"        {_format_prod_doc(alt.prod_no, alt.lhs, alt.rhs)}")
            out.append(f'    elif self.tokens[self.pos].type in PREDICT_SET["{lhs}_{i}"]:')
            out.append(_emit_rhs_actions(alt.rhs, indent=" " * 8))
            out.append("")

        out.append(f'    else: self.parse_token(PREDICT_SET_M["{lhs}"])')

    out.append("")
    out.append('    log.info("Exit: " + self.tokens[self.pos].type) # J')
    out.append("")  # trailing newline
    return "\n".join(out)


def generate() -> Path:
    tsv_path = (TSV_REL_PATH / TSV_NAME).resolve()
    out_dir = OUTPUT_DIR_REL.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUTPUT_FILENAME

    alts = _parse_tsv(tsv_path)

    # CHANGED: group_by_lhs now returns (grouped, lhs_order)
    grouped, lhs_order = _group_by_lhs(alts)

    # Stable ordering: by production number (as int if possible)
    def _prod_sort_key(a: ProductionAlt) -> Tuple[int, str]:
        try:
            return (int(a.prod_no), a.prod_no)
        except ValueError:
            return (10**9, a.prod_no)

    chunks: List[str] = []

    # CHANGED: use TSV LHS order, not sorted()
    for lhs in lhs_order:
        group_alts = sorted(grouped[lhs], key=_prod_sort_key)
        chunks.append(_emit_function(lhs, group_alts))

    out_path.write_text("\n".join(chunks), encoding="utf-8")
    return out_path
def generate() -> Path:
    tsv_path = (TSV_REL_PATH / TSV_NAME).resolve()
    out_dir = OUTPUT_DIR_REL.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / OUTPUT_FILENAME

    alts = _parse_tsv(tsv_path)

    # CHANGED: group_by_lhs now returns (grouped, lhs_order)
    grouped, lhs_order = _group_by_lhs(alts)

    # Stable ordering: by production number (as int if possible)
    def _prod_sort_key(a: ProductionAlt) -> Tuple[int, str]:
        try:
            return (int(a.prod_no), a.prod_no)
        except ValueError:
            return (10**9, a.prod_no)

    chunks: List[str] = []

    # CHANGED: use TSV LHS order, not sorted()
    for lhs in lhs_order:
        group_alts = sorted(grouped[lhs], key=_prod_sort_key)
        chunks.append(_emit_function(lhs, group_alts))

    out_path.write_text("\n".join(chunks), encoding="utf-8")
    return out_path



if __name__ == "__main__":
    path = generate()
    print(f"Wrote: {path}")
