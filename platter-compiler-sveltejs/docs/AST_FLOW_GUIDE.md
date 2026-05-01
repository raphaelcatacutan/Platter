# Platter Compiler: AST Flow Step-by-Step

## Overview
The Abstract Syntax Tree is the **canonical intermediate representation** that connects front-end parsing to all back-end analysis and code generation. It flows through 5 major stages:

```
Tokens
   ↓
[1] AST Construction (Token → AST Nodes)
   ↓
AST Tree (Program root)
   ↓
[2] Symbol Table Building (Walks AST, collects symbols)
   ↓
Symbol Table + AST
   ↓
[3] Semantic Passes (Traverse AST, check validity)
   ↓
AST (annotated with types, scope info)
   ↓
[4] IR Generation (Visit AST, emit TAC/Quads)
   ↓
TAC Instructions + Quadruples
   ↓
[5] Optimization + Execution
```

---

## Stage 1: AST Construction (Tokens → AST Nodes)

### Entry Point
**File:** `platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py`  
**Class:** `ASTParser` (line 16)  
**Main method:** `parse_program()` (line 63)

### What Happens
- **Input:** Filtered token stream (whitespace and comments removed)
- **Process:** Recursive descent parser that matches the grammar and builds tree nodes
- **Output:** `Program` node tree (root)

### Code-Level Flow Inside `ASTParser`

When reading the AST construction code, the control flow is:

```text
parse_program()
   ->
parse top-level declarations
   ->
parse recipe declarations
   ->
parse start platter
   ->
construct AST nodes
```

What this means:

1. The parser consumes the token stream in grammatical order.
2. Each parse function recognizes one language construct.
3. When a construct succeeds, that function creates the corresponding AST node immediately.
4. Higher-level parse functions assemble those child nodes into larger tree nodes like `Program`, `RecipeDecl`, and `Platter`.

### Key AST Node Types

#### Root: Program
```python
class Program(ASTNode):
    global_decl: List[IngrDecl | ArrayDecl | TablePrototype | TableDecl]
    recipe_decl: List[RecipeDecl]
    start_platter: Platter
```
**Example:**
```python
Program(
  global_decl=[
    IngrDecl("piece", "x", Literal(10)),
    TablePrototype("Point", [...]),
    TableDecl("Point", "p1", TableLiteral(...))
  ],
  recipe_decl=[
    RecipeDecl("piece", "double", [Param("piece", "n")], Platter(...))
  ],
  start_platter=Platter(statements=[...])
)
```

#### Declaration Nodes (Global + Local)

**IngrDecl** — Scalar variable
```python
IngrDecl(data_type="piece", identifier="count", init_value=Literal("piece", 5))
# Platter: piece of count = 5 ;
```

**ArrayDecl** — Array variable
```python
ArrayDecl(data_type="piece", dimensions=1, identifier="nums", 
          init_value=ArrayLiteral([Literal("piece", 1), Literal("piece", 2)]))
# Platter: piece [] of nums = { 1 , 2 } ;
```

**TablePrototype** — Type definition
```python
TablePrototype(name="Point", fields=[
  FieldDecl("piece", 0, "x"),
  FieldDecl("piece", 0, "y")
])
# Platter: prepare table Point with piece of x , piece of y ;
```

**TableDecl** — Table instance
```python
TableDecl(table_type="Point", identifier="p", 
          init_value=TableLiteral([("x", Literal(3)), ("y", Literal(4))]))
# Platter: Point of p = { x : 3 , y : 4 } ;
```

#### Statement Nodes (Inside Platter blocks)

**Platter** — Block (compound statement / scope)
```python
Platter(
  local_decls=[IngrDecl(...)],  # Local declarations
  statements=[...]  # Statements inside block
)
```

**Assignment** — Variable/array/table write
```python
Assignment(target=Identifier("x"), operator="=", value=BinaryOp(...))
# Platter: x = a + b ;
```

