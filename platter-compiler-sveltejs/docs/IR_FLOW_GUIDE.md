# Platter Compiler: IR Pipeline Flow Guide

## Overview

This guide explains the exact IR pipeline triggered by the `run_ir_pipeline` block in `src/routes/+page.svelte`.

That block does four things in order:

1. generate IR from the AST
2. format the raw IR for display
3. optimize the TAC form
4. execute the optimized TAC with the interpreter

At a high level, the flow is:

```text
Validated AST
   ->
IRGenerator.generate(ast)
   ->
TAC instructions + Quadruple table
   ->
IRFormatter
   ->
printable TAC / Quadruple text
   ->
OptimizerManager(STANDARD).optimize_tac(...)
   ->
optimized TAC
   ->
TACInterpreter.run()
   ->
execution result dict
```

---

## Source of the Flow

The pipeline comes from the `run_ir_pipeline` branch in:

- `platter-compiler-sveltejs/src/routes/+page.svelte`

Inside that block, the app imports and runs these modules dynamically:

- `app.intermediate_code.ir_generator`
- `app.intermediate_code.output_formatter`
- `app.code_optimization.optimizer_manager`
- `app.interpreter.ir_interpreter`

The relevant runtime sequence is:

```python
ir_gen = IRGenerator()
tac_instructions, quad_table = ir_gen.generate(ast)

formatter = IRFormatter()
ir_tac_text = formatter.format_tac_text(tac_instructions)
ir_quads_text = formatter.format_quadruples_text(quad_table)

optimizer = OptimizerManager(OptimizationLevel.STANDARD)
optimized_tac = optimizer.optimize_tac(tac_instructions)
ir_tac_optimized_text = formatter.format_tac_text(optimized_tac)

interpreter = TACInterpreter(optimized_tac)
exec_result = interpreter.run()
```

---

## Stage 1: IR Generation

### Module

- `static/python/app/intermediate_code/ir_generator.py`

### What it receives

- a validated AST

### What it produces

- `tac_instructions`
- `quad_table`

### Main job

This module walks the AST and lowers high-level Platter constructs into two synchronized IR forms:

1. Three Address Code for readable execution steps
2. quadruples for structured analysis

### Output of this stage

After this stage, the compiler already has a flat executable representation of the program, but it is still unoptimized.

For the detailed guide, see:

- [IR_GENERATOR_FLOW_GUIDE.md](./IR_GENERATOR_FLOW_GUIDE.md)

---

## Stage 2: IR Formatting

### Module

- `static/python/app/intermediate_code/output_formatter.py`

### What it receives

- raw TAC instruction objects
- raw quadruple objects

### What it produces

- formatted text for TAC
- formatted text for quadruples

### Main job

This stage does not change program behavior. It only turns internal IR objects into readable output for the UI or console.

In the Svelte pipeline, it formats:

- the original TAC
- the original quadruples
- the optimized TAC

For the detailed guide, see:

- [IR_FORMATTER_FLOW_GUIDE.md](./IR_FORMATTER_FLOW_GUIDE.md)

---

## Stage 3: TAC Optimization

### Module

- `static/python/app/code_optimization/optimizer_manager.py`

### What it receives

- the unoptimized TAC list from `IRGenerator`

### What it produces

- `optimized_tac`

### Main job

This stage applies a configured sequence of optimization passes. In the `+page.svelte` code, the chosen level is:

```python
OptimizationLevel.STANDARD
```

At this level, the manager applies passes such as:

- algebraic simplification
- constant propagation
- copy propagation
- constant folding
- dead code elimination

It repeats passes until no more changes are found or the iteration limit is reached.

For the detailed guide, see:

- [OPTIMIZER_MANAGER_FLOW_GUIDE.md](./OPTIMIZER_MANAGER_FLOW_GUIDE.md)

---

## Stage 4: TAC Interpretation

### Module

- `static/python/app/interpreter/ir_interpreter.py`

### What it receives

- optimized TAC instructions

### What it produces

- a result dictionary with fields such as:
  - `success`
  - `paused`
  - `output`
  - `error`
  - `globals`
  - `exit_message`
  - `terminate_message`

### Main job

This module executes the optimized TAC directly.

It:

- pre-indexes labels for jumps
- pre-indexes function entry points
- skips recipe bodies during top-level scanning
- runs `start` inline as the entry function
- handles `param`, `call`, and `return`
- implements built-in runtime functions like `bill`, `take`, `topiece`, `append`, and `size`

For the detailed guide, see:

- [IR_INTERPRETER_FLOW_GUIDE.md](./IR_INTERPRETER_FLOW_GUIDE.md)

---

## Full Runtime Story

The pipeline in `+page.svelte` is best understood as two parallel purposes:

### 1. Show compiler output

The app prints:

- raw TAC
- raw quadruples
- optimized TAC

This is the compiler-visualization side of the feature.

### 2. Run the compiled program

After optimization, the app immediately constructs:

```python
interpreter = TACInterpreter(optimized_tac)
```

and executes:

```python
exec_result = interpreter.run()
```

This is the runtime side of the feature.

So the code block is not only a compiler step. It is a full mini-pipeline from AST to executable IR.

---

## Result Handling in `+page.svelte`

After `interpreter.run()`, the Svelte-side Python block reads:

- `output`
- `success`
- `error`
- `paused`
- `globals`
- `exit_message`
- `terminate_message`

Then it decides what to print:

- `[Execution OK]` when execution succeeds
- `[Execution Paused - waiting for input]` when `take()` needs more input
- `[Execution Error] ...` when interpretation fails

If program output exists, it prints the captured output text. Otherwise, successful runs print `(no output)`.

---

## Why These Guides Are Split

Each imported file has a different responsibility:

- `ir_generator.py` lowers AST into executable IR
- `output_formatter.py` turns IR into readable display output
- `optimizer_manager.py` improves TAC before execution
- `ir_interpreter.py` executes the optimized TAC

Splitting the documentation makes it easier to explain each layer without mixing compile-time logic with runtime logic.

---

## Guide Map

- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md): top-level pipeline from `+page.svelte`
- [IR_GENERATOR_FLOW_GUIDE.md](./IR_GENERATOR_FLOW_GUIDE.md): AST to TAC and quadruples
- [IR_FORMATTER_FLOW_GUIDE.md](./IR_FORMATTER_FLOW_GUIDE.md): IR display formatting
- [OPTIMIZER_MANAGER_FLOW_GUIDE.md](./OPTIMIZER_MANAGER_FLOW_GUIDE.md): optimization pass orchestration
- [IR_INTERPRETER_FLOW_GUIDE.md](./IR_INTERPRETER_FLOW_GUIDE.md): optimized TAC execution

---

## Relationship to the Rest of the Compiler

This IR pipeline sits after semantic validation:

```text
Source
-> Lexer
-> Parser
-> AST
-> Symbol Table
-> Semantic Analysis
-> IR Generation
-> IR Formatting
-> TAC Optimization
-> IR Interpretation
```

Related docs:

- [LEXER_FLOW_GUIDE.md](./LEXER_FLOW_GUIDE.md)
- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md)
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md)
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md)
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md)
