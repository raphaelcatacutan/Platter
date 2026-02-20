# Symbol Table for Platter Language

This directory contains the symbol table implementation for the Platter programming language compiler. The symbol table handles semantic analysis including type checking, scoping, and declaration validation.

## Features

### ✅ Complete Semantic Analysis
- **Scoping**: Supports global, function, and block-level scopes with proper nesting
- **Type Checking**: Validates type compatibility in assignments, operations, and function calls
- **Declaration Checking**: Ensures variables are declared before use
- **Duplicate Detection**: Prevents duplicate symbol declarations in the same scope

### ✅ Advanced Type Support
- **Primitive Types**: `piece` (int), `sip` (float), `flag` (bool), `chars` (string)
- **Arrays**: Full support for multidimensional arrays (e.g., `piece[][]`, `sip[][][]`)
- **Tables/Structs**: User-defined table types with nested fields
- **Nested Structures**: Arrays of tables, tables with array fields, tables within tables
- **Type Inference**: Automatically infers expression types during analysis

### ✅ Comprehensive Error Detection
- Undefined type references
- Undefined variable access
- Type mismatches in assignments and operations
- Invalid array indexing
- Invalid table field access
- Break/continue outside loops
- Return statements with wrong types
- Duplicate declarations

## Architecture

### Core Classes

#### `TypeInfo`
Represents type information including base type, array dimensions, and table structure.

```python
# Scalar types
piece_type = TypeInfo("piece", 0)

# Array types
array_type = TypeInfo("piece", 2)  # piece[][]

# Table types with fields
point_fields = {
    "x": TypeInfo("piece", 0),
    "y": TypeInfo("piece", 0)
}
point_type = TypeInfo("Point", 0, point_fields)
```

#### `Symbol`
Represents an entry in the symbol table with name, kind, type, and scope information.

```python
symbol = Symbol(
    name="myVar",
    kind=SymbolKind.VARIABLE,
    type_info=TypeInfo("piece", 0),
    scope_level=0
)
```

#### `Scope`
Represents a lexical scope with parent-child relationships.

```python
global_scope = Scope("global", level=0)
function_scope = Scope("recipe_main", level=1, parent=global_scope)
```

#### `SymbolTable`
Manages the scope stack and provides lookup/definition operations.

```python
symbol_table = SymbolTable()
symbol_table.enter_scope("function")
symbol_table.define_symbol("x", SymbolKind.VARIABLE, TypeInfo("piece", 0))
symbol = symbol_table.lookup_symbol("x")
symbol_table.exit_scope()
```

#### `SymbolTableBuilder`
Traverses the AST and builds the symbol table with semantic checking.

```python
builder = SymbolTableBuilder()
symbol_table = builder.build(ast_root)
```

## Usage

### Basic Usage

```python
from app.semantic_analyzer.ast.ast_parser_program import parse_program
from app.semantic_analyzer.symbol_table import build_symbol_table, print_symbol_table

# Parse source code to AST
ast_root = parse_program(source_code)

# Build symbol table
symbol_table = build_symbol_table(ast_root)

# Check for errors
if symbol_table.has_errors():
    print(symbol_table.get_errors_str())
else:
    print("No semantic errors!")

# Print symbol table (for debugging)
print_symbol_table(symbol_table)
```

### Programmatic Symbol Lookup

```python
# Look up a symbol
symbol = symbol_table.lookup_symbol("myVariable")
if symbol:
    print(f"Found: {symbol.name}, Type: {symbol.type_info}")
    
# Look up a table type
table_type = symbol_table.lookup_table_type("Point")
if table_type:
    print(f"Fields: {table_type.table_fields.keys()}")
```

### Type Checking

```python
# Check type compatibility
type1 = TypeInfo("piece", 0)
type2 = TypeInfo("sip", 0)

if type1.is_compatible_with(type2):
    print("Types are compatible")

# Get element type of array
array_type = TypeInfo("piece", 2)  # piece[][]
element_type = array_type.get_element_type()  # piece[]

# Get field type from table
point_type = symbol_table.lookup_table_type("Point")
x_type = point_type.get_field_type("x")
```

## Examples

### Example 1: Simple Variable Declaration

```platter
ingredient piece myVar = 5;
```

