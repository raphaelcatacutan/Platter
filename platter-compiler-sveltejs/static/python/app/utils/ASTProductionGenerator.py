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


def _substitute_field_value(value: str, rhs: List[str]) -> str:
    """
    Substitute field values in AST action expressions.
    - $0, $1, etc. -> node_0, node_1, etc. (for nonterminals) or token_0, token_1 (for terminals)
    - $0.value -> token_0.value (for terminals)
    - $0_fieldname -> node_0.fieldname (attribute access)
    - CONTEXT -> (needs context from caller)
    - Complex expressions like Literal("piece",$0.value) are processed recursively
    - String literals remain as-is
    """
    value = value.strip()
    
    # Check if this is a complex expression with $N substitutions inside
    # Pattern: Look for $N or $N.value or $N_field anywhere in the string
    if '$' in value or 'CONTEXT' in value:
        # Process all substitutions in the expression
        result = value
        
        # Substitute $N_fieldname patterns first (more specific)
        for match in re.finditer(r'\$(\d+)_(\w+)', result):
            idx = int(match.group(1))
            field = match.group(2)
            if idx < len(rhs):
                prefix = "node" if _is_nonterminal(rhs[idx]) else "token"
                result = result.replace(match.group(0), f"{prefix}_{idx}.{field}")
        
        # Substitute $N.value patterns
        for match in re.finditer(r'\$(\d+)\.value', result):
            idx = int(match.group(1))
            if idx < len(rhs):
                if _is_nonterminal(rhs[idx]):
                    result = result.replace(match.group(0), f"node_{idx}.value")
                else:
                    result = result.replace(match.group(0), f"token_{idx}.value")
        
        # Substitute $N patterns (simple references)
        for match in re.finditer(r'\$(\d+)(?![\._])', result):
            idx = int(match.group(1))
            if idx < len(rhs):
                prefix = "node" if _is_nonterminal(rhs[idx]) else "token"
                result = result.replace(match.group(0), f"{prefix}_{idx}")
        
        # Substitute CONTEXT keywords
        result = result.replace("CONTEXT_TYPE", "self._context_type")
        result = result.replace("CONTEXT_ID", "self._context_identifier")
        result = result.replace("CONTEXT", "self._context_dimensions")
        
        return result
    
    # Simple value - no substitutions needed
    # Check if it's a numeric literal (don't quote numbers)
    try:
        # Try to parse as int or float
        float(value)
        return value  # Return as-is (unquoted number)
    except ValueError:
        pass
    
    # Check if already quoted
    if value.startswith('"') and value.endswith('"'):
        return value  # Already quoted, return as-is
    
    # String literals - quote them
    if value and not value.startswith(("node_", "token_", "self.", "[", "CONTEXT")):
        return f'"{value}"'
    
    return value


def _substitute_list_expr(expr: str, rhs: List[str]) -> str:
    """
    Substitute list expressions like [$2] or [$2,$4] with proper Python syntax.
    """
    # Handle list expressions like [$2,$4]
    if expr.startswith("[") and expr.endswith("]"):
        inner = expr[1:-1]
        # Split by comma and substitute each element
        parts = inner.split(",")
        substituted = []
        for part in parts:
            part = part.strip()
            if part:
                substituted.append(_substitute_field_value(part, rhs))
        return "[" + ", ".join(substituted) + "]"
    return expr


