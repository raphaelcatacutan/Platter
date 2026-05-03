# IR Formatter Flow Guide

## Overview

This guide explains `static/python/app/intermediate_code/output_formatter.py`.

Unlike the generator, optimizer, and interpreter, this module does not change program meaning. Its job is presentation.

It converts internal IR objects into:

- plain text
- JSON
- HTML
- simple statistics reports

The main class is:

```python
IRFormatter
```

---

## Role in the Pipeline

Inside `+page.svelte`, the formatter is used immediately after IR generation and again after TAC optimization:

```python
formatter = IRFormatter()
ir_tac_text = formatter.format_tac_text(tac_instructions)
ir_quads_text = formatter.format_quadruples_text(quad_table)
ir_tac_optimized_text = formatter.format_tac_text(optimized_tac)
```

So the formatter is the display layer between raw compiler data structures and user-visible output.

---

## Main Methods

### `format_tac_text(instructions)`

Builds a readable numbered listing of TAC instructions.

Flow:

1. print a section header
2. iterate over instructions with indexes
3. convert each instruction with `str(instr)`
4. append a total count footer

This is the method used by the IR pipeline for both raw TAC and optimized TAC.

### `format_quadruples_text(quad_table)`

Builds a fixed-width table with:

- index
- operator
- arg1
- arg2
- result

Missing fields are shown as `-`.

### `format_quadruples_readable(quad_table)`

Uses each quadruple's `to_string()` method instead of a table layout. This is helpful when you want quadruples to read more like TAC.

### `format_both_text(...)`

Concatenates formatted TAC and formatted quadruples into one text payload.

---

## JSON Output Flow

The formatter also has JSON-producing methods.

### `format_tac_json(instructions)`

For each TAC instruction, it creates an object with:

- `index`
- `type`
- `instruction`

Then it conditionally adds extra fields like:

- `result`
- `arg1`
- `arg2`
- `operator`
- `label`

This is driven by `hasattr(...)`, which lets one method handle many TAC instruction subclasses.

### `format_quadruples_json(quad_table)`

Each quadruple becomes:

- `index`
- `operator`
- `arg1`
- `arg2`
- `result`
- `readable`

### `format_both_json(...)`

Wraps both outputs under a shared top-level key:

```json
{
  "intermediate_representation": {
    "three_address_code": [...],
    "quadruples": [...]
  }
}
```

---

## HTML Output Flow

`format_html(...)` generates a standalone HTML document string.

It builds:

1. a small CSS block
2. a TAC table
3. a quadruple table

This method is useful for saved reports or visual inspection outside the terminal or web console.

Important detail:

- TAC rows use `str(instr)`
- quadruple rows use raw fields plus `quad.to_string()`

So the HTML view shows both machine-structured and human-readable forms.

---

## Statistics Flow

`format_statistics(...)` summarizes the IR rather than listing it.

It counts:

- TAC instruction types using `instr.op_type`
- quadruple operators using `quad.operator`

The report includes totals and per-type breakdowns.

This is useful when you want a high-level profile of a program's IR shape instead of the full listing.

---

## Convenience Functions

The module also exposes wrappers outside the class:

- `format_tac(...)`
- `format_quadruples(...)`
- `format_ir(...)`

These functions:

1. create an `IRFormatter`
2. choose output mode
3. return the requested representation

They are lightweight helpers around the same formatting logic.

---

## Mental Model

The easiest way to think about `output_formatter.py` is:

- it never generates IR
- it never optimizes IR
- it never executes IR
- it only reshapes IR data into readable or serializable forms

That separation is why the rest of the pipeline can stay compiler-focused while this file stays UI/report-focused.
