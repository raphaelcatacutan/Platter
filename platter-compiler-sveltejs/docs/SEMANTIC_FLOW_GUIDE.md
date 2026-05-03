# Platter Compiler: Semantic Flow Guide

## Overview

Semantic analysis is the stage that answers:

1. Is every symbol valid in the scope where it is used?
2. Are values and expressions type-correct?
3. Are control-flow statements used legally?
4. Do recipe calls match their declared spices and serve types?

In Platter, semantic analysis happens after AST construction and is coordinated by `SemanticAnalyzer`.

```
Tokens
   ->
AST Construction
   ->
Program AST
   ->
Symbol Table Building
   ->
Semantic Passes
   ->
Validated AST + Symbol Table + Error List
```

The semantic pipeline is:

```
[1] Build symbol table
   ->
[2] Scope checking
   ->
[3] Type checking
   ->
[4] Control-flow checking
   ->
[5] Recipe-call checking
```

---

## Entry Point

**File:** `platter-compiler-sveltejs/static/python/app/semantic_analyzer/semantic_analyzer.py`  
**Class:** `SemanticAnalyzer`  
**Main method:** `analyze(ast_root)`

### Analyzer Orchestration

```python
def analyze(self, ast_root: Program):
    builder = SymbolTableBuilder()
    builder.symbol_table.error_handler = self.error_handler
    self.symbol_table = builder.build(ast_root)

    self._run_semantic_passes(ast_root)
    return self.symbol_table, self.error_handler
```

### Pass Order

```python
def _run_semantic_passes(self, ast_root: Program):
    ScopeChecker(self.symbol_table, self.error_handler).check(ast_root)
    TypeChecker(self.symbol_table, self.error_handler).check(ast_root)
    ControlFlowChecker(self.symbol_table, self.error_handler).check(ast_root)
    FunctionChecker(self.symbol_table, self.error_handler).check(ast_root)
```

This order matters:

- Scope checking must run before type checking so identifiers and recipes can be resolved first.
- Type checking must run before function-call validation so argument types are available.
- Control-flow checking runs after structural symbol collection so recipe bodies can be analyzed safely.

### Code-Level Flow Inside `SemanticAnalyzer`

When reading `semantic_analyzer.py`, the execution flow is:

```text
analyze()
   ->
SymbolTableBuilder.build()
   ->
ScopeChecker.check()
   ->
TypeChecker.check()
   ->
ControlFlowChecker.check()
   ->
FunctionChecker.check()
```

What this code does:

1. creates one shared `SemanticErrorHandler`
2. attaches that handler to the symbol-building phase
3. builds the symbol table once
4. reuses the same AST and symbol table across every semantic pass
5. accumulates errors in one place instead of stopping after the first failure

---

## Inputs and Outputs

### Input

- A fully built `Program` AST
- Source positions stored on AST nodes (`line`, `column`)

### Output

- `SymbolTable` containing global symbols, nested scopes, table types, and built-in recipes
- `SemanticErrorHandler` containing errors and warnings

### High-Level Result

If semantic analysis succeeds, later compiler stages can assume:

- all referenced identifiers are declared
- types are compatible
- `serve`, `stop`, and `next` appear in valid contexts
- recipe calls match declared signatures

---

## Phase 1: Symbol Table Building

### Entry Point

**File:** `symbol_table/symbol_table_builder.py`  
**Class:** `SymbolTableBuilder`  
**Method:** `build(ast_root)`

### Goal

This phase does not fully validate semantics yet. Its job is to build the semantic environment that later passes depend on.

### What It Builds

- global scope
- nested scopes for recipes and blocks
- symbols for variables, parameters, recipes, and table types
- built-in recipe overload registry
- table type definitions
- forward-reference traces from initializer usage

### Build Sequence

```python
def build(self, ast_root: Program) -> SymbolTable:
    self._gather_type_definitions(ast_root)
    self._process_global_declarations(ast_root)
    self._process_function_declarations(ast_root)

    if ast_root.start_platter:
        self.symbol_table.enter_scope("start_platter")
        self._process_platter(ast_root.start_platter)
        self.symbol_table.exit_scope()
```

What this code does:

