# AST.TSV Documentation Guide

## Overview

The `ast.tsv` file is a specification that maps grammar productions from `cfg.tsv` to AST (Abstract Syntax Tree) construction actions. Each row defines how to build AST nodes when parsing a specific production rule.

---

## File Structure

### Columns (Tab-Separated)

```
prod_no    <lhs>           =>    action_type    ast_class         field_mapping                                note
1          <program>       =>    create         Program           global_decl=collect($0) ...                  Root node
```

| Column | Description |
|--------|-------------|
| `prod_no` | Production number matching cfg.tsv |
| `<lhs>` | Left-hand side nonterminal |
| `=>` | Separator (always "=>") |
| `action_type` | Type of AST action (see below) |
| `ast_class` | AST node class name (or "-" for no class) |
| `field_mapping` | How to construct the AST node |
| `note` | Human-readable description |

---

## Action Types

### 1. **create**
Creates a new AST node of the specified class.

**Syntax:**
```
action_type: create
ast_class: <ClassName>
field_mapping: field1=value1 field2=value2 ...
```

**Example:**
```tsv
1	<program>	=>	create	Program	global_decl=collect($0) recipe_decl=collect($1) start_platter=$5	Root node
```

**Simulation:**
- Parse production 1: `<program> => <global_decl> <recipe_decl> start ( ) <platter>`
- Capture: node_0 (global_decl), node_1 (recipe_decl), node_5 (platter)
- Create: `Program(global_decl=collect(node_0), recipe_decl=collect(node_1), start_platter=node_5)`

---

### 2. **propagate**
Pass through a child node, optionally with attribute mappings.

**Syntax:**
```
action_type: propagate
field_mapping: $N                    # Simple propagation
field_mapping: $N context_id=$M.value  # With context setting
field_mapping: type="piece" dims=$1    # Attribute mapping
```

**Examples:**

**Simple propagation:**
```tsv
9	<piece_decl>	=>	propagate	-	$1	Piece declaration
```
Production: `<piece_decl> => of <piece_id> ;`
- Returns: node_1 (the piece_id result)

**Attribute mapping:**
```tsv
148	<primitive_types_dims>	=>	propagate	-	type="piece" dims=$1	Piece type
```
Production: `<primitive_types_dims> => piece <dimensions_tail>`
- Creates: `PropagatedAttrs` object with `type="piece"` and `dims=node_1`
- Returns: This attribute object

**Context setting:**
```tsv
197	<id_statements>	=>	propagate	-	$1 context_id=$0.value	ID statement extension
```
- Sets `self._context_identifier = token_0.value`
- Returns: node_1

---

### 3. **collect**
Collects/aggregates nodes into a list.

**Syntax:**
```
action_type: collect
field_mapping: [<expression>] + $N
field_mapping: $M + $N
field_mapping: []
```

**Examples:**

**List construction:**
```tsv
11	<piece_id>	=>	collect	-	[VarDecl("piece", $0.value, $1)] + $2	Piece var
```
Production: `<piece_id> => id <piece_ingredient_init> <piece_id_tail>`
- Creates: `[VarDecl("piece", token_0.value, node_1)] + node_2`
- Result: A list starting with one VarDecl, concatenated with the tail list

**List concatenation:**
```tsv
2	<global_decl>	=>	collect	-	$1 + $2	Piece global var
```
Production: `<global_decl> => piece <piece_decl> <global_decl>`
- Returns: `node_1 + node_2` (concatenate two lists)

**Empty list:**
```tsv
8	<global_decl>	=>	collect	-	[]	Empty global decl
```
- Returns: `[]` (empty list)

---

### 4. **build_binop**
Builds binary operation chains (left-associative).

**Syntax:**
```
field_mapping: left=$0 right=$1          # Combine left with tail
field_mapping: op=<operator> right=$N tail=$M  # Build operation
```

**Examples:**

**Tail combination:**
```tsv
319	<strict_chars_expr>	=>	build_binop	-	left=$0 right=$1	Chars expression
```
Production: `<strict_chars_expr> => <strict_chars_factor> <strict_chars_add_tail>`
- If tail exists: `left = node_0; tail(left)` (tail function modifies left)
- If tail is None: return `node_0`

**Operation construction:**
```tsv
323	<strict_chars_add_tail>	=>	build_binop	-	op=+ right=$1 tail=$2	Chars add tail
```
Production: `<strict_chars_add_tail> => + <strict_chars_factor> <strict_chars_add_tail>`
- Creates: `BinaryOp("+", left, node_1)`
- If tail exists: tail(result)
- Returns: Chained binary operation

