# Optimizer Manager Flow Guide

## Overview

This guide explains `static/python/app/code_optimization/optimizer_manager.py`.

This file does not define optimization rules itself. Its job is to decide:

- which optimization passes to use
- in what order to run them
- how many times to repeat them
- how to collect optimization statistics

The core class is:

```python
OptimizerManager
```

---

## Role in the Pipeline

In `+page.svelte`, optimization is triggered like this:

```python
optimizer = OptimizerManager(OptimizationLevel.STANDARD)
optimized_tac = optimizer.optimize_tac(tac_instructions)
```

That means the manager receives unoptimized TAC from the generator and returns a cleaner TAC list for the interpreter.

---

## Optimization Levels

The file defines four levels:

- `NONE`
- `BASIC`
- `STANDARD`
- `AGGRESSIVE`

These are plain integer constants in `OptimizationLevel`.

The level determines which passes `_configure_passes()` adds to `self.passes`.

---

## Pass Configuration Flow

`_configure_passes()` is the first important method.

### `NONE`

Adds no passes.

### `BASIC`

Adds:

- `DeadCodeEliminationPass`

### `STANDARD`

Adds this ordered sequence:

1. `AlgebraicSimplificationPass`
2. `ConstantPropagationPass`
3. `CopyPropagationPass`
4. `ConstantFoldingPass`
5. `DeadCodeEliminationPass`

The order is explicitly documented in the file as critical:

- propagation must happen before folding
- otherwise later iterations could create newly foldable expressions that bypass overflow checks

### `AGGRESSIVE`

Adds everything above plus:

- `StrengthReductionPass`
- `UnreachableCodeEliminationPass`

---

## TAC Optimization Flow

`optimize_tac(instructions)` is the main method used by your Svelte pipeline.

Its flow is:

```text
input TAC
   ->
for each iteration
   ->
run each configured pass in order
   ->
sum pass changes
   ->
stop when an iteration makes zero changes
   ->
return optimized TAC
```

More concretely, it does this:

1. exits early if the optimization level is `NONE`
2. starts with `optimized = instructions`
3. repeats for up to `self.max_iterations`
4. lets each pass transform the current TAC list
5. reads `pass_obj.changes_made` after each pass
6. records per-pass statistics
7. stops when an entire iteration makes no changes

This is a fixed-point optimizer design.

---

## Statistics Flow

The manager tracks stats in `self.stats`.

For each pass, it records:

- total `changes`
- total `applications`

After optimization it also stores:

- `total_iterations`
- `total_changes`
- `original_size`
- `optimized_size`

That is why the manager can later print a summary without rerunning the passes.

---

## Quadruple Optimization Flow

`optimize_quads(quad_table)` mirrors the TAC flow, but it calls each pass's `optimize_quads(...)` method instead.

Even though your current `+page.svelte` block only optimizes TAC, the manager is designed to support both IR forms.

---

## Supporting Methods

### `add_pass(pass_obj)`

Lets you append a custom pass manually.

### `get_stats()`

Returns the accumulated statistics dictionary.

### `print_stats()`

Prints a formatted report including:

- optimization level name
- iteration count
- total changes
- code-size reduction
- per-pass details

### `_get_level_name()`

Maps numeric levels to human-readable names like `Standard (O2)`.

### `reset_stats()`

Clears old statistics so TAC and quadruple runs can be measured separately.

---

## Convenience Function

The module also exposes:

```python
optimize_ir(instructions, quad_table, level, verbose)
```

That helper:

1. creates an `OptimizerManager`
2. optimizes TAC
3. stores TAC stats
4. resets stats
5. optimizes quadruples
6. optionally prints both reports
7. returns both optimized outputs plus the stats bundle

This is useful for demos and tooling, even if the Svelte route currently only needs optimized TAC.

---

## Mental Model

The simplest way to think about `optimizer_manager.py` is:

- passes know how to optimize
- the manager knows when, how often, and in what order to run them

So this file is the coordinator for optimization, not the place where the optimization rules themselves are implemented.