- gathers type definitions before value declarations
- processes recipes in two stages so signatures exist before bodies are analyzed
- creates the `start_platter` scope only after global and recipe declarations have been registered
- returns one scope tree that all later semantic passes navigate rather than rebuild

### Important Details

#### 1. Built-in recipes are registered first

Built-ins are stored separately in `SymbolTable.builtin_recipes` and support overloads.

#### 2. Table prototypes are gathered before other declarations

This allows later declarations to query `lookup_table_type(...)`.

#### 3. Recipe declarations use two passes

- Pass 1 registers recipe signatures in global scope.
- Pass 2 enters each recipe scope and processes spices plus body contents.

This allows recursive and mutually recursive calls to resolve by name.

#### 4. Initializers are scanned before the declared symbol is inserted

Example:

```platter
piece of x = y ;
piece of y = 5 ;
```

The builder tracks usage inside `x`'s initializer before defining `x`, which helps later passes detect `y` as a forward reference.

#### 5. Scope names are created once and reused later

The builder creates names such as:

- `global`
- `start_platter`
- `double` for recipe scope of `recipe_double`
- `check_1`, `alt_1`, `instead_1`
- `repeat_1`, `pass_1`, `choice_1`, `usual_1`

Later semantic passes navigate this exact scope tree rather than rebuilding it.

---

## Core Semantic Data Structures

### TypeInfo

**File:** `symbol_table/types.py`

Represents the semantic type of a value:

```python
TypeInfo(
    base_type="piece",
    dimensions=0,
    table_fields=None
)
```

It supports:

- primitive types: `piece`, `sip`, `chars`, `flag`
- arrays via `dimensions`
- table instances via `table_fields`
- compatibility checks with `is_exact_match()` and `is_compatible_with()`

### Symbol

Stores one named entity:

```python
Symbol(
    name="count",
    kind=SymbolKind.VARIABLE,
    type_info=TypeInfo("piece", 0),
    scope_level=0,
    declaration_node=<IngrDecl>,
    declared_scope=<global>
)
```

### Scope

Stores declarations for one lexical region:

```python
Scope(
    name="repeat_1",
    level=2,
    parent=<recipe scope>
)
```

### SymbolTable

The central semantic registry contains:

- `global_scope`
- `current_scope`
- `table_types`
- `builtin_recipes`
- `undeclared_symbols`
- `current_function`

---

## Phase 2: Scope Checking

### Entry Point

**File:** `semantic_passes/scope_checker.py`  
**Class:** `ScopeChecker`  
**Method:** `check(ast_root)`

### Goal

Ensure every identifier, recipe name, and declared type is valid in the current lexical context.

### What It Checks

- undefined ingredients
- undefined recipes
- undefined types
- invalid array dimensions
- forward references discovered during symbol table building
- unused ingredients

### How It Works

The checker walks the AST and navigates into the already-built scope tree using `navigate_to_scope(...)`.

Example for a recipe:

```python
if self.symbol_table.navigate_to_scope(node.name):
    self._check_platter(node.body)
    self.symbol_table.exit_scope()
```

What this code does:

- replays the same structural walk that the symbol-table builder used
- moves through existing scopes by name
- validates identifier use without mutating the scope tree
- records warnings like unused ingredients while it walks

### Identifier Resolution

```python
symbol = self.symbol_table.lookup_symbol(expr.name)
if not symbol:
    error("Undefined ingredient ...")
```

Lookup order is:

1. current scope
2. parent scopes
3. built-in recipe registry for recipe lookups

### Forward Reference Detection

If a symbol was used before its declaration, the builder leaves a trace in `undeclared_symbols`. The scope checker then confirms whether that name was eventually declared somewhere and reports it as a semantic error.

### Example

```platter
piece of a = b ;
piece of b = 10 ;
```

Result:

- `b` is accessed while undefined in `a`'s initializer
- later `b` is declared
- scope checker reports it as a use-before-declaration error

---

## Phase 3: Type Checking

### Entry Point

**File:** `semantic_passes/type_checker.py`  
**Class:** `TypeChecker`  
**Method:** `check(ast_root)`

### Goal

Verify that declarations, assignments, expressions, conditions, table literals, array literals, and serve statements use compatible types.

### Major Checks