---

### 5. **build_access**
Builds array/table accessor chains.

**Syntax:**
```
field_mapping: base=$0 tail=$1           # ID with accessor
field_mapping: type=array value=$N       # Array access start
field_mapping: index=<expr> tail=$N      # Array index
field_mapping: type=table field=$N tail=$M  # Table field
```

**Example:**
```tsv
376	<id>	=>	build_access	-	base=$0 tail=$1	Identifier with accessor
```
Production: `<id> => id <id_tail>`
- Base: `Identifier(token_0.value)`
- If tail exists: tail(base)
- Returns: Base or accessor-wrapped identifier

---

### 6. **build_call**
Builds a function call closure.

**Syntax:**
```
field_mapping: args=$N                   # Arguments list
field_mapping: args=$N tail=$M           # With tail
```

**Example:**
```tsv
379	<call_tailopt>	=>	build_call	-	args=$1	Function call
```
Production: `<call_tailopt> => ( <flavor> )`
- Returns: A closure that takes a base and creates `FunctionCall(base.name, args)`

---

### 7. **build_unary**
Builds unary operations.

**Syntax:**
```
field_mapping: operator=<op> operand=$N tail=$M
```

**Example:**
```tsv
416	<flag_operand>	=>	build_unary	-	operator=not operand=$1 tail=$2	Flag not
```
Production: `<flag_operand> => not <flag_operand> <flag_op_tail>`
- Creates: `UnaryOp("not", node_1)`
- If tail exists: tail(result)

---

### 8. **build_notation**
Builds notation/accessor chains (similar to build_access).

**Example:**
```tsv
86	<notation_val>	=>	build_notation	-	base=$0 tail=$1	Notation with tail
```

---

### 9. **token**
Returns token value.

**Example:**
```tsv
381	<chars_ops>	=>	token	-	value=+	+
```
Production: `<chars_ops> => +`
- Returns: `"+"` (the operator value)

---

### 10. **count_dims**
Counts array dimensions.

**Example:**
```tsv
77	<dimensions>	=>	count_dims	-	base=1 tail=$2	Count dimensions
```
Production: `<dimensions> => [ ] <dimensions_tail>`
- Returns: `1 + (node_2 if node_2 else 0)`

---

### 11. **skip**
Returns None (no AST node).

**Example:**
```tsv
13	<piece_ingredient_init>	=>	skip	-	-	No initializer
```

---

### 12. **manual**
Executes arbitrary Python code for complex AST construction. Use when standard actions are insufficient.

**Syntax:**
```
action_type: manual
field_mapping: <python_expression>
```

**Examples:**

**Setting context with tuple unpacking:**
```tsv
197	<id_statements>	=>	manual	-	(lambda ctx, stmt, rest: (setattr(self, '_context_identifier', ctx), stmt + rest)[1])($0.value, [$1], $2)
```
Production: `<id_statements> => id <id_statements_ext> <statements>`
- Lambda sets `self._context_identifier = token_0.value`
- Returns: `[node_1] + node_2` (current statement + remaining statements)
- Note: Uses `setattr()` because walrus operator `:=` doesn't work with attributes

**Nested binary operations:**
```tsv
423	<arith_operand>	=>	manual	-	lambda left: BinaryOp(BinaryOp(left, "%", $1), $2, $3)
```
Production: `<arith_operand> => % <arith_operand> <rel_op> <rel_operand>`
- Creates nested BinaryOp for expressions like `n % 2 != 0`
- Needed when $2 is a string operator, not a function

**Filtering mixed node types:**
```tsv
171	<platter>	=>	manual	-	(lambda decls, stmts: Platter([d for d in decls if isinstance(d, (VarDecl, ArrayDecl, TableDecl))], [s for s in decls if isinstance(s, (Assignment, ExpressionStatement, ...))] + stmts))($1, $2)
```
Production: `<platter> => { <local_decl> <statements> }`
- Separates declarations from statements in mixed list
- local_decl may contain both VarDecl and Assignment nodes

**When to use manual:**
- Context variables need setting mid-production
- Complex filtering or conditional logic required
- Standard actions produce incorrect AST structure
- Multiple nested operations in one production

---

## Field Mapping Syntax

### Positional References

| Reference | Meaning |
|-----------|---------|
| `$0` | First symbol in RHS (node_0 or token_0) |
| `$1` | Second symbol (node_1 or token_1) |
| `$N` | Nth symbol (0-indexed) |