Symbol Table:
```
Scope(global, level=0)
  └─ Symbol(myVar: piece, kind=variable, level=0)
```

### Example 2: Nested Structures

```platter
table Point {
    ingredient piece x;
    ingredient piece y;
}

table Rectangle {
    ingredient Point topLeft;
    ingredient Point bottomRight;
}

ingredient Rectangle rect;
```

Symbol Table:
```
Scope(global, level=0)
  ├─ Symbol(Point: Table(Point), kind=table_type)
  ├─ Symbol(Rectangle: Table(Rectangle), kind=table_type)
  └─ Symbol(rect: Table(Rectangle), kind=variable)
```

### Example 3: Multidimensional Arrays

```platter
ingredient piece[][] matrix;
ingredient piece[] row = matrix[0];
ingredient piece element = matrix[0][0];
```

Symbol Table correctly tracks:
- `matrix` as `piece[][]` (2D array)
- `matrix[0]` returns `piece[]` (1D array)
- `matrix[0][0]` returns `piece` (scalar)

### Example 4: Function with Scoping

```platter
ingredient piece globalVar = 10;

recipe void testScope() {
    ingredient piece localVar = 20;
    
    plate {
        ingredient piece innerVar = 30;
        localVar = globalVar + innerVar;  // All visible
    }
}
```

Symbol Table preserves scope hierarchy:
```
Scope(global, level=0)
  ├─ Symbol(globalVar: piece)
  └─ Symbol(testScope: void, kind=function)
      └─ Scope(recipe_testScope, level=1)
          ├─ Symbol(localVar: piece)
          └─ Scope(block, level=2)
              └─ Symbol(innerVar: piece)
```

## Error Detection Examples

### Type Mismatch
```platter
ingredient piece x = "hello";  // ERROR: Cannot assign chars to piece
```

### Undefined Variable
```platter
ingredient piece y = undefinedVar;  // ERROR: Undefined variable
```

### Invalid Field Access
```platter
table Point { ingredient piece x; }
ingredient Point pt;
ingredient piece z = pt.z;  // ERROR: Point has no field 'z'
```

### Break Outside Loop
```platter
recipe void test() {
    stop;  // ERROR: Break statement outside of loop
}
```

## Testing

Run the comprehensive test suite:

```bash
cd platter-compiler-sveltejs/static/python
python -m app.semantic_analyzer.symbol_table.test_symbol_table
```

Tests cover:
- Simple variables and arrays
- Table definitions and instances
- Nested table structures
- Function declarations with parameters
- Scoping rules
- Semantic error detection
- Array and table access
- Multidimensional arrays

## Integration with Compiler Pipeline

```
Source Code
    ↓
Lexer → Tokens
    ↓
Parser → AST
    ↓
Symbol Table Builder → Symbol Table   ← You are here
    ↓
Type Checker (uses symbol table)
    ↓
Code Generator
```

The symbol table is built after parsing and serves as the foundation for:
1. **Type checking** - Validate operations and assignments
2. **Semantic analysis** - Check program semanticslogic
3. **Code generation** - Resolve variable addresses and types
4. **Runtime support** - Provide debugging information

## Advanced Features

### Type Compatibility

The system supports intelligent type compatibility:
- Exact type matches
- Numeric conversions between `piece` and `sip`
- Array dimension matching
- Structural table compatibility

### Nested Access Chains

Correctly handles complex expressions:
```platter
ingredient Person[] people;
ingredient chars name = people[0].address.city;
```

Type inference chain:
- `people` → `Person[]`
- `people[0]` → `Person`
- `people[0].address` → `Address`
- `people[0].address.city` → `chars`

### Scope Tree Visualization

Use `symbol_table.print_scope_tree()` to visualize the complete scope hierarchy with all symbols at each level.

## Future Enhancements

Potential improvements:
- [ ] Function overloading support
- [ ] Generic/template types
- [ ] Constant propagation
- [ ] Dead code detection
- [ ] Control flow analysis
- [ ] Memory lifetime analysis

## Files

- `symbol_table_builder.py` - Main implementation
- `__init__.py` - Package exports
- `test_symbol_table.py` - Comprehensive tests
- `README.md` - This file

## Author

Symbol table implementation for the Platter programming language compiler.
