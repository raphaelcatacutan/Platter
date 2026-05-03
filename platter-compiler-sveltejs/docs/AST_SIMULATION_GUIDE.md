# AST Parser Program Guide

This guide simulates what [`ast_parser_program.py`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:1) actually does while building the AST.

It is intentionally focused on the parser itself, not the full compiler pipeline. The goal is to make it easy to answer questions like:

- What does `parse_program()` expect first?
- When does the parser return a `Program`, `Platter`, `Assignment`, or `RecipeCall` node?
- Why does the parser keep `_context_type`, `_context_dimensions`, and `_context_identifier`?
- How does a plain `id` become a variable reference, a function call, an array access, or a table access?

The node classes referenced here live in [`ast_nodes.py`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_nodes.py:1).

## 1. What `ASTParser` receives

`ASTParser.__init__()` does four important things before any grammar function runs:

1. It removes non-semantic tokens:
   - `space`
   - `tab`
   - `newline`
   - `comment_single`
   - `comment_multi`
2. It creates parser state:
   - `self.pos`
   - `self.error_arr`
   - `_context_dimensions`
   - `_context_type`
   - `_context_identifier`
   - `_context_identifier_line`
   - `_context_identifier_col`
3. It rejects an empty token stream with `ErrorHandler("EOF", ...)`.
4. It appends a synthetic `EOF` token so `parse_program()` can verify that the whole source was consumed.

In practice, the parser works over a clean token list that looks more like this:

```text
[prepare, flag, of, safeIsPiece, (, chars, of, txt, ,, flag, of, positiveOnly, ), {, ... , }, start, (, ), {, ... , }, EOF]
```

## 2. The top-level grammar shape

The parser entry point is `parse_program()`:

```text
<program>
  -> <global_decl> <recipe_decl> start ( ) <platter>
```

That means the parser always tries to build the source in this order:

1. global declarations
2. recipe declarations
3. the mandatory `start()` block

The resulting tree is always a `Program` node:

```python
Program(
    global_decl=[...],
    recipe_decl=[...],
    start_platter=Platter(...)
)
```

## 3. Real control-flow inside `parse_program()`

Here is the parser’s real top-level behavior in plain English:

1. `appendF(FIRST_SET["<program>"])` seeds expected tokens for error reporting.
2. If the current token belongs to `PREDICT_SET["<program>"]`, parsing begins.
3. `global_decl()` returns a list of top-level declarations.
4. `recipe_decl()` returns a list of `RecipeDecl` nodes.
5. The parser then requires:
   - `start`
   - `(`
   - `)`
6. `platter()` parses the body of `start`.
7. A fresh `Program()` is created.
8. Each global declaration is added with `prog.add_global_decl(...)`.
9. Each recipe declaration is added with `prog.add_recipe_decl(...)`.
10. `prog.set_start_platter(node_5)` attaches the start block.
11. If the next token is not `EOF`, parsing fails with `ExpectedEOF_err`.

So `parse_program()` is not just validating syntax. It also assembles the final AST root.

## 4. Simulation: parsing a small program

Use this tiny source as the mental model:

```platter
piece of x = 5;

prepare piece of double(piece of n){
    serve n + n;
}

start(){
    piece of y = double(x);
}
```

### Step 4.1: `parse_program()`

Current token is `piece`, so the parser enters:

```text
parse_program
  -> global_decl
  -> recipe_decl
  -> start ( )
  -> platter
```

### Step 4.2: `global_decl()`

`global_decl()` is recursive and returns a list.

It sees `piece`, so it follows:

```text
<global_decl> -> piece <piece_decl> <global_decl>
```

Then:

```text
piece_decl
  -> of <piece_id> ;
```

Then:

```text
piece_id
  -> id <piece_ingredient_init> <piece_id_tail>
```

For `piece of x = 5;`, this becomes:

- token `id` has value `x`
- `piece_ingredient_init()` sees `=`
- it parses the right side as a strict piece expression
- it returns a `Literal("piece", 5)` or equivalent piece-valued expression

The parser constructs:

```python
IngrDecl("piece", "x", Literal("piece", 5), line, col)
```

Then `global_decl()` calls itself again. Since the next token is `prepare`, it stops and returns:

```python
[IngrDecl("piece", "x", Literal("piece", 5))]
```

### Step 4.3: `recipe_decl()`

Now the parser sees `prepare`, so it follows:

```text
<recipe_decl> -> prepare <serve_type> ( <spice> ) <platter> <recipe_decl>
```

`serve_type()` delegates to `decl_head()`:

```text
<decl_head> -> <primitive_types_dims> of id
```

For:

```platter
prepare piece of double(...)
```