- declaration initializer matches declared type
- assignment target matches value type
- condition expressions are `flag`
- `serve` expression matches recipe return type
- array and table accesses are type-valid
- recipe calls produce the correct resulting type when used in expressions
- table literal fields exist and match field types

### Exact Match vs Compatible Match

The type system uses two comparison modes:

- `is_exact_match()`
  - used for assignments, declarations, serve statements, and user recipe flavors
  - `piece` is not exactly equal to `sip`
- `is_compatible_with()`
  - used in places where numeric compatibility or table structural compatibility is acceptable
  - `piece` and `sip` are compatible

### Expression Type Inference

The checker infers types recursively:

```python
Literal       -> TypeInfo(value_type, 0)
Identifier    -> symbol.type_info
ArrayAccess   -> array_type.get_element_type()
TableAccess   -> table_type.get_field_type(field)
RecipeCall    -> recipe return type
CastExpr      -> TypeInfo(target_type, dims)
```

What this code does:

- asks each expression node what type it produces
- uses recursive descent over AST expressions, not token text
- returns `TypeInfo` objects that later checks compare for exact match or compatibility

### Special Cases in the Implementation

#### Empty array literals

An empty `ArrayLiteral([])` is allowed for any array declaration or assignment target with array dimensions.

#### Table literal validation

Table literals are checked field by field:

- each field must exist in the table prototype
- each field value must match the expected field type

#### Assignment to recipes is rejected

```platter
double = 5 ;
```

This is invalid because recipes are not assignable symbols.

#### Conditions must be `flag`

The following constructs require a `flag` condition:

- `check`
- `repeat`
- `order repeat`
- `pass`

### Example

```platter
piece of x = 1 ;
sip of y = x + 2.5 ;
check ( y ) :
    ...
```

Results:

- `x + 2.5` is numeric and valid
- `check ( y )` is invalid because `y` is `sip`, not `flag`

---

## Phase 4: Control-Flow Checking

### Entry Point

**File:** `semantic_passes/control_flow_checker.py`  
**Class:** `ControlFlowChecker`  
**Method:** `check(ast_root)`

### Goal

Validate whether control-flow statements appear in legal contexts and whether recipes guarantee a `serve` when required.

### What It Checks

- `stop` appears only inside loops or `menu`
- `next` appears only inside loops
- `serve` appears only inside a recipe context
- non-`void` recipes guarantee a `serve` on all code paths
- unreachable code after `serve`

What this code does:

- walks recipe and `start` bodies statement by statement
- tracks whether the current location is inside a loop-like construct
- tracks whether all branches guarantee a `serve`
- issues warnings for unreachable statements after an unconditional `serve`

### Loop/Menu Tracking

The checker increments `in_loop` for:

- `repeat`
- `order repeat`
- `pass`
- `menu`

That means `stop` is allowed inside `menu`, while `next` is only meaningful inside loop-like constructs that keep `in_loop > 0`.

### Guaranteed Serve Analysis

For non-`void` recipes, `_block_has_serve(...)` checks whether all paths definitely return a value.

A `check` statement only guarantees a `serve` if:

- the `then` block serves
- every `alt` block serves
- the `instead` block exists and serves

### Example

```platter
piece maybeServe ( flag of ok ) :
    check ( ok ) :
        serve 1 ;
```

This fails because there is no guaranteed `serve` when `ok` is false.

---

## Phase 5: Recipe Call Checking

### Entry Point

**File:** `semantic_passes/function_checker.py`  
**Class:** `FunctionChecker`  
**Method:** `check(ast_root)`

### Goal

Validate recipe-call arguments after scopes and types are already known.

### What It Checks

- flavor count matches spice count
- each flavor type matches the expected spice type
- built-in recipes resolve to a compatible overload

What this code does:

- revisits expressions specifically to inspect `RecipeCall` nodes
- separates user-defined recipe checking from built-in overload checking
- uses the symbol table to recover parameter symbols from each recipe scope

### User-Defined Recipe Calls

For user recipes:

- argument count must match exactly
- argument type must satisfy `is_exact_match()`

Example:

```platter
piece addOne ( piece of n ) :
    serve n + 1 ;

start() :
    sip of x = 2.5 ;
    piece of y = addOne ( x ) ;
```

