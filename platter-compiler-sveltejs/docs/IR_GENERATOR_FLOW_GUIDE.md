# IR Generator Flow Guide

## Overview

This guide explains how `static/python/app/intermediate_code/ir_generator.py` turns a validated AST into two synchronized intermediate representations:

1. TAC instruction objects
2. quadruple records

The core class is:

```python
IRGenerator
```

Its main entry point is:

```python
generate(ast)
```

---

## Main Flow

The generator follows this shape:

```text
generate(ast)
   ->
visit_declaration() / visit_recipe_decl() / visit_platter()
   ->
visit_statement()
   ->
visit_expression()
   ->
emit_tac() + emit_quad()
```

That means the file is a tree-walker that lowers each AST node into flat IR as it goes.

---

## Internal State

The generator keeps a few important counters and contexts:

- `self.tac_instructions`: collected TAC output
- `self.quad_table`: collected quadruple output
- `self.temp_count`: generates temporary names like `t0`, `t1`
- `self.label_count`: generates labels like `else0`, `while_end1`
- `self.current_function`: tracks the recipe currently being emitted
- `self.recipe_names`: used for zero-argument recipe call fallback
- `self.loop_stack`: stores `(continue_label, break_label)`

These are what let the generator preserve control flow and write both IR forms in sync.

---

## Program-Level Entry

`generate(ast)` emits the program in this order:

1. global declarations
2. recipe declarations
3. `start` platter

The high-level structure is:

```python
self.emit_comment("=== Platter Program IR ===")

if ast.global_decl:
    ...

if ast.recipe_decl:
    ...

if ast.start_platter:
    self.emit_tac(TACFunctionBegin("start"))
    ...
    self.emit_tac(TACFunctionEnd("start"))
```

This order matters because global setup must exist before `start` runs, while recipes must already be indexed and available for later calls.

---

## Declaration Flow

### Variable declarations

`visit_var_decl()` handles:

- initialized ingredients
- default values for uninitialized ingredients

Examples of defaults:

- `piece -> 0`
- `sip -> 0.0`
- `chars -> ""`
- `flag -> down`

### Array declarations

`visit_array_decl()` can:

- allocate an array from a literal size inferred from elements
- initialize array slots one by one
- assign from an expression or recipe call result

### Table prototypes

`visit_table_prototype()` emits only a comment because table prototypes are type declarations, not runtime objects.

### Table declarations

`visit_table_decl()`:

1. allocates a table object
2. initializes fields if a table literal exists
3. otherwise can assign from another expression result

---

## Recipe Flow

`visit_recipe_decl()` lowers each recipe into a function region:

```text
begin_func recipeName
param binding
body
return
end_func recipeName
```

Important behaviors:

- the recipe name is stored in `self.current_function`
- a comment like `# Recipe: add` is emitted
- caller arguments are expected as `p0`, `p1`, `p2`
- those positional parameters are rebound to declared parameter names
- a final `return` is always emitted even if the body already contains `serve`

This makes every recipe body structurally consistent for later execution.

---

## Statement Flow

`visit_statement()` dispatches into specific lowering methods.

### Assignment

`visit_assignment()`:

1. lowers the right-hand expression
2. handles simple `=` or compound assignments like `+=`
3. routes final storage through `emit_assignment()`

`emit_assignment()` decides whether the write target is:

- a scalar variable
- an array slot
- a table field

### If / elif / else

`visit_if_statement()` creates:

- an `else` label
- an `endif` label
- one extra label for each `elif`

It lowers the condition first, emits an `ifFalse` jump, then lowers the matching branch blocks in order.

### While loop

`visit_while_loop()` creates:

- `while_start...`
- `while_end...`

It pushes those labels to `loop_stack`, which is why `next` and `stop` work correctly inside nested loops.

### Do-while loop

`visit_do_while_loop()` creates:

- `do_start...`
- `do_continue...`
- `do_end...`

The dedicated continue label is important because `next` should jump to the condition check, not to the top of the body.

### For loop

`visit_for_loop()` emits:

1. initialization
2. loop head label
3. condition test
4. body
5. continue label
6. update step
7. back edge jump
8. end label

### Menu / switch

`visit_switch_statement()`:

1. evaluates the switch expression once
2. compares it against each case value
3. jumps to the matching case label
4. falls back to default or end
5. forces every case to jump to a shared end label

This implementation has no fall-through.

### Serve / stop / next

- `visit_return_statement()` emits `return` or `return value`
- `visit_break_statement()` jumps to the current break label
- `visit_continue_statement()` jumps to the current continue label

---

## Expression Flow

Every expression method returns the name holding the computed result.

That return value can be:

- an existing identifier
- a literal string form
- a newly created temporary such as `t5`

### Binary and unary ops

`visit_binary_op()` and `visit_unary_op()`:

1. lower subexpressions first
2. allocate a fresh temp
3. emit one TAC instruction and one matching quadruple
4. return the temp name

### Identifier and literal

- identifiers are returned directly by name
- literals are returned directly as immediate values
- `chars` literals are forced to stay quoted so the interpreter will not mistake them for variable names

### Array and table access

`visit_array_access()` and `visit_table_access()` emit read instructions that load the accessed value into a temporary.

### Function call

`visit_function_call()`:

1. evaluates arguments left to right
2. emits a `param` instruction for each
3. emits a `call`
4. returns the result temp

### Cast

`visit_cast_expr()` emits `TACCast` plus a matching `cast` quadruple.

### Array and table literals

`visit_array_literal()` and `visit_table_literal()` allocate a temporary runtime object, initialize it, then return its temp name.

---

## Synchronizing TAC and Quadruples

The generator keeps both IR forms aligned by emitting them together.

A binary operation is the clearest example:

```python
self.emit_tac(TACBinaryOp(result_temp, left_temp, node.operator, right_temp))
self.emit_quad(node.operator, left_temp, right_temp, result_temp)
```

This pattern appears throughout the file and is the reason formatted TAC and quadruples describe the same execution order.

---

## Mental Model

The simplest way to read `ir_generator.py` is:

- declarations allocate and initialize storage
- statements create control flow
- expressions compute values into names or temps
- emitters write both output formats immediately

That is the full job of the file.