**Important:** Both terminals and nonterminals increment the position counter. In the generated code:
- Terminals are captured as `token_N`
- Nonterminals are captured as `node_N`
- Both use the same position index N

**Example from Production 1:**
```
<program> => <global_decl> <recipe_decl> start ( ) <platter>
Positions:   0             1             2     3 4 5
```
- `$0` → `node_0` (global_decl)
- `$1` → `node_1` (recipe_decl)
- `$2` → `token_2` (start)
- `$3` → `token_3` ("(")
- `$4` → `token_4` (")")
- `$5` → `node_5` (platter)

So `start_platter=$5` correctly refers to the platter nonterminal at position 5, which becomes `node_5` in the generated code.

### Attribute Access

| Syntax | Meaning |
|--------|---------|
| `$0.value` | Access token value: `token_0.value` |
| `$0_fieldname` | Access node attribute: `node_0.fieldname` |

### Context Variables

| Variable | Meaning |
|----------|---------|
| `CONTEXT` | `self._context_dimensions` |
| `CONTEXT_TYPE` | `self._context_type` |
| `CONTEXT_ID` | `self._context_identifier` |

### Special Functions

| Function | Meaning |
|----------|---------|
| `collect($0)` | Ensure $0 is a list (for create actions) |

---

## Simulation Guide

### How to Trace a Production

**Example: Production 11**
```tsv
11	<piece_id>	=>	collect	-	[VarDecl("piece", $0.value, $1)] + $2	Piece var
```

**Step 1: Find the Production in cfg.tsv**
```
11	<piece_id>	=>	id	<piece_ingredient_init>	<piece_id_tail>
```

**Step 2: Identify RHS Symbols**
- Position 0: `id` (terminal → token_0)
- Position 1: `<piece_ingredient_init>` (nonterminal → node_1)
- Position 2: `<piece_id_tail>` (nonterminal → node_2)

**Step 3: Parse the Action**
- Action: `collect`
- Expression: `[VarDecl("piece", $0.value, $1)] + $2`

**Step 4: Substitute References**
- `$0.value` → `token_0.value` (the identifier name)
- `$1` → `node_1` (the initializer expression or None)
- `$2` → `node_2` (the tail list)

**Step 5: Simulate Execution**
```python
# Create a VarDecl node
var_decl = VarDecl("piece", token_0.value, node_1)

# Put it in a list and concatenate with tail
result = [var_decl] + node_2

# Return the list
return result
```

**Step 6: Verify Result Type**
- Returns: `List[VarDecl]`
- Used by: Parent productions that expect a list of declarations

---

## Common Patterns

### Pattern 1: List Building (Head + Tail)
```tsv
80	<flavor>	=>	collect	-	[$0] + $1	Arguments list
81	<flavor>	=>	collect	-	[]	No arguments
```

**Usage:**
- Production 80: Start list with first element, add tail
- Production 81: Base case - empty list

### Pattern 2: Left-Recursive Binary Operations
```tsv
325	<strict_piece_expr>	=>	build_binop	-	left=$0 right=$1	Piece expression
334	<strict_piece_add_tail>	=>	build_binop	-	op=+ right=$1 tail=$2	Piece add
336	<strict_piece_add_tail>	=>	skip	-	-	Empty add tail
```

**Flow:**
1. Parse left operand
2. Parse tail (may be empty)
3. If tail exists, it returns a closure that builds BinaryOp
4. Result: `BinaryOp("+", left, right)` or just `left`

### Pattern 3: Optional Elements
```tsv
45	<piece_array_init>	=>	propagate	-	$1	Has array init
46	<piece_array_init>	=>	skip	-	-	No array init
```

**Usage:**
- Production 45: Return the initializer
- Production 46: Return None (no initializer)

### Pattern 4: Type Propagation with Attributes
```tsv
148	<primitive_types_dims>	=>	propagate	-	type="piece" dims=$1	Piece type
```

**Creates:**
```python
class PropagatedAttrs:
    pass

result = PropagatedAttrs()
result.type = "piece"
result.dims = node_1
return result
```

---

## Validation Checklist

### For Each Entry:

1. **Production Number Match**
   - [ ] prod_no exists in cfg.tsv
   - [ ] LHS matches cfg.tsv entry

2. **Action Type**
   - [ ] Action type is valid (create/propagate/collect/build_binop/etc.)
   - [ ] ast_class matches action type requirements