**CheckStatement** — If/else-if/else
```python
CheckStatement(
  condition=BinaryOp(...),  # check condition
  then_block=Platter(...),   # then block
  elif_clauses=[(BinaryOp(...), Platter(...))],  # alt blocks
  else_block=Platter(...)    # instead (else) block
)
```

**MenuStatement** — Switch/case
```python
MenuStatement(
  expr=Identifier("day"),
  cases=[CaseClause(Literal("piece", 1), [...]), ...],
  default=[...]  # usual clause
)
```

**PassLoop** — For loop
```python
PassLoop(
  init=Assignment(...),      # pass init
  condition=BinaryOp(...),   # condition
  update=Assignment(...),    # update
  body=Platter(...)          # body
)
```

**RepeatLoop** — While loop
```python
RepeatLoop(
  condition=BinaryOp(...),
  body=Platter(...)
)
```

**ServeStatement** — Return
```python
ServeStatement(value=BinaryOp(...))  # serve x + 1 ;
```

**BreakStatement / ContinueStatement** — Stop / next
```python
BreakStatement()       # stop ;
ContinueStatement()    # next ;
```

#### Expression Nodes

**BinaryOp** — Binary operation
```python
BinaryOp(left=Identifier("a"), operator="+", right=Literal("piece", 5))
# Platter: a + 5
```

**UnaryOp** — Unary operation
```python
UnaryOp(operator="-", operand=Identifier("x"))
# Platter: - x
```

**RecipeCall** — Function call
```python
RecipeCall(name="double", args=[Identifier("n")])
# Platter: double ( n )
```

**Identifier** — Variable reference
```python
Identifier(name="count")
# Platter: count
```

**ArrayAccess** — Array indexing
```python
ArrayAccess(array=Identifier("nums"), index=Literal("piece", 0))
# Platter: nums [ 0 ]
```

**TableAccess** — Field access
```python
TableAccess(table=Identifier("p"), field="x")
# Platter: p . x
```

**Literal** — Constant value
```python
Literal(data_type="piece", value=42)
Literal(data_type="chars", value="hello")
Literal(data_type="sip", value=3.14)
Literal(data_type="flag", value=True)  # up
```

**ArrayLiteral** — Array literal
```python
ArrayLiteral([Literal("piece", 1), Literal("piece", 2)])
# Platter: { 1 , 2 }
```

**TableLiteral** — Table literal
```python
TableLiteral([("x", Literal(3)), ("y", Literal(4))])
# Platter: { x : 3 , y : 4 }
```

---

## Stage 2: AST + Symbol Table Building

### Entry Point
**File:** `platter-compiler-sveltejs/static/python/app/semantic_analyzer/semantic_analyzer.py`  
**Function:** `analyze_program(ast_root)` (line 82)

**File:** `platter-compiler-sveltejs/static/python/app/semantic_analyzer/symbol_table/symbol_table_builder.py`  
**Class:** `SymbolTableBuilder` (line 30)  
**Method:** `build(ast_root)` (line 105)

### What Happens
1. **Walk the AST** to collect all symbol declarations
2. **Build scopes** (global, per-recipe, per-statement-block)
3. **Register symbols** in their respective scopes
4. **Track usage** of symbols

What this code does in the larger pipeline:

- takes the finished AST as input
- does not rebuild syntax
- uses AST node types to decide which scope and symbol actions to perform next
- leaves the AST structure intact for later semantic and IR passes

### Output: SymbolTable
```python
class SymbolTable:
    global_scope: Scope          # Top-level scope
    current_scope: Scope         # Currently active scope during tree walk
    table_types: Dict[str, TypeInfo]  # Table prototypes
    builtin_recipes: Dict[str, Symbol]  # Built-in functions (overloadable)
    undeclared_symbols: Dict[str, Symbol]  # Symbols used but never declared
    error_handler: ErrorHandler  # Collects errors/warnings
```

### Scope Building Example
For this Platter program:
```
piece of x = 5 ;
piece double ( piece of n ) :
    piece of result = n * 2 ;
    serve result ;
start ( ) :
    piece of y = double ( x ) ;
```

