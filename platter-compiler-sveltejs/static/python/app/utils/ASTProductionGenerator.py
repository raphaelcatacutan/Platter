"""
Generate AST-building parser production functions from CFG and AST action TSV files.

- Input:  cfg.tsv (grammar) + ast.tsv (AST actions)
- Output: ast_parser_program.py with AST-building parser functions
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import keyword
import re
from typing import List, Dict, Tuple, Optional

# =========================
# Config
# =========================
PROJECT_ROOT = Path(__file__).resolve().parents[4]

SOURCES_DIR = PROJECT_ROOT / "static/python/app/utils/sources"
CFG_TSV = SOURCES_DIR / "cfg.tsv"
AST_TSV = SOURCES_DIR / "ast.tsv"

OUTPUT_DIR = PROJECT_ROOT / "static/python/app/semantic_analyzer/ast"
OUTPUT_FILE = OUTPUT_DIR / "ast_parser_program.py"
# =========================


ANGLE_RE = re.compile(r"^<(.+)>$")


@dataclass(frozen=True)
class ProductionAlt:
    prod_no: str
    lhs: str
    rhs: List[str]


@dataclass(frozen=True)
class ASTAction:
    prod_no: str
    lhs: str
    action_type: str  # create, propagate, skip, collect, build_binop, build_access, etc.
    ast_class: str
    field_mapping: str
    note: str


def _strip_angle(sym: str) -> str:
    m = ANGLE_RE.match(sym.strip())
    return m.group(1) if m else sym.strip()


def _is_nonterminal(sym: str) -> bool:
    sym = sym.strip()
    return sym.startswith("<") and sym.endswith(">")


def _safe_func_name(nonterminal: str) -> str:
    """Convert nonterminal to safe function name"""
    name = _strip_angle(nonterminal)
    name = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not name:
        name = "_"
    if name[0].isdigit():
        name = "_" + name
    if keyword.iskeyword(name) or name in dir(__builtins__):
        name = name + "_"
    return name


def _format_prod_doc(prod_no: str, lhs: str, rhs: List[str]) -> str:
    rhs_part = "\t".join(rhs) if rhs else ""
    return f'"""    {prod_no} {lhs}\t=>\t{rhs_part}    """'


def _parse_cfg_tsv(tsv_path: Path) -> List[ProductionAlt]:
    """Parse the CFG TSV file"""
    alts: List[ProductionAlt] = []
    for raw in tsv_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            continue

        parts = line.split("\t")
        while parts and parts[-1] == "":
            parts.pop()

        if len(parts) < 3:
            continue

        prod_no = parts[0].strip()
        lhs = parts[1].strip()
        rhs = [p.strip() for p in parts[3:] if p.strip()]

        if len(rhs) == 1 and rhs[0] == "λ":
            rhs = []
            
        alts.append(ProductionAlt(prod_no=prod_no, lhs=lhs, rhs=rhs))
    return alts


def _parse_ast_tsv(tsv_path: Path) -> Dict[str, ASTAction]:
    """Parse the AST actions TSV file, keyed by prod_no"""
    actions: Dict[str, ASTAction] = {}
    
    for raw in tsv_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip("\n")
        if not line.strip() or line.startswith("prod_no"):  # Skip header
            continue

        parts = line.split("\t")
        if len(parts) < 6:
            continue

        prod_no = parts[0].strip()
        lhs = parts[1].strip()
        action_type = parts[3].strip()
        ast_class = parts[4].strip()
        field_mapping = parts[5].strip()
        note = parts[6].strip() if len(parts) > 6 else ""

        actions[prod_no] = ASTAction(
            prod_no=prod_no,
            lhs=lhs,
            action_type=action_type,
            ast_class=ast_class,
            field_mapping=field_mapping,
            note=note
        )
    
    return actions


def _group_by_lhs(alts: List[ProductionAlt]) -> Tuple[Dict[str, List[ProductionAlt]], List[str]]:
    """Group productions by LHS"""
    grouped: Dict[str, List[ProductionAlt]] = {}
    lhs_order: List[str] = []
    seen = set()

    for alt in alts:
        if alt.lhs not in seen:
            seen.add(alt.lhs)
            lhs_order.append(alt.lhs)
        grouped.setdefault(alt.lhs, []).append(alt)

    return grouped, lhs_order


def _emit_ast_action(action: ASTAction, rhs: List[str], indent: str = " " * 8) -> str:
    """Generate code for an AST action"""
    lines: List[str] = []
    
    if action.action_type == "skip":
        lines.append(f"{indent}return None")
    
    elif action.action_type == "propagate":
        # Return the specified child node
        ref = action.field_mapping.strip()
        if ref.startswith("$"):
            idx = int(ref[1:])
            lines.append(f"{indent}return node_{idx}")
        else:
            lines.append(f"{indent}return None")
    
    elif action.action_type == "create":
        # Create a new AST node
        lines.append(f"{indent}# Create {action.ast_class} node")
        
        # Parse field_mapping to extract constructor args
        # Simple implementation: just pass the mapping as comment for now
        # Real implementation would parse and substitute $0, $1, etc.
        lines.append(f"{indent}# TODO: {action.field_mapping}")
        lines.append(f"{indent}node = {action.ast_class}()")
        lines.append(f"{indent}return node")
    
    elif action.action_type == "collect":
        # Collect/aggregate nodes into a list
        lines.append(f"{indent}# Collect nodes: {action.field_mapping}")
        lines.append(f"{indent}result = []")
        lines.append(f"{indent}# TODO: Implement collection logic")
        lines.append(f"{indent}return result")
    
    elif action.action_type == "build_binop":
        # Build binary operation from left, operator, right
        lines.append(f"{indent}# Build binary operation")
        lines.append(f"{indent}# TODO: Implement binop building")
        lines.append(f"{indent}return node_0")
    
    elif action.action_type == "build_access":
        # Build array/table access
        lines.append(f"{indent}# Build accessor")
        lines.append(f"{indent}# TODO: Implement accessor building")
        lines.append(f"{indent}return node_0")
    
    elif action.action_type == "token":
        # Return token value
        lines.append(f"{indent}return self.tokens[self.pos - 1].value")
    
    else:
        # Unknown action type - just return None
        lines.append(f"{indent}# Unknown action: {action.action_type}")
        lines.append(f"{indent}return None")
    
    return "\n".join(lines)


def _emit_rhs_parse_and_action(rhs: List[str], action: Optional[ASTAction], indent: str = " " * 8) -> str:
    """Emit parsing code and AST action for a RHS"""
    lines: List[str] = []
    
    if not rhs:
        # Empty production
        if action:
            lines.append(_emit_ast_action(action, rhs, indent))
        else:
            lines.append(f"{indent}return None")
        return "\n".join(lines)
    
    # Parse all symbols in RHS
    for i, sym in enumerate(rhs):
        if _is_nonterminal(sym):
            lines.append(f"{indent}node_{i} = self.{_safe_func_name(sym)}()")
        else:
            lines.append(f'{indent}self.parse_token("{sym}")')
    
    # Apply AST action
    lines.append("")
    if action:
        lines.append(_emit_ast_action(action, rhs, indent))
    else:
        # No action specified - return None
        lines.append(f"{indent}return None")
    
    return "\n".join(lines)


def _emit_function(lhs: str, alts: List[ProductionAlt], actions: Dict[str, ASTAction]) -> str:
    """Generate a parser function with AST building"""
    func_name = _safe_func_name(lhs)

    out: List[str] = []
    out.append(f"def {func_name}(self):")
    out.append(f'    self.appendF(FIRST_SET["<{func_name}>"])')
    out.append('    log.info("Enter: " + self.tokens[self.pos].type)')
    out.append('    log.info("STACK: " + str(self.error_arr))')
    out.append("")

    if len(alts) == 1:
        alt = alts[0]
        action = actions.get(alt.prod_no)
        
        out.append(f"    {_format_prod_doc(alt.prod_no, alt.lhs, alt.rhs)}")
        out.append(f'    if self.tokens[self.pos].type in PREDICT_SET["{lhs}"]:')
        out.append(_emit_rhs_parse_and_action(alt.rhs, action, indent=" " * 8))
        out.append(f'    else: self.parse_token(self.error_arr)')
    else:
        # Multiple alternatives
        first = alts[0]
        first_action = actions.get(first.prod_no)
        
        out.append(f"    {_format_prod_doc(first.prod_no, first.lhs, first.rhs)}")
        out.append(f'    if self.tokens[self.pos].type in PREDICT_SET["{lhs}"]:')
        out.append(_emit_rhs_parse_and_action(first.rhs, first_action, indent=" " * 8))
        out.append("")

        # Remaining alternatives
        for i, alt in enumerate(alts[1:], start=1):
            alt_action = actions.get(alt.prod_no)
            
            out.append(f"        {_format_prod_doc(alt.prod_no, alt.lhs, alt.rhs)}")
            out.append(f'    elif self.tokens[self.pos].type in PREDICT_SET["{lhs}_{i}"]:')
            out.append(_emit_rhs_parse_and_action(alt.rhs, alt_action, indent=" " * 8))
            out.append("")

        # Else clause only if last alternative has non-empty RHS
        if alts[-1].rhs:
           out.append(f'    else: self.parse_token(self.error_arr)')
    
    out.append("")
    out.append('    log.info("Exit: " + self.tokens[self.pos].type)')
    out.append("")
    return "\n".join(out)


def generate() -> Path:
    """Generate AST parser program"""
    print(f"Reading CFG from: {CFG_TSV}")
    print(f"Reading AST actions from: {AST_TSV}")
    
    cfg_alts = _parse_cfg_tsv(CFG_TSV)
    ast_actions = _parse_ast_tsv(AST_TSV)
    
    print(f"Loaded {len(cfg_alts)} productions")
    print(f"Loaded {len(ast_actions)} AST actions")
    
    grouped, lhs_order = _group_by_lhs(cfg_alts)
    
    # Sort alternatives by production number
    def _prod_sort_key(a: ProductionAlt) -> Tuple[int, str]:
        try:
            return (int(a.prod_no), a.prod_no)
        except ValueError:
            return (10**9, a.prod_no)
    
    # Generate header
    header = '''"""