def _parse_field_mapping(field_mapping: str, rhs: List[str]) -> Dict[str, str]:
    """
    Parse field_mapping like 'field1=value1 field2=$0 field3=$1.value args=[$2,$4]'
    Returns dict of field_name -> substituted_value
    """
    result = {}
    
    # Handle complex expressions with brackets
    # Split carefully to preserve [...] expressions
    i = 0
    while i < len(field_mapping):
        # Find next key=value pair
        eq_pos = field_mapping.find('=', i)
        if eq_pos == -1:
            break
        
        # Find key (go back to find start of key)
        key_start = eq_pos - 1
        while key_start > i and field_mapping[key_start] not in ' \t':
            key_start -= 1
        if field_mapping[key_start] in ' \t':
            key_start += 1
        key = field_mapping[key_start:eq_pos].strip()
        
        # Find value (could have brackets)
        value_start = eq_pos + 1
        if value_start < len(field_mapping) and field_mapping[value_start] == '[':
            # Find matching ]
            bracket_count = 1
            value_end = value_start + 1
            while value_end < len(field_mapping) and bracket_count > 0:
                if field_mapping[value_end] == '[':
                    bracket_count += 1
                elif field_mapping[value_end] == ']':
                    bracket_count -= 1
                value_end += 1
            value = field_mapping[value_start:value_end].strip()
            i = value_end
        else:
            # Find end of value (next space or end of string)
            value_end = value_start
            while value_end < len(field_mapping) and field_mapping[value_end] not in ' \t':
                value_end += 1
            value = field_mapping[value_start:value_end].strip()
            i = value_end
        
        # Substitute value
        if value.startswith('[') and value.endswith(']'):
            result[key] = _substitute_list_expr(value, rhs)
        else:
            result[key] = _substitute_field_value(value, rhs)
    
    return result


def _find_first_token(rhs: List[str]) -> Optional[int]:
    """Find the index of the first terminal token in RHS"""
    for i, sym in enumerate(rhs):
        if not _is_nonterminal(sym):
            return i
    return None


def _inject_position_args(expr: str, rhs: List[str]) -> str:
    """
    Inject position arguments into node constructors in an expression.
    Looks for patterns like VarDecl(...), ArrayDecl(...), Literal(...), etc.
    and adds the appropriate token_X.line, token_X.col arguments.
    """
    # Node classes that typically need position info
    node_classes = [
        "VarDecl", "ArrayDecl", "RecipeDecl", "Assignment", "IfStatement",
        "WhileLoop", "ForLoop", "ReturnStatement", "BreakStatement", "ContinueStatement",
        "BinaryOp", "UnaryOp", "FunctionCall", "ArrayAccess", "TableAccess",
        "Literal", "Identifier", "ArrayLiteral", "TableLiteral"
    ]
    
    # Find the first token in the RHS for fallback position
    first_token_idx = _find_first_token(rhs)
    
    result = expr
    
    for node_class in node_classes:
        # Find all occurrences of NodeClass(...)
        pattern = rf'({node_class}\([^)]+\))'
        matches = list(re.finditer(pattern, result))
        
        # Process matches in reverse to maintain string indices
        for match in reversed(matches):
            constructor_call = match.group(1)
            
            # Check if it already has position arguments (look for token_X.line or .line)
            if '.line' in constructor_call:
                continue
            
            # Special case: Identifier with context identifier
            if 'self._context_identifier' in constructor_call and node_class == 'Identifier':
                # Use context position instead of token position
                close_paren_pos = constructor_call.rfind(')')
                new_call = (constructor_call[:close_paren_pos] +
                           ", self._context_identifier_line, self._context_identifier_col" +
                           constructor_call[close_paren_pos:])
                result = result[:match.start()] + new_call + result[match.end():]
                continue
            
            # Find which token to use for position (extract token_N references)
            token_refs = re.findall(r'token_(\d+)', constructor_call)
            if token_refs:
                # Use the first token reference found
                token_idx = token_refs[0]
            elif first_token_idx is not None:
                # No token references in constructor, use first token from RHS
                token_idx = str(first_token_idx)
            else:
                # No tokens available, skip this node
                continue
            
            # Insert position args before the closing paren
            # Find the last closing paren
            close_paren_pos = constructor_call.rfind(')')
            new_call = (constructor_call[:close_paren_pos] +
                       f", token_{token_idx}.line, token_{token_idx}.col" +
                       constructor_call[close_paren_pos:])
            
            # Replace in result
            result = result[:match.start()] + new_call + result[match.end():]
    
    return result