The symbol table creates:
```python
SymbolTable:
  global_scope:
    symbols:
      "x" → Symbol(kind=VARIABLE, type=piece, scope=global)
      "double" → Symbol(kind=FUNCTION, type=piece, scope=global)
    children:
      [recipe_double]:
        symbols:
          "n" → Symbol(kind=PARAMETER, type=piece, scope=recipe_double)
          "result" → Symbol(kind=VARIABLE, type=piece, scope=recipe_double)
        file/line info...
      [start_platter]:
        symbols:
          "y" → Symbol(kind=VARIABLE, type=piece, scope=start_platter)
        children: (none in this example)
```

**Key:** Each scope is a **Scope node** with `.symbols` dict and `.children` list.

---

## Stage 3: Semantic Passes (Validate AST + Symbol Table)

### Entry Point
**File:** `platter-compiler-sveltejs/static/python/app/semantic_analyzer/semantic_analyzer.py`  
**Method:** `SemanticAnalyzer._run_semantic_passes(ast_root)` (line 42)

### Four Passes (in order):

#### Pass 1: ScopeChecker
- **What:** Finds **undefined symbols** and **duplicate definitions**
- **Walks:** AST + SymbolTable simultaneously
- **Checks:**
  - Every `Identifier` node is declared before use
  - No two symbols with same name in same scope
  - Recipe parameters don't shadow names in parent scopes incorrectly

#### Pass 2: TypeChecker
- **What:** Ensures **type compatibility** in operations
- **Walks:** Expression subtrees (BinaryOp, UnaryOp, calls, assignments)
- **Checks:**
  - `piece + sip` → error (incompatible)
  - Array indexing uses `piece` type
  - Function return type matches assignment target

#### Pass 3: ControlFlowChecker
- **What:** Validates **control flow** logic
- **Walks:** Loop/condition/serve statement nodes
- **Checks:**
  - `stop` / `next` only inside loops
  - `serve` only inside functions
  - Unreachable code after `serve`

#### Pass 4: FunctionChecker (RecipeChecker)
- **What:** Validates **recipe (function) usage**
- **Walks:** All `RecipeCall` nodes
- **Checks:**
  - Recipe is defined
  - Argument count matches parameter count
  - Argument types match parameter types

### Mutation
- **AST is NOT modified** during passes
- **Errors/warnings are collected** in `error_handler`
- **Symbol table may be augmented** (e.g., storing inferred types)

### Error Handler Output
```python
class SemanticErrorHandler:
    errors: List[SemanticError]
    
    # Stats
    def has_errors() → bool
    def get_errors() → List[SemanticError]
```

---

## Stage 4: IR Generation (AST → Three Address Code)

### Entry Point
**File:** `platter-compiler-sveltejs/static/python/app/intermediate_code/ir_generator.py`  
**Class:** `IRGenerator` (line 35)  
**Method:** `generate(ast)` (line 93)

### What Happens
- **Traverses the AST** depth-first
- **Emits TAC (Three Address Code) instructions**
- **Builds quadruple table** (intermediate quadruple representation)
- **Returns:** `(tac_instructions, quad_table)`

### AST Visitor Pattern
The IRGenerator implements visitor methods for each AST node type:

```python
def visit_program(self, node: Program):
    # Process global declarations
    for decl in node.global_decl:
        self.visit_declaration(decl)
    
    # Process recipe definitions
    for recipe in node.recipe_decl:
        self.visit_recipe_decl(recipe)
    
    # Process start() main block
    self.visit_platter(node.start_platter)

def visit_var_decl(self, node: IngrDecl):
    # Emit TAC assignment instruction
    # e.g., TACAssignment("x", TACLiteral(5))

def visit_binary_op(self, node: BinaryOp):
    # Generate temp variable
    # Emit TAC for left operand
    # Emit TAC for right operand
    # Emit TAC binary operation
    # Return temp variable name
    # e.g., generates "t0 = a + b"
```