that returns a temporary attribute object whose fields are roughly:

```python
data_type = "piece"
dimensions = 0
identifier = "double"
```

Then `spice()` parses:

```platter
piece of n
```

into:

```python
FieldDecl("piece", 0, "n", ...)
```

and the recipe constructor reuses that shape as parameter metadata for:

```python
RecipeDecl("piece", 0, "double", params, body, ...)
```

### Step 4.4: recipe body `platter()`

The body:

```platter
{
    serve n + n;
}
```

is parsed by:

```text
<platter> -> { <local_decl> <statements> }
```

`local_decl()` returns `[]` because the first token is `serve`, not a declaration.

`statements()` sees a jump/serve statement and parses:

```python
ServeStatement(
    BinaryOp(
        Identifier("n"),
        "+",
        Identifier("n")
    )
)
```

Then `platter()` manually splits its collected results into:

- declarations for `Platter.local_decls`
- executable statements for `Platter.statements`

That means a `Platter` is always normalized into:

```python
Platter(
    local_decls=[...],
    statements=[...]
)
```

### Step 4.5: `start(){ ... }`

After recipes, `parse_program()` requires:

```text
start ( ) <platter>
```

Inside:

```platter
{
    piece of y = double(x);
}
```

`local_decl()` handles `piece of y = double(x);`, creating:

```python
IngrDecl(
    "piece",
    "y",
    RecipeCall("double", [Identifier("x")])
)
```

At the end, the full AST is effectively:

```python
Program(
    global_decl=[
        IngrDecl("piece", "x", Literal("piece", 5))
    ],
    recipe_decl=[
        RecipeDecl(
            "piece",
            0,
            "double",
            [FieldDecl("piece", 0, "n")],
            Platter(
                local_decls=[],
                statements=[
                    ServeStatement(
                        BinaryOp(
                            Identifier("n"),
                            "+",
                            Identifier("n")
                        )
                    )
                ]
            )
        )
    ],
    start_platter=Platter(
        local_decls=[
            IngrDecl(
                "piece",
                "y",
                RecipeCall("double", [Identifier("x")])
            )
        ],
        statements=[]
    )
)
```

## 5. How declaration parsing works

The parser uses the same pattern repeatedly for primitive declarations:

- `piece`
- `sip`
- `flag`
- `chars`

For each type, it supports two broad forms:

1. scalar declaration
2. array declaration

### Scalar declarations

Example:

```platter
chars of name = "plate";
```

The parser path is:

```text
chars -> chars_decl -> of -> chars_id
```

This produces:

```python
IngrDecl("chars", "name", Literal("chars", "plate"))
```

If there are comma-separated identifiers, the parser returns a list:

```platter
piece of a = 1, b = 2, c;
```

becomes:

```python
[
    IngrDecl("piece", "a", Literal("piece", 1)),
    IngrDecl("piece", "b", Literal("piece", 2)),
    IngrDecl("piece", "c", None),
]
```

### Array declarations

The parser uses `_context_dimensions` so one function can compute dimensions and a later function can finish the `ArrayDecl`.

Example mental flow:

```platter
piece[] of nums;
```

becomes:

1. parser recognizes an array form
2. dimension count is stored in `_context_dimensions`
3. later tail functions reuse that saved count
4. final node is created as:

```python
ArrayDecl("piece", 1, "nums", None)
```

### Table prototypes and table declarations

Two top-level forms are important:

```platter
table of Person = [
    chars of name;
    piece of age;
];

Person of chef;
```

The first goes through `table_prototype()` and creates:

```python
TablePrototype(
    "Person",
    [
        FieldDecl("chars", 0, "name"),
        FieldDecl("piece", 0, "age"),
    ]
)
```

The second depends on `_context_type`.

When `global_decl()` or `local_decl()` sees an initial `id`, that `id` might be a table type. The parser stores that name in `_context_type`, then `table_decl()` builds:

```python
TableDecl("Person", "chef", None)
```

This is why the parser needs context instead of relying on a single function-local variable.

## 6. Why context variables exist

`ast_parser_program.py` is heavily recursive, and many grammar tails need information that was parsed earlier.

The three important saved contexts are:

### `_context_type`

Used when the parser has already consumed a type-like token and later needs it to build:

- `TableDecl`
- `ArrayDecl`

Common case:

```platter
Person of chef;
```

After consuming `Person` as an `id`, the parser saves:

```python
self._context_type = "Person"
```

Then `table_decl()` knows the resulting node is:

```python
TableDecl("Person", "chef", ...)
```

### `_context_dimensions`

Used when array brackets are parsed before the final declaration node is created.

Common case:

```platter
piece[][] of grid;
```