def _emit_ast_action(action: ASTAction, rhs: List[str], indent: str = " " * 8) -> str:
    """Generate code for an AST action"""
    lines: List[str] = []
    
    if action.action_type == "skip":
        lines.append(f"{indent}return None")
    
    elif action.action_type == "propagate":
        # Return the specified child node or create a simple object with attributes
        # Note: context_id setting is handled during parsing, not here
        ref = action.field_mapping.strip()
        
        # Extract the main return value (ignore context_id since it's handled earlier)
        if "context_id=" in ref:
            parts = ref.split()
            ref = parts[0] if parts else "$0"
        
        # Check if this is a simple reference like $0
        if ref.startswith("$") and "=" not in ref:
            idx_match = re.match(r'\$(\d+)', ref)
            if idx_match:
                idx = int(idx_match.group(1))
                # Check if RHS[idx] is a terminal or nonterminal
                if idx < len(rhs):
                    if _is_nonterminal(rhs[idx]):
                        lines.append(f"{indent}return node_{idx}")
                    else:
                        # Terminal: wrap appropriately based on type
                        if rhs[idx] == "id":
                            lines.append(f"{indent}return Identifier(token_{idx}.value, token_{idx}.line, token_{idx}.col)")
                        elif rhs[idx] in ["piece_lit", "sip_lit", "flag_lit", "chars_lit"]:
                            # Wrap literal tokens in Literal nodes
                            lit_type = rhs[idx].replace("_lit", "")  # "piece_lit" -> "piece"
                            lines.append(f"{indent}return Literal('{lit_type}', token_{idx}.value, token_{idx}.line, token_{idx}.col)")
                        else:
                            lines.append(f"{indent}return token_{idx}.value")
                else:
                    lines.append(f"{indent}return None")
            else:
                lines.append(f"{indent}return None")
        # Check if this is an attribute mapping like type="piece" dims=$1
        elif "=" in ref and not any(ref.startswith(prefix) for prefix in ["Identifier(", "TableLiteral(", "ArrayLiteral("]):
            lines.append(f"{indent}# Create simple attribute object")
            fields = _parse_field_mapping(ref, rhs)
            # Use a class with dynamic attributes for cleaner access
            lines.append(f"{indent}class PropagatedAttrs: pass")
            lines.append(f"{indent}result = PropagatedAttrs()")
            for field_name, field_value in fields.items():
                lines.append(f"{indent}result.{field_name} = {field_value}")
            lines.append(f"{indent}return result")
        # Check if this is an expression (like Identifier(CONTEXT_ID) for empty productions)
        elif any(ref.startswith(prefix) for prefix in ["Identifier(", "TableLiteral(", "ArrayLiteral(", "["]):
            lines.append(f"{indent}# Propagate expression")
            expr = ref
            # Substitute CONTEXT keywords (longest first to avoid partial matches)
            expr = expr.replace("CONTEXT_TYPE", "self._context_type")
            # Special handling for Identifier(CONTEXT_ID) - add position info
            if "Identifier(CONTEXT_ID)" in expr:
                expr = expr.replace("Identifier(CONTEXT_ID)", "Identifier(self._context_identifier, self._context_identifier_line, self._context_identifier_col)")
            else:
                expr = expr.replace("CONTEXT_ID", "self._context_identifier")
            expr = expr.replace("CONTEXT", "self._context_dimensions")
            lines.append(f"{indent}return {expr}")
        else:
            lines.append(f"{indent}return None")
    
    elif action.action_type == "create":
        # Create a new AST node with proper constructor args
        lines.append(f"{indent}# Create {action.ast_class} node")
        
        # Parse field_mapping to extract constructor args
        fields = _parse_field_mapping(action.field_mapping, rhs)
        
        # Find first token for position info
        first_token_idx = _find_first_token(rhs)
        pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
        
        # Special handling for Assignment with accessor field
        if action.ast_class == "Assignment" and "accessor" in fields:
            # Assignment(target, operator, value)
            # If accessor exists, apply it to target: target = accessor(target)
            target = fields.get("target", "None")
            accessor = fields.get("accessor", "None")
            operator = fields.get("operator", "None")
            value = fields.get("value", "None")
            
            # Inject position args into target if it's an Identifier
            target = _inject_position_args(target, rhs)
            
            lines.append(f"{indent}target = {target}")
            lines.append(f"{indent}accessor = {accessor}")
            lines.append(f"{indent}if accessor:")
            lines.append(f"{indent}    target = accessor(target)")
            lines.append(f"{indent}node = Assignment(target, {operator}, {value}, {pos_args})")
            lines.append(f"{indent}return node")
        else:
            # Normal node creation
            args = []
            for field_name, field_value in fields.items():
                # Inject position args into any node constructors in field values
                field_value = _inject_position_args(field_value, rhs)
                args.append(field_value)
            
            if args:
                args_str = ", ".join(args)
                lines.append(f"{indent}node = {action.ast_class}({args_str}, {pos_args})")
            else:
                lines.append(f"{indent}node = {action.ast_class}({pos_args})")
            
            lines.append(f"{indent}return node")
    
    elif action.action_type == "collect":
        # Collect/aggregate nodes into a list
        # Parse expressions like: [Literal("piece", $0.value)] + $1
        lines.append(f"{indent}# Collect: {action.field_mapping}")
        
        # Parse and substitute the expression
        expr = action.field_mapping
        
        # Substitute $N_field patterns first (most specific)
        for i in range(len(rhs), -1, -1):
            if i < len(rhs):
                # Find all field references for this index
                for match in re.finditer(rf'\${i}_(\w+)', expr):
                    field = match.group(1)
                    prefix = "node" if _is_nonterminal(rhs[i]) else "token"
                    expr = expr.replace(match.group(0), f"{prefix}_{i}.{field}")
        
        # Substitute $N.value and $N references
        # Process in reverse order to handle $10 before $1
        for i in range(len(rhs), -1, -1):
            # Check if RHS[i] exists and what type it is
            if i < len(rhs):
                if _is_nonterminal(rhs[i]):
                    # Nonterminal: use node_i
                    expr = expr.replace(f"${i}.value", f"node_{i}.value")
                    expr = expr.replace(f"${i}", f"node_{i}")
                else:
                    # Terminal: use token_i
                    expr = expr.replace(f"${i}.value", f"token_{i}.value")
                    expr = expr.replace(f"${i}", f"token_{i}")
        
        # Replace CONTEXT keywords with instance variables (longest first to avoid partial matches)
        expr = expr.replace("CONTEXT_TYPE", "self._context_type")
        expr = expr.replace("CONTEXT_ID", "self._context_identifier")
        expr = expr.replace("CONTEXT", "self._context_dimensions")
        
        # Inject position arguments into node constructors in the expression
        expr = _inject_position_args(expr, rhs)
        
        # Generate the return statement
        lines.append(f"{indent}result = {expr}")
        lines.append(f"{indent}return result")
    
    elif action.action_type == "build_binop":
        # Build binary operation chains (left-associative)
        # Pattern 1: left=$0 right=$1 - combine left with right tail
        # Pattern 2: op=OPERATOR right=$1 tail=$2 - build BinaryOp and continue chain
        fields = _parse_field_mapping(action.field_mapping, rhs)
        
        if "left" in fields and "right" in fields:
            # Pattern: left=$0 right=$1 (combine operand with tail)
            left = fields["left"]
            right = fields["right"]
            lines.append(f"{indent}# Build binary operation: combine left with right tail")
            lines.append(f"{indent}if {right}:")
            lines.append(f"{indent}    return {right}({left})")
            lines.append(f"{indent}else:")
            lines.append(f"{indent}    return {left}")
        elif "op" in fields:
            # Pattern: op=OPERATOR right=$1 tail=$2 (build chain)
            op = fields["op"]
            right = fields["right"]
            tail = fields.get("tail", None)
            first_token_idx = _find_first_token(rhs)
            pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
            lines.append(f"{indent}# Build binary operation chain")
            lines.append(f"{indent}def build_op(left):")
            lines.append(f"{indent}    node = BinaryOp(left, {op}, {right}, {pos_args})")
            if tail:
                lines.append(f"{indent}    if {tail}:")
                lines.append(f"{indent}        return {tail}(node)")
            lines.append(f"{indent}    return node")
            lines.append(f"{indent}return build_op")
        else:
            lines.append(f"{indent}# Unknown binop pattern")
            lines.append(f"{indent}return None")
    
    elif action.action_type == "build_access":
        # Build array/table accessor chains
        # Pattern 1: base=$0 tail=$1 - identifier with accessor tail
        # Pattern 2: type=array value=$1 - start array accessor
        # Pattern 3: index=... tail=$2 - array index access
        # Pattern 4: type=table field=... tail=$2 - table field access
        fields = _parse_field_mapping(action.field_mapping, rhs)
        
        if "base" in fields and "tail" in fields:
            # Pattern: base identifier with accessor tail
            base_ref = fields["base"]
            tail = fields["tail"]
            
            # Check if base is a terminal token (like id) that needs wrapping
            # Extract the index from base_ref (e.g., "token_0" -> 0)
            base_match = re.match(r'(token|node)_(\d+)', base_ref)
            if base_match and base_match.group(1) == "token":
                # It's a terminal token - wrap in Identifier
                idx = int(base_match.group(2))
                if idx < len(rhs) and rhs[idx] == "id":
                    lines.append(f"{indent}# Build accessor: id token with tail")
                    lines.append(f"{indent}base = Identifier({base_ref}.value, {base_ref}.line, {base_ref}.col)")
                    lines.append(f"{indent}if {tail}:")
                    lines.append(f"{indent}    return {tail}(base)")
                    lines.append(f"{indent}else:")
                    lines.append(f"{indent}    return base")
                else:
                    # Other terminal - just use as is
                    lines.append(f"{indent}# Build accessor: base with tail")
                    lines.append(f"{indent}if {tail}:")
                    lines.append(f"{indent}    return {tail}({base_ref})")
                    lines.append(f"{indent}else:")
                    lines.append(f"{indent}    return {base_ref}")
            else:
                # It's a nonterminal node - use as is
                lines.append(f"{indent}# Build accessor: base with tail")
                lines.append(f"{indent}if {tail}:")
                lines.append(f"{indent}    return {tail}({base_ref})")
                lines.append(f"{indent}else:")
                lines.append(f"{indent}    return {base_ref}")
        elif fields.get("type") == '"array"':
            # Array accessor start
            value = fields.get("value", "None")
            lines.append(f"{indent}# Build array accessor start")
            lines.append(f"{indent}return {value}")
        elif "index" in fields:
            # Array index access with tail
            index = fields["index"]
            tail = fields.get("tail", "None")
            first_token_idx = _find_first_token(rhs)
            pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
            lines.append(f"{indent}# Build array accessor chain")
            lines.append(f"{indent}def build_access(base):")
            lines.append(f"{indent}    node = ArrayAccess(base, {index}, {pos_args})")
            lines.append(f"{indent}    if {tail}:")
            lines.append(f"{indent}        return {tail}(node)")
            lines.append(f"{indent}    return node")
            lines.append(f"{indent}return build_access")
        elif fields.get("type") == '"table"':
            # Table field access with tail
            field = fields.get("field", '""')
            tail = fields.get("tail", "None")
            first_token_idx = _find_first_token(rhs)
            pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
            lines.append(f"{indent}# Build table accessor chain")
            lines.append(f"{indent}def build_access(base):")
            lines.append(f"{indent}    node = TableAccess(base, {field}, {pos_args})")
            lines.append(f"{indent}    if {tail}:")
            lines.append(f"{indent}        return {tail}(node)")
            lines.append(f"{indent}    return node")
            lines.append(f"{indent}return build_access")
        else:
            lines.append(f"{indent}# Unknown accessor pattern")
            lines.append(f"{indent}return None")
    
    elif action.action_type == "token":
        # Return token value
        lines.append(f"{indent}return self.tokens[self.pos - 1].value")
    
    elif action.action_type == "count_dims":
        # Count dimensions for arrays
        fields = _parse_field_mapping(action.field_mapping, rhs)
        base = fields.get("base", "1")
        tail = fields.get("tail", "0")
        lines.append(f"{indent}# Count dimensions")
        lines.append(f"{indent}return {base} + (({tail}) if {tail} else 0)")
    
    elif action.action_type == "build_notation":
        # Build notation/accessor chain (same as build_access with base and tail)
        fields = _parse_field_mapping(action.field_mapping, rhs)
        base_ref = fields.get("base", "None")
        tail = fields.get("tail", "None")
        
        # Check if base is a terminal token (like id) that needs wrapping
        base_match = re.match(r'(token|node)_(\d+)', base_ref)
        if base_match and base_match.group(1) == "token":
            idx = int(base_match.group(2))
            if idx < len(rhs) and rhs[idx] == "id":
                # It's an id token - wrap in Identifier
                lines.append(f"{indent}# Build notation with id token")
                lines.append(f"{indent}base = Identifier({base_ref}.value, {base_ref}.line, {base_ref}.col)")
                lines.append(f"{indent}if {tail}:")
                lines.append(f"{indent}    return {tail}(base)")
                lines.append(f"{indent}else:")
                lines.append(f"{indent}    return base")
            else:
                # Other terminal
                lines.append(f"{indent}# Build notation with accessor chain")
                lines.append(f"{indent}if {tail}:")
                lines.append(f"{indent}    return {tail}({base_ref})")
                lines.append(f"{indent}else:")
                lines.append(f"{indent}    return {base_ref}")
        else:
            # It's a nonterminal node
            lines.append(f"{indent}# Build notation with accessor chain")
            lines.append(f"{indent}if {tail}:")
            lines.append(f"{indent}    return {tail}({base_ref})")
            lines.append(f"{indent}else:")
            lines.append(f"{indent}    return {base_ref}")
    
    elif action.action_type == "build_unary":
        # Build unary operation with optional tail
        # Pattern: operator=not operand=$1 tail=$2
        fields = _parse_field_mapping(action.field_mapping, rhs)
        operator = fields.get("operator", '"not"')
        operand = fields.get("operand", "None")
        tail = fields.get("tail", "None")
        first_token_idx = _find_first_token(rhs)
        pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
        
        lines.append(f"{indent}# Build unary operation")
        lines.append(f"{indent}node = UnaryOp({operator}, {operand}, {pos_args})")
        lines.append(f"{indent}if {tail}:")
        lines.append(f"{indent}    return {tail}(node)")
        lines.append(f"{indent}else:")
        lines.append(f"{indent}    return node")
    
    elif action.action_type == "build_call":
        # Build a function call closure
        # Pattern: args=<flavor> tail=<accessor_tail>
        # Returns a closure that takes a base (Identifier) and creates a FunctionCall
        lines.append(f"{indent}# Build function call closure")
        
        fields = _parse_field_mapping(action.field_mapping, rhs)
        args_ref = fields.get("args", "[]")
        
        # Generate closure that extracts name from base Identifier
        first_token_idx = _find_first_token(rhs)
        pos_args = f"token_{first_token_idx}.line, token_{first_token_idx}.col" if first_token_idx is not None else "None, None"
        
        lines.append(f"{indent}def build_call(base):")
        lines.append(f"{indent}    # Extract function name from Identifier node")
        lines.append(f"{indent}    if hasattr(base, 'name'):")
        lines.append(f"{indent}        func_name = base.name")
        lines.append(f"{indent}    else:")
        lines.append(f"{indent}        func_name = str(base)")
        lines.append(f"{indent}    ")
        lines.append(f"{indent}    # Create FunctionCall node")
        lines.append(f"{indent}    node = FunctionCall(func_name, {args_ref}, {pos_args})")
        
        # Only add tail handling if tail is specified
        if "tail" in fields:
            tail_ref = fields["tail"]
            lines.append(f"{indent}    ")
            lines.append(f"{indent}    # Apply accessor tail if present")
            lines.append(f"{indent}    if {tail_ref}:")
            lines.append(f"{indent}        return {tail_ref}(node)")
        
        lines.append(f"{indent}    return node")
        lines.append(f"{indent}")
        lines.append(f"{indent}return build_call")
    
    elif action.action_type == "manual":
        # Manual inline Python code - substitute $N references
        code = action.field_mapping.strip()
        code = _substitute_field_value(code, rhs)
        lines.append(f"{indent}# Manual code")
        lines.append(f"{indent}return {code}")
    
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
    
    # Check if we need to set context_id between parsing steps
    context_id_info = None
    if action and action.action_type == "propagate" and "context_id=" in action.field_mapping:
        # Extract context_id setting info
        parts = action.field_mapping.split()
        for part in parts:
            if part.startswith("context_id="):
                context_val = part.split("=")[1]
                # Check which symbol it references (e.g., $0.value means after parsing symbol 0)
                if context_val.startswith("$"):
                    idx_match = re.match(r'\$(\d+)', context_val)
                    if idx_match:
                        context_idx = int(idx_match.group(1))
                        context_id_info = (context_idx, context_val)
                break
    
    # Parse all symbols in RHS and capture them as node_N
    for i, sym in enumerate(rhs):
        if _is_nonterminal(sym):
            sym_name = _strip_angle(sym)
            
            # Check if this is an array_declare_tail function that needs dimensions context
            if "array_declare_tail" in sym_name:
                # Only set context if we're in an array_decl function (not recursive tail)
                # Check if first symbol is <dimensions> (means we're in array_decl)
                if rhs and _strip_angle(rhs[0]) == "dimensions":
                    lines.append(f"{indent}# Set context for array tail declarations")
                    lines.append(f"{indent}self._context_dimensions = node_0")
            
            # Check if this is table_decl that needs table type context
            # Pattern: id <table_decl> (id is the table type name)
            elif sym_name == "table_decl":
                # Check if previous symbol was "id" terminal
                if i > 0 and rhs[i-1] == "id":
                    lines.append(f"{indent}# Set table type context")
                    lines.append(f"{indent}self._context_type = token_{i-1}.value")
            
            lines.append(f"{indent}node_{i} = self.{_safe_func_name(sym)}()")
        else:
            # For terminals, capture the token before parsing it
            # This allows us to access its value with $N.value in AST actions
            lines.append(f"{indent}token_{i} = self.tokens[self.pos]")
            lines.append(f'{indent}self.parse_token("{sym}")')
        
        # Check if we need to set context_id after parsing this symbol
        if context_id_info and context_id_info[0] == i:
            context_val = context_id_info[1]
            context_subst = _substitute_field_value(context_val, rhs)
            lines.append(f"{indent}# Set identifier context for subsequent parsing")
            lines.append(f"{indent}self._context_identifier = {context_subst}")
            # Also store position info if it's from a token
            if '.value' in context_val and '$' in context_val:
                idx_match = re.match(r'\$(\d+)', context_val)
                if idx_match:
                    idx = int(idx_match.group(1))
                    if idx < len(rhs) and not _is_nonterminal(rhs[idx]):
                        lines.append(f"{indent}self._context_identifier_line = token_{idx}.line")
                        lines.append(f"{indent}self._context_identifier_col = token_{idx}.col")
    
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
    out.append(f'    self.appendF(FIRST_SET["{lhs}"])')
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
        
        # Context variables for passing info to tail parsing functions
        self._context_dimensions = None
        self._context_type = None
        self._context_identifier = None  # For passing identifier names to function calls
        self._context_identifier_line = None
        self._context_identifier_col = None
        
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
            token_2 = self.tokens[self.pos]
            self.parse_token("start")
            token_3 = self.tokens[self.pos]
            self.parse_token("(")
            token_4 = self.tokens[self.pos]
            self.parse_token(")")
            node_5 = self.platter()
            
            # Create Program node
            prog = Program()
            if isinstance(node_0, list):
                for decl in node_0:
                    prog.add_global_decl(decl)
            if isinstance(node_1, list):
                for recipe in node_1:
                    prog.add_recipe_decl(recipe)
            prog.set_start_platter(node_5)
            
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
        func_code = _emit_function(lhs, group_alts, ast_actions)
        # Note: FormatASTParser.py will add class method indentation
        chunks.append(func_code)
    
    # Write output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(chunks), encoding="utf-8")
    
    print(f"✓ Generated: {OUTPUT_FILE}")
    return OUTPUT_FILE


if __name__ == "__main__":
    path = generate()
    print(f"Wrote: {path}")