### Example: AST → TAC

**AST:**
```python
Assignment(
  target=Identifier("x"),
  operator="=",
  value=BinaryOp(
    left=Identifier("a"),
    operator="+",
    right=Literal("piece", 5)
  )
)
```

**TAC Output:**
```
t0 = 5            # TACLiteral("5")
t1 = a + t0       # TACBinaryOp("t1", "a", "+", "t0")
x = t1            # TACAssignment("x", "t1")
```

**Quadruple Table Entry:**
```
0: (+, a, 5, t1)
1: (=, t1, _, x)
```

### TAC Instruction Types
```python
TACAssignment(result, arg1)              # x = y
TACBinaryOp(result, arg1, op, arg2)      # t = a + b
TACUnaryOp(result, op, arg1)             # t = -a
TACArrayAccess(result, array, index)     # t = arr[i]
TACArrayAssign(array, index, value)      # arr[i] = val
TACTableAccess(result, table, field)     # t = obj.field
TACTableAssign(table, field, value)      # obj.field = val
TACFunctionCall(result, func_name, arg_count)  # t = call func
TACParam(value)                          # param val
TACLabel(label)                          # L0:
TACGoto(label)                           # goto L0
TACConditionalGoto(cond, label)          # if cond goto L0
TACReturn(value)                         # return val
```

---

## Stage 5: Optimization + Execution

### Optimization
**File:** `platter-compiler-sveltejs/static/python/app/intermediate_code/optimizer_manager.py`  
**Class:** `OptimizerManager` (line 26)  
**Method:** `optimize_tac(instructions)` (line 63)

Applies iterative passes:
1. **ConstantFolding** — `t = 5 + 3` → `t = 8`
2. **DeadCodeElimination** — Remove unreachable/unused assignments
3. **AlgebraicSimplification** — `x * 1` → `x`, `x + 0` → `x`
4. **ConstantPropagation** — Substitute known constants
5. **CopyPropagation** — `t1 = t0; x = t1` → `x = t0`

### Execution
**File:** `platter-compiler-sveltejs/static/python/app/intermediate_code/ir_interpreter.py`  
**Class:** `TACInterpreter` (line 47)  
**Method:** `run()` (line 140)

**Tree-walking interpreter:**
- Maintains a **program counter (pc)** through instruction list
- Maintains **call stack (Frames)** for function scoping
- Maintains **variable store** (per-frame locals)
- Executes **TAC instructions one by one**

**Example execution:**
```
TAC:
  0: t0 = 5
  1: t1 = a + t0
  2: x = t1

State after instruction 0:
  global_frame.vars = {t0: 5}

State after instruction 1:
  global_frame.vars = {t0: 5, a: 10, t1: 15}  // assuming a=10

State after instruction 2:
  global_frame.vars = {t0: 5, a: 10, t1: 15, x: 15}
```

---

## Complete Example Walkthrough

### Source Code
```
piece of x = 5 ;

piece double ( piece of n ) :
    piece of result = n * 2 ;
    serve result ;

start ( ) :
    piece of y = double ( x ) ;
```

### Step 1: Lexical Analysis
```
Tokens: [piece, of, x, =, 5, ;, piece, double, (, piece, of, n, ), :, ...]
```

### Step 2: Syntax Check (Parser)
- Validates token sequence matches grammar ✓

### Step 3: AST Construction (ASTParser)
```python
Program(
  global_decl=[
    IngrDecl("piece", "x", Literal("piece", 5))
  ],
  recipe_decl=[
    RecipeDecl(
      return_type="piece",
      return_dims=0,
      name="double",
      params=[ParamDecl("piece", 0, "n")],
      body=Platter(
        local_decls=[IngrDecl("piece", "result", None)],
        statements=[
          Assignment(
            target=Identifier("result"),
            operator="=",
            value=BinaryOp(Identifier("n"), "*", Literal("piece", 2))
          ),
          ServeStatement(Identifier("result"))
        ]
      )
    )
  ],
  start_platter=Platter(
    local_decls=[IngrDecl("piece", "y", None)],
    statements=[
      Assignment(
        target=Identifier("y"),
        operator="=",
        value=RecipeCall("double", [Identifier("x")])
      )
    ]
  )
)
```