The parser computes `2`, stores it, and later constructs:

```python
ArrayDecl("piece", 2, "grid", ...)
```

### `_context_identifier`

Used when the parser reads an `id` first and only later learns whether it is:

- a plain identifier
- an assignment target
- a function call
- a table access chain
- an array access chain

Example:

```platter
double(x);
```

The parser first consumes `double` and stores:

```python
self._context_identifier = "double"
```

Then `call_tail()` can build:

```python
RecipeCall("double", [Identifier("x")])
```

without needing the original token to still be in scope.

## 7. How `id` becomes different AST shapes

This is one of the most useful mental models for the parser.

The token type `id` is not enough to decide the node shape. The next tokens decide that.

### Case 1: plain identifier expression

```platter
x
```

Path:

```text
id_ -> id -> id_tail -> epsilon
```

Node:

```python
Identifier("x")
```

### Case 2: recipe call

```platter
double(x)
```

Path:

```text
id_ -> id -> id_tail -> call_tailopt
```

Node:

```python
RecipeCall("double", [Identifier("x")])
```

### Case 3: array access

```platter
nums[i]
```

The parser builds the base identifier first, then applies an accessor closure that returns:

```python
ArrayAccess(
    Identifier("nums"),
    Identifier("i")
)
```

### Case 4: table access

```platter
chef.name
```

Again, the parser builds the base first and then applies a closure:

```python
TableAccess(
    Identifier("chef"),
    "name"
)
```

### Case 5: chained access

```platter
board[0].name
```

The parser does not construct the full chain immediately. Tail functions return builder closures. Those closures are applied to the base node later, producing nested accessors:

```python
TableAccess(
    ArrayAccess(
        Identifier("board"),
        Literal("piece", 0)
    ),
    "name"
)
```

That closure-based approach is used all over the parser for access tails and operation tails.

## 8. How statement parsing works

Inside `platter()`, executable code comes from `statements()`.

The high-level categories are:

- identifier-led statements
- built-in recipe calls
- conditionals
- loops
- jump/serve statements

### Identifier-led statements

When a statement starts with `id`, the parser must decide between:

1. expression statement
2. assignment

Example:

```platter
sum(total);
```

becomes:

```python
ExpressionStatement(
    RecipeCall("sum", [Identifier("total")])
)
```

Example:

```platter
total += 1;
```

becomes:

```python
Assignment(
    Identifier("total"),
    "+=",
    Literal("piece", 1)
)
```

Example:

```platter
items[i] = value;
```

becomes:

```python
Assignment(
    ArrayAccess(Identifier("items"), Identifier("i")),
    "=",
    Identifier("value")
)
```

### Built-in recipe calls

Built-ins like `append`, `bill`, and `copy` are parsed into the same general node:

```python
RecipeCall("append", [...])
RecipeCall("bill", [...])
RecipeCall("copy", [...])
```

So from the AST’s point of view, built-ins and user-defined recipes share one representation.

### Conditional statements

`check`, `alt`, and `instead` are collapsed into one `CheckStatement`:

```python
CheckStatement(
    condition=...,
    then_block=Platter(...),
    elif_clauses=[(..., ...), (..., ...)],
    else_block=Platter(...)
)
```

### Loop statements

The parser creates different node classes for different loop styles:

- `RepeatLoop`
- `OrderRepeatLoop`
- `PassLoop`

### Serve and jump statements

These become:

- `ServeStatement(value)`
- `BreakStatement()`
- `ContinueStatement()`

## 9. How expression parsing is assembled

Many expression functions follow the same pattern:

1. parse a left operand
2. parse a tail
3. if the tail exists, call it with the left operand
4. otherwise return the left operand directly

Typical shape:

```python
left = ...
tail = ...

if tail:
    return tail(left)
return left
```

This allows the parser to delay final node creation until it knows the full right side.

### Example: `n + n * 2`

The parser may initially build a right-heavy structure because of the LL grammar:

```python
BinaryOp(
    Identifier("n"),
    "+",
    BinaryOp(
        Identifier("n"),
        "*",
        Literal("piece", 2)
    )
)
```

Then `BinaryOp.__init__()` in [`ast_nodes.py`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_nodes.py:269) rotates the tree when needed so precedence is preserved.

That is a very important implementation detail:

- the grammar is LL-style and often right-recursive
- the AST node class repairs associativity and precedence afterwards

Without that rotation logic, many arithmetic trees would associate incorrectly.

## 10. How `platter()` normalizes mixed local results

One subtle but important behavior is in `platter()`.

`local_decl()` can return more than pure declarations. In some branches, it can also return early executable nodes such as:

- `Assignment`
- `ExpressionStatement`

