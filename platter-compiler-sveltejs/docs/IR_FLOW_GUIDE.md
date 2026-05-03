# Platter Compiler: IR Generation Flow Guide

## Overview

IR generation is the stage that converts a validated AST into a lower-level, executable intermediate form.

In Platter, the IR generator produces two synchronized representations at the same time:

1. **Three Address Code (TAC)** for readable step-by-step instructions
2. **Quadruples** for structured `(operator, arg1, arg2, result)` form

This stage happens after parsing and semantic analysis.

```
Source
   ->
AST
   ->
Semantic Analysis
   ->
IR Generation
   ->
TAC + Quadruples
   ->
Optimization / Interpretation
```

The main purpose of IR generation is to:

- linearize the AST into instructions
- break complex expressions into small steps
- introduce temporary variables for intermediate results
- introduce labels and jumps for control flow
- represent arrays, tables, calls, and returns in a uniform low-level format

---

## Entry Point

**File:** `platter-compiler-sveltejs/static/python/app/intermediate_code/ir_generator.py`  
**Class:** `IRGenerator`  
**Main method:** `generate(ast)`

### Main Pipeline

```python
def generate(self, ast: Program):
    self.emit_comment("=== Platter Program IR ===")

    if ast.global_decl:
        self.emit_comment("Global Declarations")
        for decl in ast.global_decl:
            self.visit_declaration(decl)

    if ast.recipe_decl:
        self.recipe_names = {recipe.name for recipe in ast.recipe_decl}
        self.emit_comment("Recipe Declarations")
        for recipe in ast.recipe_decl:
            self.visit_recipe_decl(recipe)

    if ast.start_platter:
        self.emit_comment("Main Program (start)")
        self.emit_tac(TACFunctionBegin("start"))
        self.emit_quad("begin_func", "start")

        self.visit_platter(ast.start_platter)

        self.emit_tac(TACFunctionEnd("start"))
        self.emit_quad("end_func", "start")
```

### Output

`generate(ast)` returns:

```python
(
    List[TACInstruction],
    QuadrupleTable
)
```

### Code-Level Flow Inside `IRGenerator`

When reading `ir_generator.py`, the flow of control is:

```text
generate()
   ->
visit_declaration() / visit_recipe_decl() / visit_platter()
   ->
visit_statement()
   ->
visit_expression()
   ->
emit_tac() + emit_quad()
```

That means the generator works like a tree walk:

1. `generate()` starts the whole process from the `Program` root.
2. It dispatches top-level nodes into declaration visitors and recipe visitors.
3. `visit_platter()` walks block contents in source order.
4. `visit_statement()` chooses the correct lowering rule for each statement.
5. `visit_expression()` recursively lowers subexpressions and returns the name that now holds the result.
6. Every lowering step writes to both IR outputs immediately through `emit_tac()` and `emit_quad()`.

This is the most important mental model for the file:

- declaration visitors allocate or initialize storage
- statement visitors create control flow
- expression visitors compute values into temporaries
- helper emitters keep TAC and quadruples synchronized

---

## Inputs and Outputs

### Input

- semantically valid `Program` AST
- declarations, expressions, and statement nodes from `ast_nodes.py`

### Output

- `self.tac_instructions`: flat list of TAC instructions
- `self.quad_table`: flat list of quadruples with indices

### Important Assumption

The IR generator is not the stage that validates meaning. It assumes semantic analysis has already succeeded.

That means:

- identifiers are already declared
- type errors were already caught
- invalid `serve`, `stop`, or `next` were already rejected

---

## Core IR Data Structures

### TAC Instructions

**File:** `intermediate_code/tac.py`

Each TAC instruction is an object like:

- `TACAssignment`
- `TACBinaryOp`
- `TACUnaryOp`
- `TACArrayAccess`
- `TACArrayAssign`
- `TACTableAccess`
- `TACTableAssign`
- `TACLabel`
- `TACGoto`
- `TACConditionalGoto`
- `TACParam`
- `TACFunctionCall`
- `TACReturn`
- `TACFunctionBegin`
- `TACFunctionEnd`
- `TACAllocate`
- `TACCast`
- `TACComment`

### Example

```python
TACBinaryOp("t3", "a", "+", "b")
```

Readable form:

```text
t3 = a + b
```

### Quadruples

**File:** `intermediate_code/quadruple.py`

A quadruple stores:

```python
(operator, arg1, arg2, result)
```

### Example

```python
("+", "a", "b", "t3")
```

Readable form:

```text
t3 = a + b
```

### Why Both Are Generated

The generator emits both forms in parallel so:

- TAC is easy for humans to read and debug
- quadruples are easy for later passes to analyze and transform

Every major emission site does both:

```python
self.emit_tac(...)
self.emit_quad(...)
```

---

## Generator State

The IR generator maintains internal state while walking the AST:

### Temporary Counter

```python
self.temp_count = 0
```

Used by:

```python
def new_temp(self):
    return f"t{self.temp_count}"
```

Temporary names look like:

- `t0`
- `t1`
- `t2`

### Label Counter

```python
self.label_count = 0
```

Used by:

```python
def new_label(self, prefix="L"):
    return f"{prefix}{self.label_count}"
```

Labels look like:

- `else0`
- `endif1`
- `while_start2`
- `for_end3`

### Current Function

Tracks which recipe is being emitted.

### Recipe Name Set

```python
self.recipe_names = set()
```

Used for parser-compatibility fallback when a zero-argument recipe call is emitted as an `Identifier`.

### Loop Stack

```python
self.loop_stack: List[Tuple[str, str]]
```

Stores:

```python
(continue_label, break_label)
```

This lets `next` and `stop` jump to the correct target inside nested loops or `menu` blocks.

---

## Phase 1: Program-Level Emission

The generator emits the program in this order:

1. global declarations
2. recipe declarations
3. `start()` platter

At code level, this happens in `generate()`:

```python
if ast.global_decl:
    for decl in ast.global_decl:
        self.visit_declaration(decl)

if ast.recipe_decl:
    for recipe in ast.recipe_decl:
        self.visit_recipe_decl(recipe)

if ast.start_platter:
    self.emit_tac(TACFunctionBegin("start"))
    self.visit_platter(ast.start_platter)
    self.emit_tac(TACFunctionEnd("start"))
```

What this block does:

- walks global declarations first so their runtime setup is emitted before `start`
- emits every recipe body as a function region
- wraps the top-level `start` block inside `begin_func start` / `end_func start`
- preserves source order inside each region

### Why This Order Matters

- global variables must exist before runtime execution reaches `start`
- recipe bodies are emitted as functions
- `start` is emitted last as the entry function of the executable program flow

### Comments Are Emitted Too

The generator inserts readable markers like:

```text
# === Platter Program IR ===
# Global Declarations
# Recipe Declarations
# Main Program (start)
```

These comments exist in both TAC and quadruple output.

---

## Phase 2: Declaration Lowering

### Ingredient Declarations

### File Path

`visit_var_decl(node)`

### Behavior

#### With initializer

```platter
piece of x = a + b ;
```

Becomes roughly:

```text
t0 = a + b
x = t0
```

What the code does:

1. `visit_var_decl()` asks `visit_expression()` to compute the initializer.
2. `visit_expression()` returns either a literal, identifier name, or temporary like `t0`.
3. The declaration visitor emits an assignment into the declared variable.

#### Without initializer

The generator emits a default runtime assignment:

- `piece` -> `0`
- `sip` -> `0.0`
- `chars` -> `""`
- `flag` -> `down`

Example:

```platter
piece of x ;
```

Becomes:

```text
x = 0
```

What the code does:

- chooses a default runtime value based on `node.data_type`
- emits that default directly as an assignment
- avoids leaving primitive variables uninitialized in the IR

### Array Declarations

### Array literal initializer

```platter
piece [] of nums = { 1 , 2 , 3 } ;
```

Lowering:

```text
nums = allocate array 3
nums[0] = 1
nums[1] = 2
nums[2] = 3
```

What the code does:

1. `visit_array_decl()` measures the literal length.
2. It emits `allocate array size`.
3. It walks each literal element in order.
4. Each element is lowered with `visit_expression()`.
5. The result is written to `array[index]`.

### Expression initializer

If an array is initialized from an expression or recipe call, the generator emits a normal assignment from that computed value.

### Uninitialized arrays

Uninitialized array declarations do not emit runtime initialization code.

### Table Prototypes

Table prototypes are type-only definitions, so they emit no executable runtime code.

Instead, the generator only emits a comment:

```text
# Table type: Point
```

### Table Declarations

```platter
Point of p = { x : 1 , y : 2 } ;
```

Lowering:

```text
p = allocate table Point
p.x = 1
p.y = 2
```

What the code does:

- allocates a runtime table object first
- lowers each field initializer one by one
- emits a field write for every `field : value` pair
- falls back to plain assignment when the initializer is an expression instead of a literal

If the initializer is another expression, the generator emits a normal assignment after allocation logic.

---

## Phase 3: Recipe Lowering

### Entry Shape

Each recipe is lowered as:

```text
begin_func recipeName
... parameter binding ...
... body ...
return
end_func recipeName
```

This structure comes directly from `visit_recipe_decl(node)`.

What that block of code does:

1. stores the current recipe name in `self.current_function`
2. emits a readable comment such as `# Recipe: add`
3. emits function begin markers in both TAC and quadruples
4. binds incoming positional arguments to declared parameter names
5. lowers the recipe body through `visit_platter(node.body)`
6. appends a final `return`
7. emits the function end marker

### Parameter Binding

Arguments are passed positionally as synthetic names:

- `p0`
- `p1`
- `p2`

When entering a recipe, the generator binds those positional slots to declared spice names:

```python
for i, param in enumerate(node.params):
    self.emit_tac(TACAssignment(param.identifier, f"p{i}"))
```

Example:

```platter
piece add ( piece of a , piece of b ) :
    serve a + b ;
```

Starts as:

```text
begin_func add
a = p0
b = p1
...
end_func add
```

### Automatic Final Return

After emitting the body, the generator always appends:

```text
return
```

This guarantees the function body has a terminator in IR even if the source already emitted an explicit `serve`.

---

## Phase 4: Statement Lowering

### Assignment

### Simple assignment

```platter
x = y + 1 ;
```

Lowering:

```text
t0 = y + 1
x = t0
```

What the code does:

- `visit_assignment()` lowers the right-hand side first
- if the operator is `=`, it delegates the final write to `emit_assignment()`
- `emit_assignment()` checks whether the target is:
  - a scalar identifier
  - an array slot
  - a table field
- it then emits the correct write instruction for that target kind

### Compound assignment

```platter
x += 5 ;
```

Lowering:

```text
t0 = x + 5
x = t0
```

For `array[index] += value` or `table.field += value`, the generator:

1. reads the current value
2. computes the new value in a temp
3. writes back to the array slot or table field

In code, that is exactly why `visit_assignment()` first emits a read for `ArrayAccess` or `TableAccess`, then emits a `TACBinaryOp`, then calls `emit_assignment()` again for the write-back step.

### If / Alt / Instead

`check / alt / instead` is lowered with labels and jumps.

### Shape

```text
cond = ...
ifFalse cond goto else0
... then block ...
goto endif1
else0:
... elif / else chain ...
endif1:
```

Each `alt` gets its own label, and all successful branches jump to the shared end label.

What the code does inside `visit_if_statement()`:

1. creates one label for the first false branch and one final end label
2. lowers the main condition
3. emits `ifFalse` to skip the `then` block when needed
4. emits the `then` block
5. jumps to the shared end label after a successful branch
6. emits one extra label per `alt`
7. lowers the `instead` block only after all `alt` checks fail

### Repeat Loop

`repeat` lowers to:

```text
while_start0:
cond = ...
ifFalse cond goto while_end1
... body ...
goto while_start0
while_end1:
```

This shape comes from `visit_while_loop(node)`.

What that block of code does:

1. creates a start label and end label
2. pushes them into `loop_stack`
3. emits the start label
4. lowers the condition
5. emits `ifFalse` to leave the loop
6. emits the body
7. emits a back-edge jump to the start label
8. emits the end label and pops the loop context

The loop stack stores:

```python
(continue_label, break_label) = (while_start0, while_end1)
```

So:

- `next` jumps to `while_start0`
- `stop` jumps to `while_end1`

### Order-Repeat Loop

`order ... repeat` lowers to:

```text
do_start0:
... body ...
do_continue1:
cond = ...
if cond goto do_start0
do_end2:
```

This is why the continue target is not the start label, but the label just before condition re-check.

This block is produced by `visit_do_while_loop(node)`.

What that block of code does:

1. emits `do_start...` so execution always enters the body once
2. lowers the loop body before checking the condition
3. emits `do_continue...` as the place where `next` should jump
4. lowers the condition after the body
5. emits `if cond goto do_start...` to repeat only when the condition stays true
6. emits `do_end...` as the exit label for `stop`

So the `do_continue1:` line in the IR is not just a label name. It is the exact control-flow point the generator uses to make `next` skip the remainder of the body and continue with the condition re-check.

### Pass Loop

`pass` lowers to:

```text
... init ...
for_start0:
cond = ...
ifFalse cond goto for_end2
... body ...
for_continue1:
... update ...
goto for_start0
for_end2:
```

This gives `next` the correct behavior: it skips the rest of the body and jumps to the update step.

This block is produced by `visit_for_loop(node)`.

What that block of code does:

1. emits the initialization assignment first, if present
2. emits the loop-head label
3. lowers the condition and exits on `ifFalse`
4. emits the loop body
5. emits a dedicated continue label
6. emits the update assignment after that continue label
7. jumps back to the loop head
8. emits the end label for normal exit and `stop`

### Menu / Choice / Usual

`menu` lowers into a comparison chain:

1. evaluate menu expression
2. compare against each `choice`
3. jump to matching case label
4. jump to `usual` or end if nothing matches

### Shape

```text
t0 = menu_expr
t1 = t0 == case1
if t1 goto case0
t2 = t0 == case2
if t2 goto case1
goto default2

case0:
... statements ...
goto switch_end3

case1:
... statements ...
goto switch_end3

default2:
... statements ...
goto switch_end3

switch_end3:
```

There is no fall-through. Every case jumps to the common end label.

The generator also pushes a loop-like context so `stop` inside `menu` jumps to the menu end label.

What the code does inside `visit_switch_statement()`:

1. lowers the menu expression once and keeps it in a temporary
2. creates one label per `choice`
3. lowers each case value and emits an equality test against the menu expression
4. emits `if` jumps to the matching case labels
5. emits a default jump if no case matches
6. emits every case body under its own label
7. always jumps to the shared end label after each case body

That is why this implementation behaves like a non-fall-through switch.

### Serve

`serve expr ;` lowers to:

```text
t0 = ...
return t0
```

`serve ;` lowers to:

```text
return
```

What the code does:

- lowers the serve value first, if one exists
- emits `return value_temp` for value-returning recipes
- emits plain `return` for empty `serve`

### Stop and Next

These do not compute anything directly. They emit jumps using the top of `loop_stack`.

```text
goto break_label
goto continue_label
```

### Expression Statements

Normal expression statements simply evaluate the expression for side effects.

Special case:

When array-transforming built-ins are used as statements:

- `append`
- `remove`
- `sort`
- `reverse`

the generator writes the returned array back into the first identifier argument.

Example:

```platter
append ( nums , 5 ) ;
```

Lowering conceptually becomes:

```text
param nums
param 5
t0 = call append, 2
nums = t0
```

This preserves the expected source-level behavior for these built-ins.

What the code does:

- if the statement is an ordinary expression, it just lowers it for side effects
- if the statement is one of the array-transforming built-ins, it treats the returned array as the updated version of the first argument and writes it back

---

## Phase 5: Expression Lowering

Expressions are lowered recursively, and every complex result is stored in a temporary.

The code flow here is centered on one rule:

```python
def visit_expression(self, node):
    ...
    return name_of_value_holder
```

So each expression visitor does two jobs:

1. emit the instructions needed to compute the expression
2. return the identifier or temporary where the result now lives

### Binary Operation

```platter
a * ( b + c )
```

Lowering:

```text
t0 = b + c
t1 = a * t0
```

What the code does in `visit_binary_op(node)`:

1. lowers the left child
2. lowers the right child
3. allocates a fresh temp
4. emits one binary-op instruction whose result is that temp
5. returns the temp name to the caller

### Unary Operation

```platter
-x
```

Lowering:

```text
t0 = - x
```

Quadruple operator:

- `unary-` for unary minus
- `not` for logical negation

What the code does:

- lowers the operand first
- allocates a temp for the result
- emits `TACUnaryOp`
- emits a matching quadruple operator name

### Identifier

Identifiers are returned directly by name:

```python
return node.name
```

No extra temp is needed unless the identifier participates in a larger instruction.

### Literal

Literals are returned as immediate values.

Special case for `chars`:

String literals are forced to remain quoted so the TAC interpreter does not mistake them for variable names.

### Array Access

```platter
nums[i]
```

Lowering:

```text
t0 = nums[i]
```

### Table Access

```platter
p.x
```

Lowering:

```text
t0 = p.x
```

### Recipe Call

Calls are lowered in two steps:

1. evaluate and push each argument with `param`
2. emit `call`

Example:

```platter
add(1, 2)
```

Lowering:

```text
param 1
param 2
t0 = call add, 2
```

What the code does in `visit_function_call(node)`:

1. lowers each argument from left to right
2. emits one `param` instruction per argument in that same order
3. allocates a result temp
4. emits the `call`
5. returns the result temp to the parent expression or statement visitor

### Cast

```platter
topiece(x)
```

If represented as `CastExpr`, lowering is:

```text
t0 = (piece) x
```

Quadruple form:

```text
(cast, piece, x, t0)
```

### Array Literal

An array literal is lowered as a temporary allocated array:

```platter
{ 4 , 5 , 6 }
```

Becomes:

```text
t0 = allocate array 3
t0[0] = 4
t0[1] = 5
t0[2] = 6
```