3. **Field Mapping**
   - [ ] All `$N` references are within RHS bounds (0 to len(rhs)-1)
   - [ ] Terminal references use `.value` (e.g., `$0.value`)
   - [ ] Nonterminal references are direct (e.g., `$1`, not `$1.value`)
   - [ ] Attribute access uses underscore (e.g., `$0_type`)

4. **Context Variables**
   - [ ] CONTEXT variables are used appropriately
   - [ ] Context is set before being used

5. **AST Class**
   - [ ] Class name matches ast_nodes.py definitions
   - [ ] Constructor fields match the class signature

6. **Type Consistency**
   - [ ] Lists are built consistently (all elements same type)
   - [ ] Binary operations have compatible operands
   - [ ] Field assignments have correct types

---

## Debugging Tips

### Issue: "can only concatenate list (not 'X') to list"
**Cause:** Mixing single object with list in collect action
**Fix:** Wrap single objects in brackets: `[$0] + $1` not `$0 + $1`

### Issue: "AttributeError: 'Token' object has no attribute 'X'"
**Cause:** Accessing attribute on terminal instead of using .value
**Fix:** Use `$0.value` for terminals, not `$0_fieldname`

### Issue: "'str' object is not callable"
**Cause:** Operator returned as string but used as function in build_binop tail
**Fix:** Use `manual` action with explicit `BinaryOp()` construction

### Issue: "cannot use assignment expressions with attribute"
**Cause:** Using walrus operator `:=` with object attributes like `self._context_id`
**Fix:** Use `setattr(self, '_context_identifier', value)` in lambda instead

### Issue: Statements/nodes missing from AST
**Cause:** Action returns only first element, discarding recursive continuation
**Fix:** Ensure recursive productions return `$current + $tail`, not just `$current`

---

## Quick Reference Table

| Action | When to Use | Returns |
|--------|-------------|---------|
| `create` | Building new AST node | AST node instance |
| `propagate` | Passing through child | Child node or attributes |
| `collect` | Building lists | List of nodes |
| `build_binop` | Binary operations | BinaryOp or closure |
| `build_access` | Array/table access | Accessor or closure |
| `build_call` | Function calls | Closure returning FunctionCall |
| `build_unary` | Unary operations | UnaryOp |
| `token` | Terminal value | String value |
| `count_dims` | Array dimensions | Integer |
| `manual` | Complex logic/filtering | Any type |
| `skip` | No AST needed | None |

---

## Testing Your Changes

After modifying ast.tsv:

1. **Regenerate Parser:**
   ```bash
   npm run build
   ```

2. **Run Tests:**
   ```bash
   npm test
   ```

3. **Check Specific Test:**
   ```bash
   cd platter-compiler-sveltejs/static/python
   python -m pytest tests/ga_parser_ast_valid.py::Test_valid_tests::test_your_file -v
   ```

---

## Example: Complete Trace

**Line 164 in ast.tsv:**
```tsv
164	<recipe_decl>	=>	collect	-	[RecipeDecl($1_data_type,$1_dimensions,$1_identifier,$3,$5)] + $6
```

**Production in cfg.tsv:**
```
164	<recipe_decl>	=>	recipe	<serve_type>	(	<spice>	)	<platter>	<recipe_decl>
```

**Trace:**
1. Position 0: Parse `recipe` token → token_0
2. Position 1: Parse `<serve_type>` → node_1 (returns PropagatedAttrs with type/dims/identifier)
3. Position 2: Parse `(` token → token_2
4. Position 3: Parse `<spice>` → node_3 (returns list of parameters)
5. Position 4: Parse `)` token → token_4
6. Position 5: Parse `<platter>` → node_5 (returns Platter node)
7. Position 6: Parse `<recipe_decl>` → node_6 (returns list of more recipes)

**Execute Action:**
```python
# Access attributes from node_1
data_type = node_1.data_type
dimensions = node_1.dimensions
identifier = node_1.identifier

# Create RecipeDecl
recipe = RecipeDecl(data_type, dimensions, identifier, node_3, node_5)

# Collect into list with tail
result = [recipe] + node_6
return result
```

**Result:** List of RecipeDecl nodes

---

## Summary

- Each line maps a grammar production to AST construction
- Use `$N` to reference parsed symbols (0-indexed)
- Terminals use `.value`, nonterminals are direct
- Attribute access uses `_fieldname` suffix
- Test changes with `npm run build` and `npm test`