So `platter()` performs a manual split:

```python
Platter(
    [d for d in decls if isinstance(d, declaration_types)],
    [s for s in decls if isinstance(s, statement_types)] + stmts
)
```

That means:

- local declaration parsing may temporarily return a mixed list
- `platter()` is the place that restores the final AST shape

If you ever see an unexpected statement appear to come from a declaration branch, this normalization step is usually the reason.

## 11. Simulation using `helper.platter`

The sample file [`helper.platter`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/tests/runtime_fixes/helper.platter:1) is a good stress test because it includes:

- multiple `prepare` declarations
- local declarations
- nested `check`
- `alt`
- `instead`
- `repeat`
- `pass`
- built-in calls like `copy()` and `append()`
- recipe calls inside conditions

Here is one short simulated slice:

```platter
repeat(copy(txt, i, i) != ""){
    ch = copy(txt, i, i);
}
```

The parser flow is roughly:

```text
looping_st
  -> repeat
  -> parse condition as strict flag expression
  -> parse body with platter()
```

The condition becomes:

```python
BinaryOp(
    RecipeCall("copy", [Identifier("txt"), Identifier("i"), Identifier("i")]),
    "!=",
    Literal("chars", "")
)
```

Inside the block:

```platter
ch = copy(txt, i, i);
```

becomes:

```python
Assignment(
    Identifier("ch"),
    "=",
    RecipeCall("copy", [Identifier("txt"), Identifier("i"), Identifier("i")])
)
```

So the full loop node is effectively:

```python
RepeatLoop(
    condition=BinaryOp(...),
    body=Platter(
        local_decls=[],
        statements=[
            Assignment(...)
        ]
    )
)
```

## 12. Error behavior

The parser uses `FIRST_SET` and `PREDICT_SET` for branch selection and error reporting.

Two helper methods matter:

- `appendF(first_set)`
- `parse_token(tok)`

### `appendF(first_set)`

This adds expected tokens into `self.error_arr`, skipping epsilon.

### `parse_token(tok)`

If the current token matches:

- it advances `self.pos`
- it clears `self.error_arr`

If it does not match:

- it merges expected tokens into `error_arr`
- it raises `ErrorHandler("Unexpected_err", current_token, error_arr)`

This means the parser is both:

- an AST builder
- a structured syntax error producer

## 13. Most important AST node outputs

These are the parser outputs you will see most often:

- `Program`
- `Platter`
- `RecipeDecl`
- `IngrDecl`
- `ArrayDecl`
- `TablePrototype`
- `TableDecl`
- `Assignment`
- `CheckStatement`
- `MenuStatement`
- `RepeatLoop`
- `OrderRepeatLoop`
- `PassLoop`
- `ServeStatement`
- `ExpressionStatement`
- `Identifier`
- `ArrayAccess`
- `TableAccess`
- `RecipeCall`
- `BinaryOp`
- `UnaryOp`
- `Literal`
- `ArrayLiteral`
- `TableLiteral`

## 14. Mental model for reading the file

When reading [`ast_parser_program.py`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:1), this is the fastest reliable mental model:

1. Each parser method corresponds to one grammar nonterminal.
2. Each `if` or `elif` matches one grammar production.
3. `parse_token(...)` consumes terminals.
4. Recursive calls build child nodes first.
5. Return values are one of:
   - a concrete AST node
   - a list of AST nodes
   - a closure that will build access/operation chains later
   - `None` for epsilon
6. Context fields bridge information across split grammar branches.
7. `Program`, `Platter`, `Assignment`, `RecipeCall`, and `BinaryOp` are assembled incrementally, not in one pass.

## 15. Short reference map

- Parser entry: [`parse_program()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:63)
- Top-level declarations: [`global_decl()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:102)
- Table prototype parsing: [`table_prototype()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:1992)
- Recipe parsing: [`recipe_decl()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:2270)
- Block parsing: [`platter()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:2363)
- Statement parsing: [`statements()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:2639)
- Identifier expression parsing: [`id_()`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_parser_program.py:5346)
- Core node definitions: [`ast_nodes.py`](/abs/path/c:/Users/Victus/Documents/PROGRAMMABLES/_projects/Platter/platter-compiler-sveltejs/static/python/app/semantic_analyzer/ast/ast_nodes.py:17)

## 16. Bottom line

`ast_parser_program.py` is best understood as an LL-style recursive-descent builder with four recurring techniques:

- list collection for repeated declarations and statements
- saved parser context for split productions
- closures for deferred accessor/operator construction
- final AST normalization in `Program`, `Platter`, and `BinaryOp`

If you keep those four ideas in mind, the file becomes much easier to trace and debug.
