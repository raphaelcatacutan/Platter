# Platter Compiler: Symbol Table Flow Guide

## Overview

The **symbol table** is the **semantic database** that tracks all named entities in your program. It answers three core questions during compilation:

1. **Is this symbol declared?** (scope checking)
2. **What type is this symbol?** (type information)
3. **Where was this symbol declared?** (scope hierarchy)

```
AST Tree
   ↓
[1] Symbol Table Building (Walk AST, collect declarations)
   ↓
Symbol Table (nested scopes, symbol registry)
   ↓
[2] Semantic Passes Reference Symbol Table (validate usage)
   ↓
Annotated AST + Error List
   ↓
[3] IR Generator Queries Symbol Table (for type info during codegen)
   ↓
TAC Instructions
```

---

## Core Data Structures

### 1. TypeInfo — Type Representation

```python
class TypeInfo:
    base_type: str              # "piece", "sip", "chars", "flag", or table name
    dimensions: int             # Array dimensions (e.g., 2 for [][])
    table_fields: Dict[str, TypeInfo]  # If is_table=True, field types
    is_table: bool              # True if this is a table type reference
```

**Examples:**

```
piece                   → TypeInfo("piece", 0)
piece []                → TypeInfo("piece", 1)
piece [][]              → TypeInfo("piece", 2)

Point (table type)      → TypeInfo("Point", 0, 
                           {"x": TypeInfo("piece", 0), 
                            "y": TypeInfo("piece", 0)})

chars [] (chars array)  → TypeInfo("chars", 1)
```

### 2. SymbolKind — What Type of Symbol

```python
class SymbolKind(Enum):
    VARIABLE = "ingredient"     # Global/local variables
    PARAMETER = "spice"          # Function parameters
    FUNCTION = "recipe"          # Functions/recipes
    TABLE_TYPE = "table_type"    # Type definitions
    FIELD = "field"              # Table fields
```

### 3. Symbol — A Single Named Entity

```python
class Symbol:
    name: str                   # "x", "double", "Point"
    kind: SymbolKind            # VARIABLE, FUNCTION, etc.
    type_info: TypeInfo         # Type of this symbol
    scope_level: int            # 0=global, 1+=nested
    declaration_node: ASTNode   # Pointer to declaration in AST
    declared_scope: Scope       # Scope where declared
    
    accessed_in_scopes: List[str]  # Tracks where this symbol is USED
    value: str                  # Computed default value (for display)
```

**Example:**
```python
Symbol(
    name="count",
    kind=SymbolKind.VARIABLE,
    type_info=TypeInfo("piece", 0),
    scope_level=0,
    declared_scope=global_scope,
    accessed_in_scopes=["start_platter", "recipe_process"],
    value="0"
)
```

### 4. Scope — Lexical Scope Container

```python
class Scope:
    name: str                   # "global", "recipe_double", "check_1", etc.
    level: int                  # 0=global, 1+=nested
    parent: Optional[Scope]     # Parent scope (or None if global)
    
    symbols: Dict[str, Symbol]  # Symbols declared in THIS scope
    children: List[Scope]       # Child scopes (nested blocks)
    table_types_in_use: set     # Table type names referenced here
```

**Scope Hierarchy Example:**

```
Scope("global", level=0)
  ├─ symbols: {x: Symbol(...), double: Symbol(...)}
  ├─ children:
  │   ├─ Scope("recipe_double", level=1)
  │   │   ├─ symbols: {n: Symbol(param), result: Symbol(...)}
  │   │   └─ children: [Scope("check_1", level=2), ...]
  │   └─ Scope("start_platter", level=1)
  │       └─ symbols: {y: Symbol(...)}
  │           children: [...]
```

### 5. SymbolTable — The Master Registry

```python
class SymbolTable:
    global_scope: Scope         # Root of scope tree
    current_scope: Scope        # Active scope during traversal
    
    table_types: Dict[str, TypeInfo]  # All table prototypes
    builtin_recipes: Dict[str, List[Symbol]]  # Built-ins (supports overloading)
    undeclared_symbols: Dict[str, Symbol]  # Symbols used but never declared
    
    current_function: Optional[Symbol]  # Current function being processed
    in_loop: int                # Loop nesting depth (for stop/next validation)
```

---

## Phase 1: Symbol Table Building

### Entry Point

**File:** `symbol_table_builder.py`  
**Class:** `SymbolTableBuilder`  
**Main method:** `build(ast_root)` (line 105)

### Code-Level Flow Inside `SymbolTableBuilder`

When reading the builder code, the control flow is:

```text
build()
   ->
_gather_type_definitions()
   ->
_process_global_declarations()
   ->
_process_function_declarations()
   ->
_process_platter(start)
```

What this code does:

1. creates the scope tree in one forward walk
2. registers table types before declarations that may depend on them
3. registers recipe names before recipe bodies
4. enters and exits scopes explicitly as the AST walk descends into blocks
5. leaves behind one finished symbol table for all later semantic work

### Build Process: 4 Passes

#### Pass 0: Register Built-in Recipes

```python
def _register_builtin_recipes(self):
    # Called in __init__
    for recipe_name, signatures in BUILTIN_RECIPES.items():
        for signature in signatures:
            # Create Symbol for each overload
            symbol = Symbol(recipe_name, FUNCTION, ...)
            self.symbol_table.register_builtin_recipe(recipe_name, symbol)
```

**Result:** `SymbolTable.builtin_recipes` populated with ~50 built-in functions.

What this code does:

- preloads overloadable built-in recipes into a separate registry
- keeps them available for lookup even though they are not user-defined global symbols
- makes later function and type checks treat built-ins as always known

#### Pass 1: Gather Type Definitions

```python
def _gather_type_definitions(self, program: Program):
    for decl in program.global_decl:
        if isinstance(decl, TablePrototype):
            self._process_table_prototype(decl)
```