### Step 4: Symbol Table Building
```python
SymbolTable:
  global_scope:
    symbols:
      "x" → Symbol(VARIABLE, piece, global_scope, init=5)
      "double" → Symbol(FUNCTION, piece, global_scope)
    children:
      [recipe_double]:
        symbols:
          "n" → Symbol(PARAMETER, piece, recipe_double)
          "result" → Symbol(VARIABLE, piece, recipe_double)
      [start_platter]:
        symbols:
          "y" → Symbol(VARIABLE, piece, start_platter)
```

### Step 5: Semantic Passes ✓
- All symbols defined before use ✓
- Types compatible ✓
- No control-flow violations ✓
- Recipe calls valid ✓

### Step 6: IR Generation
```
TAC emitted:
  0: x = 5                 // Global init
  
  1: begin_func double
  2: n = p0               // Bind param
  3: result = 0           // Default init (uninitialized var)
  4: t0 = n * 2
  5: result = t0
  6: return result
  7: end_func double
  
  8: begin_func start
  9: y = 0                // Default init
 10: param x              // Prepare call
 11: t1 = call double, 1
 12: y = t1
 13: return               // Implicit return
 14: end_func start
 
 15: t2 = call start, 0   // Main: call start()
```

### Step 7: Optimization
```
(After constant folding + dead code elimination)
  0: x = 5              // Keep (global init)
  1: begin_func double
  2: n = p0
  3: t0 = n * 2         // Remove default init of result
  4: return t0          // Simplify: return directly
  5: end_func double
  
  6: begin_func start
  7: param x
  8: t1 = call double, 1
  // removed: y = 0, y = t1 (dead if not accessed after)
  9: end_func start
  
 10: t2 = call start, 0
```

### Step 8: Execution
```
Execution trace:
  x = 5
  Call start()
    y = undefined
    Call double(x=5)
      n = 5
      t0 = 5 * 2 = 10
      return 10
    y = 10
    return
  Program finishes, y=10 in global scope
```

---

## Key Takeaways

1. **AST is the central hub** — All phases depend on it
2. **No modification during passes** — AST remains stable; errors collected separately
3. **Symbol table runs first** — Provides context for semantic passes
4. **Each phase adds constraints** — Lexer → Parser → AST → Scope → Type → ControlFlow → RecipeChecks
5. **IR is stateless from AST** — Just walks the tree, emits instructions
6. **Interpreter is a simple VM** — Executes TAC like a stack-based machine

---

## File Reference Quick Links

| Phase | File | Class/Function |
|-------|------|---|
| AST Construction | `ast_parser_program.py` | `ASTParser.parse_program()` |
| AST Nodes | `ast_nodes.py` | 31 node types |
| Symbol Table | `symbol_table_builder.py` | `SymbolTableBuilder.build()` |
| Semantic Analysis | `semantic_analyzer.py` | `SemanticAnalyzer.analyze()` |
| IR Generation | `ir_generator.py` | `IRGenerator.generate()` |
| Optimization | `optimizer_manager.py` | `OptimizerManager.optimize_tac()` |
| Execution | `ir_interpreter.py` | `TACInterpreter.run()` |
| AST Display | `ast_reader.py` | `print_ast()` |
| Symbol Display | `symbol_table_output.py` | `format_symbol_table_compact()` |

---

## Related Guides

- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md) explains the concrete source syntax accepted before AST construction begins.
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md) explains how the AST is walked to build scopes, symbols, and table type definitions.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how the AST plus symbol table are validated for scope, type, control-flow, and recipe-call correctness.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated AST is lowered into TAC and quadruples.