This is invalid because user-defined recipe flavors are checked strictly, not by numeric compatibility.

### Built-in Recipe Calls

Built-ins are more flexible:

- overload resolution uses argument type lists
- scalar built-ins may allow wider compatibility than user-defined recipes
- exact signature is preferred first, then compatible signature

### How Spice Lookup Works

For user-defined recipes, the checker finds the recipe scope in `global_scope.children`, then collects symbols of kind `PARAMETER`.

---

## End-to-End Example

### Source

```platter
prepare table Point with piece of x , piece of y ;

piece add ( piece of a , piece of b ) :
    piece of result = a + b ;
    serve result ;

start ( ) :
    Point of p = { x : 1 , y : 2 } ;
    piece of total = add ( p.x , 3 ) ;
```

### Step 1: AST arrives at semantic analyzer

The parser produces:

- one `TablePrototype`
- one `RecipeDecl`
- one `start_platter`

### Step 2: Symbol table is built

Global scope gets:

- `Point` as `TABLE_TYPE`
- `add` as `FUNCTION`

Recipe scope `add` gets:

- `a` as `PARAMETER`
- `b` as `PARAMETER`
- `result` as `VARIABLE`

Start scope gets:

- `p` as `VARIABLE` of table type `Point`
- `total` as `VARIABLE` of type `piece`

### Step 3: Scope checker validates names

- `Point` exists
- `add` exists
- `p.x` refers to declared `p`

### Step 4: Type checker validates values

- `{ x : 1 , y : 2 }` matches `Point`
- `p.x` is `piece`
- `add(p.x, 3)` returns `piece`
- initialization of `total` is valid

### Step 5: Control-flow checker validates recipe body

- `add` has a guaranteed `serve`

### Step 6: Function checker validates call

- `add` expects 2 flavors
- both arguments are `piece`

### Final Result

Semantic analysis succeeds with:

- valid symbol table
- no semantic errors
- AST ready for later stages

---

## Common Error Categories

| Category | Example |
|----------|---------|
| Undefined symbol | `piece of x = y ;` when `y` does not exist |
| Forward reference | `piece of x = y ; piece of y = 1 ;` |
| Undefined type | `spoon of x ;` where `spoon` is not a primitive or table type |
| Type mismatch | `piece of x = "hello" ;` |
| Invalid condition type | `check ( 5 ) :` |
| Invalid assignment target | assigning to a recipe name |
| Missing serve | non-`void` recipe without guaranteed `serve` |
| Stop/next misuse | `stop ;` outside loop, `next ;` outside loop |
| Flavor mismatch | wrong argument count or type in a recipe call |
| Undefined table field | `{ z : 1 }` for a table with only `x` and `y` |

---

## File Reference

| Component | File | Responsibility |
|-----------|------|----------------|
| Analyzer coordinator | `semantic_analyzer.py` | Runs the full semantic pipeline |
| Symbol table manager | `symbol_table/symbol_table.py` | Scope entry, lookup, type registry |
| Symbol builder | `symbol_table/symbol_table_builder.py` | Collects declarations and builds scopes |
| Core semantic types | `symbol_table/types.py` | `TypeInfo`, `Symbol`, `Scope`, `SymbolKind` |
| Scope checker | `semantic_passes/scope_checker.py` | Name and type existence checks |
| Type checker | `semantic_passes/type_checker.py` | Expression and assignment type validation |
| Control-flow checker | `semantic_passes/control_flow_checker.py` | `serve`, `stop`, `next`, reachability |
| Recipe checker | `semantic_passes/function_checker.py` | Flavor count, flavor type, built-in overloads |

---

## Relationship to the Other Guides

- [LEXER_FLOW_GUIDE.md](./LEXER_FLOW_GUIDE.md) explains how source text is first tokenized before parsing and semantic validation.
- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md) explains the source-level program shapes accepted before AST construction begins.
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md) explains how source code becomes the AST.
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md) explains how symbols and scopes are collected from that AST.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how the compiler uses the AST plus symbol table to validate program meaning.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated AST is lowered into executable intermediate code.

Together, these guides describe:

```text
Source -> Lexer -> Tokens -> AST -> Symbol Table -> Semantic Validation
```