**What happens:**
- Walk `Program.global_decl` for table prototypes (e.g., `prepare table Point with ...`)
- Extract field names and types
- Check for forward references (fields can't reference undefined table types)
- Register in `SymbolTable.table_types` dictionary
- Define symbol in `global_scope` with kind=TABLE_TYPE

What this code does:

- turns table syntax into `TypeInfo` objects
- stores those type objects both in the type registry and as symbols
- rejects duplicate fields, recursive self-fields, and illegal forward references during collection

**Example:**
```python
# Source:  prepare table Point with piece of x , piece of y ;

# Creates:
Symbol(
    name="Point",
    kind=TABLE_TYPE,
    type_info=TypeInfo("Point", 0, {
        "x": TypeInfo("piece", 0),
        "y": TypeInfo("piece", 0)
    })
)
```

#### Pass 2: Process Global Declarations

```python
def _process_global_declarations(self, program: Program):
    for decl in program.global_decl:
        if isinstance(decl, IngrDecl):
            self._process_var_decl(decl)
        elif isinstance(decl, ArrayDecl):
            self._process_array_decl(decl)
        elif isinstance(decl, TableDecl):
            self._process_table_decl(decl)
```

**What happens:**
- Process each global variable/array/table declaration
- For each declaration:
  - Extract type information (data_type, dimensions)
  - **Track usage in init expressions** (before defining symbol, to catch forward refs)
  - Call `SymbolTable.define_symbol()` in `global_scope`
  - Compute default value for display

What this code does:

- lowers AST declaration metadata into `Symbol` objects
- scans initializer expressions before inserting the symbol, so use-before-declaration can still be detected later
- keeps display-oriented default values on the symbol for debugging and reporting

**Example:**
```python
# Source: piece of x = 5 ;

# Produces:
Symbol(
    name="x",
    kind=VARIABLE,
    type_info=TypeInfo("piece", 0),
    declared_scope=global_scope,
    value="5"
)
```

#### Pass 3: Process Function Declarations (Two-Pass)

**3a. First Pass — Register Signatures:**

```python
def _register_recipe_signature(self, node: RecipeDecl):
    # Check not shadowing built-in
    if self.symbol_table.is_builtin_recipe(node.name):
        error(f"Cannot redefine built-in recipe '{node.name}'")
        return
    
    # Create function symbol (return type, no parameters yet)
    recipe_symbol = Symbol(
        name=node.name,
        kind=FUNCTION,
        type_info=TypeInfo(node.return_type, node.return_dims),
        scope_level=0,
        declared_scope=global_scope
    )
    
    # Define in global scope
    self.symbol_table.global_scope.define(recipe_symbol)
```

**Why two passes?** Functions can call each other recursively. First pass ensures all function names exist before processing bodies.

What this code does:

- separates name registration from body traversal
- allows recursive and mutually recursive recipe references
- ensures parameters and local declarations are added only after the enclosing recipe symbol already exists

**3b. Second Pass — Process Bodies:**

```python
def _process_recipe_body(self, node: RecipeDecl):
    recipe_symbol = self.symbol_table.lookup_symbol(node.name)
    if not recipe_symbol:
        return  # Skip if registration failed
    
    # Enter recipe scope
    self.symbol_table.enter_scope(f"recipe_{node.name}")
    self.symbol_table.current_function = recipe_symbol
    
    # Process parameters (spices)
    for spice in node.params:
        self._process_param_decl(spice)
    
    # Process body (block with local declarations)
    if node.body:
        self._process_platter(node.body)
    
    # Exit recipe scope
    self.symbol_table.current_function = None
    self.symbol_table.exit_scope()
```

**What happens:**
- Enter new scope: `Scope("recipe_double", level=1, parent=global_scope)`
- Register parameters as symbols in recipe scope
- Walk body statements/declarations, creating scopes for nested blocks
- Exit scope, return to parent

**Scope Stack Example (during body processing):**

```
Original:        During processing body:          After exit:
global           → global                         → global
                   ├─ recipe_double  (current)       (current goes back here)
                   │  ├─ check_1    (if-statement)
                   │  │  └─ (local vars here)
                   │  └─ repeat_1   (while-loop)
                   │     └─ (local vars here)
```

### Symbol Registry After Build: Example

For this Platter program:

```
prepare table Point with piece of x , piece of y ;

piece of globalVar = 10 ;

piece double ( piece of n ) :
    piece of result = n * 2 ;
    serve result ;

start ( ) :
    piece of localVar = double ( globalVar ) ;
```

**Resulting SymbolTable:**

```
SymbolTable:
  table_types:
    "Point" → TypeInfo("Point", {x: piece, y: piece})
  
  global_scope (level=0):
    symbols:
      "Point" → Symbol(TABLE_TYPE, ...)
      "globalVar" → Symbol(VARIABLE, piece, value="10")
      "double" → Symbol(FUNCTION, piece)
    
    children:
      [0] Scope("recipe_double", level=1):
          symbols:
            "n" → Symbol(PARAMETER, piece)
            "result" → Symbol(VARIABLE, piece, value="0")
          children: []
      
      [1] Scope("start_platter", level=1):
          symbols:
            "localVar" → Symbol(VARIABLE, piece, value="0")
          children: []
  
  undeclared_symbols: {}
  builtin_recipes:
    "bill" → [Symbol(FUNCTION, ...), ...]  # all overloads
    "take" → [Symbol(FUNCTION, ...)]
    ... (50+ built-ins)
```

---

## Phase 2: Scope Checking (First Semantic Pass)

### Entry Point

**File:** `semantic_passes/scope_checker.py`  
**Class:** `ScopeChecker`  
**Method:** `check(ast_root)`

### What It Does

Walks the AST and validates every **symbol access** against the symbol table:

```python
def visit_identifier(self, node: Identifier):
    # When we encounter: x or double(5)
    symbol = self.symbol_table.lookup_symbol(node.name)
    
    if not symbol:
        # Not found in current scope or parents
        error(f"Undefined symbol '{node.name}'")
        # Register as undeclared (for later display)
        self.symbol_table.undeclared_symbols[node.name] = Symbol(...)
    else:
        # Track usage: record that this symbol was accessed here
        symbol.add_usage(self.current_scope.name, symbol.declared_scope.name)
```

### Key Checks

| Check | Example |
|-------|---------|
| **Undefined symbols** | `piece of x = y;` where `y` not declared → ERROR |
| **Duplicate definitions** | Two `piece of x;` in same scope → ERROR |
| **Shadowing detection** | Local `x` hides global `x` (allowed, warns) |
| **Forward references** | `piece of x = y;` where `y` declared later → ERROR |

### Usage Tracking Example

**Source:**
```
piece of x = 5 ;

piece double ( piece of n ) :
    piece of result = x + n * 2 ;
    serve result ;

start ( ) :
    piece of y = double ( x ) ;
```

**After scope checking:**
```
Symbol("x", VARIABLE):
    accessed_in_scopes = ["recipe_double", "start_platter"]
    # x is used in two places outside its declaration
```

---

## Phase 3: Type Checking (Second Semantic Pass)

### Entry Point

**File:** `semantic_passes/type_checker.py`  
**Class:** `TypeChecker`

### What It Does

Validates **type compatibility** in operations by querying symbol table for types:

```python
def visit_binary_op(self, node: BinaryOp):
    left_type = self.infer_type(node.left)    # Look up type from symbol table
    right_type = self.infer_type(node.right)
    
    # Check compatibility
    if not left_type.is_compatible_with(right_type):
        error(f"Type mismatch: {left_type} + {right_type}")
```

### Type Compatibility Rules

```python
"piece" + "piece"      ✓ OK
"piece" + "sip"        ✓ OK (numeric promotion)
"piece" + "chars"      ✗ ERROR (incompatible)
"piece" + "piece[]"    ✗ ERROR (can't add scalar + array)
```

### Type Inference via Symbol Table

When checking `x * 2`:

```python
def infer_type(node):
    if isinstance(node, Identifier):
        symbol = symbol_table.lookup_symbol(node.name)
        return symbol.type_info  # ← Query symbol table
    elif isinstance(node, Literal):
        return TypeInfo(node.data_type, 0)
    elif isinstance(node, BinaryOp):
        left = infer_type(node.left)
        right = infer_type(node.right)
        return resulting_type(node.operator, left, right)
```

---

## Phase 4: Usage in IR Generation

### Symbol Table Queries During Codegen

The IR generator **doesn't validate**; it just **generates code** using symbol table for type information:

```python
class IRGenerator:
    def visit_assignment(self, node: Assignment):
        # Look up symbol to get type
        symbol = self.symbol_table.lookup_symbol(node.target.name)
        
        # Use type info to generate correct IR
        if symbol.type_info.is_table:
            # Generate table assignment IR
            self.emit_tac(TACTableAssign(...))
        elif symbol.type_info.dimensions > 0:
            # Generate array assignment IR
            self.emit_tac(TACArrayAssign(...))
        else:
            # Generate scalar assignment IR
            self.emit_tac(TACAssignment(...))
```

### Scope Navigation During Codegen

```python
def visit_recipe_decl(self, node: RecipeDecl):
    # Enter the recipe's scope to see its local variables
    self.symbol_table.navigate_to_scope(f"recipe_{node.name}")
    
    # Now generate code for locals and statements
    for local_decl in node.body.local_decls:
        self.visit_declaration(local_decl)
    
    # When done, navigate back (but IR gen is usually linear, no explicit return)
```

---

## Symbol Table Output & Display

### 1. Compact Format

**File:** `symbol_table_output.py`  
**Function:** `format_symbol_table_compact(symbol_table, error_handler)`

Displays the entire symbol table as a nice ASCII table:

```
╔════════════════════════════════════════════╗
║      BUILT-IN RECIPES (OVERLOADABLE)       ║
╠════════════════════════════════════════════╣
│ bill      │ #1 │ (chars)         │ piece   │
│ bill      │ #2 │ (piece)         │ piece   │
│ take      │ #1 │ ()              │ chars   │
│ pow       │ #1 │ (piece, piece)  │ sip     │
│ ...       │    │                 │         │
└────────────────────────────────────────────┘

╔════════════════════════════════════════════╗
║       USER-DEFINED SYMBOLS                 ║
╠════════════════════════════════════════════╣
│ ID        │ Type      │ Declared  │ Value  │
├───────────┼───────────┼───────────┼────────┤
│ x         │ piece     │ global    │ 10     │
│ double    │ piece     │ global    │ 0      │
│ n         │ piece     │ recipe_.. │ -      │
│ result    │ piece     │ recipe_.. │ 0      │
│ y         │ piece     │ start_... │ 0      │
└───────────┴───────────┴───────────┴────────┘

STATISTICS:
  Total Symbols: 5
  Variables: 3
  Functions: 1
  Parameters: 1
```

### 2. JSON Format

**Function:** `ASTReader.to_json()`

```json
{
  "node_type": "SymbolTable",
  "global_scope": {
    "name": "global",
    "level": 0,
    "symbols": {
      "x": {
        "name": "x",
        "kind": "ingredient",
        "type_info": {
          "base_type": "piece",
          "dimensions": 0,
          "is_table": false
        },
        "value": "10"
      }
    }
  }
}
```

### 3. Console Table Format

**Function:** `format_symbol_table_for_console(symbol_table)`

Returns list of dicts for JavaScript `console.table()`:

```python
[
  {
    'ID': 'x',
    'Type': 'piece',
    'Declared': 'global',
    'Accessed': ['recipe_double', 'start_platter'],
    'Value': '10',
    'Kind': 'ingredient'
  },
  ...
]
```

---

## Complete Example Walkthrough

### Source Program

```
prepare table Point with piece of x , piece of y ;

piece of count = 0 ;

piece increment ( piece of n ) :
    piece of result = n + 1 ;
    serve result ;

start ( ) :
    piece of p = increment ( count ) ;
```

### Step 1: Type Definitions Pass

```
TablePrototype("Point")
  fields: [x: piece, y: piece]

→ SymbolTable.table_types["Point"] = TypeInfo(...)
→ SymbolTable.global_scope.symbols["Point"] = Symbol(TABLE_TYPE, ...)
```

### Step 2: Global Declarations Pass

```
IngrDecl("piece", "count", Literal(0))

→ SymbolTable.global_scope.symbols["count"] = Symbol(
    name="count",
    kind=VARIABLE,
    type_info=TypeInfo("piece", 0),
    value="0"
)
```

### Step 3: Recipe Signature Pass

```
RecipeDecl("piece", "increment", [ParamDecl("piece", "n")], body)

→ SymbolTable.global_scope.symbols["increment"] = Symbol(
    name="increment",
    kind=FUNCTION,
    type_info=TypeInfo("piece", 0)
)
```

### Step 4: Recipe Body Pass

```
enter_scope("recipe_increment")    # Push new scope
  ↓
ParamDecl("piece", "n")
  → define_symbol("n", PARAMETER, TypeInfo("piece", 0))

IngrDecl("piece", "result", ...)
  → define_symbol("result", VARIABLE, TypeInfo("piece", 0))

ServeStatement(BinaryOp(Identifier("n"), "+", Literal(1)))
  → Query symbol_table.lookup_symbol("n") → finds it in recipe_increment scope

exit_scope()    # Pop back to global
```

### Step 5: Start Body Pass

```
enter_scope("start_platter")
  ↓
IngrDecl("piece", "p", RecipeCall("increment", [Identifier("count")]))
  → define_symbol("p", VARIABLE, TypeInfo("piece", 0))
  → Query lookup_symbol("increment") → found (global)
  → Query lookup_symbol("count") → found (global)

exit_scope()
```

### Final Symbol Table State

```
SymbolTable:
  global_scope:
    {
      "Point": Symbol(TABLE_TYPE, Point, fields={x, y}),
      "count": Symbol(VARIABLE, piece, value="0"),
      "increment": Symbol(FUNCTION, piece)
    }
    children:
      [0] Scope("recipe_increment"):
          {
            "n": Symbol(PARAMETER, piece),
            "result": Symbol(VARIABLE, piece, value="0")
          }
      
      [1] Scope("start_platter"):
          {
            "p": Symbol(VARIABLE, piece, value="0")
          }
```

---

## Key Operations Reference

### Lookup a Symbol

```python
symbol = symbol_table.lookup_symbol("x")
# Searches: current scope → parents → built-ins
```

### Check Symbol Type

```python
if symbol.type_info.dimensions > 0:
    # It's an array
if symbol.type_info.is_table:
    # It's a table
```

### Track Symbol Usage

```python
symbol.add_usage(current_scope.name, symbol.declared_scope.name)
# Records that symbol was accessed outside its declaration scope
```

### Enter New Scope

```python
symbol_table.enter_scope("check_1")  # For if/else
symbol_table.enter_scope("repeat_1")  # For loops
symbol_table.enter_scope(f"recipe_{name}")  # For functions
```

### Exit Scope

```python
symbol_table.exit_scope()
# Pops current_scope to parent
```

---

## Common Errors Detected

| Error | Check | Detection |
|-------|-------|-----------|
| Undefined symbol | ScopeChecker | `lookup_symbol()` returns None |
| Duplicate definition | Symbol table | `define_symbol()` returns False |
| Type mismatch | TypeChecker | `is_compatible_with()` fails |
| Shadowing | SymbolTableBuilder | Symbol used in parent before local define |
| Forward reference | SymbolTableBuilder | Table type used before definition |
| Stop outside loop | ControlFlowChecker | `in_loop == 0` when visiting BreakStatement |

---

## File Reference

| Component | File | Key Class/Function |
|-----------|------|---|
| Symbol definition | `types.py` | `Symbol`, `SymbolKind`, `TypeInfo` |
| Scope management | `types.py` | `Scope` |
| Symbol table | `symbol_table.py` | `SymbolTable` |
| Builder | `symbol_table_builder.py` | `SymbolTableBuilder.build()` |
| Scope checking | `semantic_passes/scope_checker.py` | `ScopeChecker` |
| Type checking | `semantic_passes/type_checker.py` | `TypeChecker` |
| Display | `symbol_table_output.py` | `format_symbol_table_compact()` |

---

## Related Guides

- [LEXER_FLOW_GUIDE.md](./LEXER_FLOW_GUIDE.md) explains how the source text becomes tokens before parsing and symbol collection ever begin.
- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md) explains the legal source-level forms that eventually produce the declarations and statements tracked here.
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md) explains how those source forms are turned into AST nodes before symbol collection starts.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how later passes use this symbol table for scope, type, control-flow, and recipe-call validation.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated AST is lowered into executable IR after symbol and semantic work is complete.