Auto-generated AST-building parser. Do not edit by hand.
Generated from cfg.tsv and ast.tsv
"""

from app.lexer.token import Token
from app.parser.error_handler import ErrorHandler
from app.parser.predict_set import PREDICT_SET
from app.parser.first_set import FIRST_SET
from app.semantic_analyzer.ast.ast_nodes import *
import logging as log

log.basicConfig(level=log.DEBUG, format='%(levelname)s: <%(funcName)s> | %(message)s')


class ASTParser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")]
        self.error_arr = []
        if not self.tokens:
            raise ErrorHandler("EOF", None, PREDICT_SET["<program>"])
        
        last_token = self.tokens[-1]
        self.tokens.append(Token("EOF", "EOF", last_token.line, last_token.col))
        
        self.pos = 0
    
    def parse_token(self, tok):
        """Parse and consume a specific token type"""
        if self.pos >= len(self.tokens):
            raise ErrorHandler("EOF", None, tok)
        
        if self.tokens[self.pos].type == tok:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: MATCH!")
            self.pos += 1
            self.error_arr.clear()
        else:
            log.warning(f"Expected: {tok} | Current: {self.tokens[self.pos].type} | Remark: INVALID!\\n")
            
            if tok != self.error_arr:
                if isinstance(tok, list):
                    self.error_arr.extend([t for t in tok if t not in self.error_arr])
                else:
                    if tok not in self.error_arr:
                        self.error_arr.append(tok)
            
            log.info("STACK: " + str(self.error_arr) + "\\n")
            self.error_arr = list(dict.fromkeys(self.error_arr))
            raise ErrorHandler("Unexpected_err", self.tokens[self.pos], self.error_arr)
    
    def appendF(self, first_set):
        first_set = [t for t in first_set if not (t=="λ")]
        self.error_arr.extend(first_set)
    
    def parse_program(self):
        """Entry point for parsing"""
        self.appendF(FIRST_SET["<program>"])
        log.info("Enter: " + self.tokens[self.pos].type)
        log.info("STACK: " + str(self.error_arr))

        """    1 <program>	=>	<global_decl>	<recipe_decl>	start	(	)	<platter>    """
        if self.tokens[self.pos].type in PREDICT_SET["<program>"]:
            node_0 = self.global_decl()
            node_1 = self.recipe_decl()
            self.parse_token("start")
            self.parse_token("(")
            self.parse_token(")")
            node_7 = self.platter()
            
            # Create Program node
            prog = Program()
            if isinstance(node_0, list):
                for decl in node_0:
                    prog.add_global_decl(decl)
            if isinstance(node_1, list):
                for recipe in node_1:
                    prog.add_recipe_decl(recipe)
            prog.set_start_platter(node_7)
            
            # Ensure we've consumed all tokens
            if self.pos < len(self.tokens) and self.tokens[self.pos].type != "EOF":
                raise ErrorHandler("ExpectedEOF_err", self.tokens[self.pos], None)
            
            log.info("Exit: " + self.tokens[self.pos].type)
            return prog
        else:
            self.parse_token(self.error_arr)

'''
    
    chunks: List[str] = [header]
    
    # Generate functions (skip program since it's in header)
    for lhs in lhs_order:
        if lhs == "<program>":
            continue
        
        group_alts = sorted(grouped[lhs], key=_prod_sort_key)
        chunks.append(_emit_function(lhs, group_alts, ast_actions))
    
    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(chunks), encoding="utf-8")
    
    print(f"✓ Generated: {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    path = generate()
    print(f"Wrote: {path}")