What the code does:

- allocates a temporary runtime array
- lowers each element in order
- writes each element into the newly allocated array
- returns the temporary array name so the caller can assign or pass it onward

### Table Literal

A table literal becomes a temporary allocated table:

```platter
{ x : 1 , y : 2 }
```

Becomes:

```text
t0 = allocate table table_literal
t0.x = 1
t0.y = 2
```

What the code does:

- allocates a temporary runtime table object
- lowers each field value
- emits one field assignment per field
- returns the temporary table name

---

## How TAC and Quadruples Stay in Sync

The generator emits both formats at every lowering step.

### Example: Binary Op

```python
self.emit_tac(TACBinaryOp(result_temp, left_temp, node.operator, right_temp))
self.emit_quad(node.operator, left_temp, right_temp, result_temp)
```

### Result

TAC:

```text
t3 = a + b
```

Quadruple:

```text
(+, a, b, t3)
```

This design means:

- one AST traversal produces both outputs
- both outputs describe the same computation order
- formatting and optimization can choose whichever form is more convenient

---

## End-to-End Example

### Source

```platter
piece add ( piece of a , piece of b ) :
    serve a + b ;

start ( ) :
    piece of x = 2 ;
    piece of y = 3 ;
    piece of z = add ( x , y ) ;
```

### Step 1: Emit Recipe

```text
begin_func add
a = p0
b = p1
t0 = a + b
return t0
return
end_func add
```

### Step 2: Emit Start

```text
begin_func start
x = 2
y = 3
param x
param y
t1 = call add, 2
z = t1
end_func start
```

### Matching Quadruples

```text
(begin_func, add, -, -)
(=, p0, -, a)
(=, p1, -, b)
(+, a, b, t0)
(return, t0, -, -)
(return, -, -, -)
(end_func, add, -, -)
(begin_func, start, -, -)
(=, 2, -, x)
(=, 3, -, y)
(param, x, -, -)
(param, y, -, -)
(call, add, 2, t1)
(=, t1, -, z)
(end_func, start, -, -)
```

---

## Integration with the Rest of the Compiler

### In `main.py`

After semantic analysis succeeds:

```python
ir_gen = IRGenerator()
tac_instructions, quad_table = ir_gen.generate(ast)
```

Then the app:

1. formats TAC for display
2. runs optimization passes
3. executes optimized TAC with `TACInterpreter`

### Optimization Stage

IR is passed into:

- `OptimizerManager`
- constant folding
- algebraic simplification
- propagation
- dead code elimination

### Execution Stage

The interpreter reads TAC directly:

**File:** `interpreter/ir_interpreter.py`

Important runtime behavior:

- labels are pre-indexed
- recipe bodies are skipped during top-level scan until called
- `start` runs inline as the program entry
- `param` instructions push arguments before `call`
- arrays and tables are executed as Python lists and dictionaries

---

## Common Lowering Patterns

| Source Construct | Typical IR Shape |
|------------------|------------------|
| variable init | evaluate expression, then assign |
| binary expression | evaluate operands, emit temp result |
| recipe call | `param ...`, then `call` |
| `check` | `ifFalse`, branch labels, end label |
| `repeat` | start label, condition jump, body, back edge |
| `pass` | init, start label, condition, body, update, back edge |
| `menu` | compare chain, case labels, shared end label |
| array literal | `allocate array`, indexed writes |
| table literal | `allocate table`, field writes |

---

## File Reference

| Component | File | Responsibility |
|-----------|------|----------------|
| Main IR generator | `intermediate_code/ir_generator.py` | Traverses AST and emits IR |
| TAC instruction set | `intermediate_code/tac.py` | Human-readable instruction objects |
| Quadruple model | `intermediate_code/quadruple.py` | Structured IR tuples |
| Output formatter | `intermediate_code/output_formatter.py` | Text, JSON, HTML display |
| TAC interpreter | `interpreter/ir_interpreter.py` | Executes TAC directly |
| Compiler integration | `main.py` | Calls generator, optimizer, interpreter |

---

## Relationship to the Other Guides

- [LEXER_FLOW_GUIDE.md](./LEXER_FLOW_GUIDE.md) explains how source code is tokenized before parsing and AST construction.
- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md) explains the source-level grammar and program shapes that exist before AST construction.
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md) explains how source becomes AST.
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md) explains how names and scopes are collected.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how AST meaning is validated.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated AST is lowered into executable intermediate code.

Together, the pipeline is:

```text
Source -> Lexer -> Tokens -> AST -> Symbol Table -> Semantic Validation -> IR -> Optimization/Execution
```
