# Symbol Table Console Output - Integration Guide

## Changes Made

The symbol table is now automatically outputted to the browser console when you run semantic analysis in the Platter Compiler web application.

### Files Modified

1. **`src/routes/+page.svelte`**
   - Added symbol table Python files to Pyodide file loading list:
     - `/python/app/semantic_analyzer/__init__.py`
     - `/python/app/semantic_analyzer/symbol_table/__init__.py`
     - `/python/app/semantic_analyzer/symbol_table/symbol_table_builder.py`
   
   - Updated `analyzeSemantic()` function to:
     - Import symbol table functions
     - Build the symbol table after AST creation
     - Print symbol table to console logs using `print_symbol_table()`

### Files Created

2. **`symbol_table_output.py`**
   - Utility functions for formatting symbol table output
   - Includes compact formatting, summaries, and status messages
   - Can be used for custom output formatting

3. **`test_complete_pipeline.py`**
   - Test script that demonstrates the complete pipeline with symbol table

## How to Test

### In the Web Application

1. **Start the application:**
   ```bash
   cd platter-compiler-sveltejs
   npm run dev
   ```

2. **Open your browser** and navigate to the application

3. **Write some Platter code** in the editor, for example:
   ```platter
   table Point {
       ingredient piece x;
       ingredient piece y;
   }
   
   ingredient Point origin;
   ingredient Point[] points;
   
   recipe piece getDistance(Point p1, Point p2) {
       ingredient piece dx = p1.x - p2.x;
       ingredient piece dy = p1.y - p2.y;
       serve dx * dx + dy * dy;
   }
   ```

4. **Click the "Semantic" button**

5. **Open browser console** (F12 or right-click → Inspect → Console)

6. **Look for the symbol table output:**
   ```
   ================================================================================
   Building Symbol Table
   ================================================================================
   
   ============================================================
   Symbol Table
   ============================================================
   Scope(global, level=0, symbols=4)
     ├─ Symbol(Point: Table(Point), kind=table_type, level=0)
     ├─ Symbol(origin: Table(Point), kind=variable, level=0)
     ├─ Symbol(points: Table(Point)[], kind=variable, level=0)
     ├─ Symbol(getDistance: piece, kind=function, level=0)
       Scope(recipe_getDistance_1, level=1, symbols=4)
         ├─ Symbol(p1: Table(Point), kind=parameter, level=1)
         ├─ Symbol(p2: Table(Point), kind=parameter, level=1)
         ├─ Symbol(dx: piece, kind=variable, level=1)
         ├─ Symbol(dy: piece, kind=variable, level=1)
   
   No semantic errors found!
   ============================================================
   ```

## What You'll See in the Console

### 1. AST Analysis (already existed)
```
================================================================================
AST Analysis Complete
================================================================================
[AST tree structure...]
```

### 2. Symbol Table Analysis (NEW!)
```
================================================================================
Building Symbol Table
================================================================================
[Symbol table with scopes, symbols, and type information]
```

### 3. Error Detection (if any)
If there are semantic errors, you'll see them listed with details:
```
Semantic Errors/Warnings:
------------------------------------------------------------
  [ERROR] Undefined variable 'xyz'
  [ERROR] Cannot assign value of type chars to piece
  [WARNING] Loop condition should be of type 'flag', got piece
```

## Console Output Details

The symbol table output includes:

- **Scope hierarchy** - Shows global, function, and block scopes
- **Symbol information** - Name, type, kind (variable/function/table_type/parameter)
- **Type details** - Base type and array dimensions
- **Nested structures** - Tables within tables, arrays of tables
- **Semantic errors** - Type mismatches, undefined variables, etc.

## Example Outputs

### Simple Variables
```
Scope(global, level=0, symbols=2)
  ├─ Symbol(count: piece, kind=variable, level=0)
  ├─ Symbol(price: sip, kind=variable, level=0)
```

### Multidimensional Arrays
```
Scope(global, level=0, symbols=1)
  ├─ Symbol(matrix: piece[][], kind=variable, level=0)
```

### Functions with Parameters
```
Scope(global, level=0, symbols=1)
  ├─ Symbol(add: piece, kind=function, level=0)
    Scope(recipe_add_1, level=1, symbols=2)
      ├─ Symbol(a: piece, kind=parameter, level=1)
      ├─ Symbol(b: piece, kind=parameter, level=1)
```

### Error Detection
```
Semantic Errors/Warnings:
------------------------------------------------------------
  [ERROR] Variable 'myVar' has undefined type 'undefined_type'
  [ERROR] Symbol 'duplicate' already defined in this scope
  [ERROR] Cannot assign value of type chars to piece
  [ERROR] Undefined variable 'undefinedVar'
  [ERROR] Break statement outside of loop
```

## Testing from Command Line

You can also test the complete pipeline from the command line:

```bash
cd platter-compiler-sveltejs/static/python
python -m app.semantic_analyzer.symbol_table.test_complete_pipeline
```

This will run the complete analysis pipeline (lexer → parser → AST → symbol table) on test cases and show all output including the symbol table.

## Utility Functions Available

The `symbol_table_output.py` module provides additional utilities:

```python
from app.semantic_analyzer.symbol_table.symbol_table_output import (
    format_symbol_table_compact,    # Compact text format
    format_symbol_table_summary,    # Dictionary of statistics
    get_symbol_table_status_message, # Short status string
    format_errors_only,             # Only errors/warnings
    get_all_symbols_flat,           # Flat list of symbols
    find_symbol_by_name             # Search for symbol
)
```

## Summary

✅ Symbol table is now automatically displayed in console when running semantic analysis  
✅ Shows complete scope hierarchy with all symbols  
✅ Displays type information including nested structures  
✅ Reports all semantic errors and warnings  
✅ Works alongside existing AST output  

The integration is complete and ready to use!
