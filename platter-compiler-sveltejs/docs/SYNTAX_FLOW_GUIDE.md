# Platter Compiler: Syntax Flow Guide

## Overview

This guide describes the **actual source-level syntax flow** of Platter as accepted by the current lexer, parser, and syntax test suite.

It is intentionally written from the parser's point of view:

1. what a complete Platter file looks like
2. what can appear at global scope
3. what can appear inside recipes and `start()`
4. how expressions, arrays, tables, and built-ins fit together
5. what syntax shapes are valid but easy to get wrong

If another document disagrees with this guide, treat this one as the more implementation-aligned reference.

---

## 1. Top-Level Program Flow

Every complete Platter program follows this high-level order:

```platter
<global declarations and global table instances>
<zero or more recipe declarations>
start() {
    <statements>
}
```

### Important ordering rules

- Global declarations must come **before** `start()`.
- Recipe declarations must come **before** `start()`.
- `start()` is required.
- Nothing may appear after `start()`.

### Minimal valid program

```platter
start() {
}
```

### Full top-level example

```platter
table of Student = [
    chars of name;
    piece of age;
];

piece of limit = 3;
chars of label = "Platter";
Student of sample = [name = "Mia"; age = 20;];

prepare piece of add(piece of a, piece of b) {
    serve a + b;
}

start() {
    piece of total = add(limit, 2);
    bill(tochars(total));
}
```

---

## 2. Global Scope Syntax

At global scope, the parser accepts:

- primitive declarations
- primitive array declarations
- table type declarations
- table instance declarations
- table array declarations
- recipe declarations
- the final `start()`

---

## Related Guides

- [LEXER_FLOW_GUIDE.md](./LEXER_FLOW_GUIDE.md) explains how raw source text is first converted into the token stream that the parser consumes.
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md) explains how valid source syntax is transformed into AST nodes.
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md) explains how declarations and scopes from that AST are collected into the symbol table.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how the compiler validates meaning after syntax has already parsed successfully.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated program is lowered into TAC and quadruples.

### Primitive globals

```platter
piece of x;
piece of a = 1, b = 2;

chars of name = "Ada";
flag of ready = up;
sip of rate = 3.14;
```

### Primitive array globals

```platter
piece[] of nums = [1, 2, 3];
chars[] of words = ["a", "b"];
flag[] of states = [up, down, up];
sip[][] of grid;
```

### Table type declarations

Tables are Platter's record/struct types.

```platter
table of Student = [
    chars of name;
    piece of age;
];
```

Field declarations inside a table body end with semicolons.

### Table instance declarations

Unlike primitive declarations, table instances begin with the **table type name**.

```platter
Student of s;
Student of t = [name = "Kai"; age = 19;];
Student of a = [name = "A"; age = 1;], b = [name = "B"; age = 2;];
```

### Table array declarations

```platter
Student[] of classList;
Student[] of classList = [
    [name = "Ana"; age = 18;],
    [name = "Ben"; age = 19;]
];
```

---

## 3. Recipe Declaration Flow

Recipes are declared with `prepare`.

### General form

```platter
prepare <return-type> of <recipe-name>(<parameters>) {
    <local declarations>
    <statements>
}
```

### Examples

```platter
prepare piece of inc(piece of x) {
    serve x + 1;
}

prepare chars of greet(chars of name) {
    serve "Hi " + name;
}

prepare piece[] of makeList() {
    piece[] of vals = [1, 2, 3];
    serve vals;
}

prepare Student of makeStudent(chars of name, piece of age) {
    serve [name = name; age = age;];
}
```

### Parameter syntax

Parameters use the same type pattern as declarations:

```platter
piece of n
chars of text
flag of ok
sip of amount
piece[] of nums
Student of person
Student[] of people
```

### Return type syntax

A recipe may return:

- `piece`
- `chars`
- `flag`
- `sip`
- any declared table type
- any of those as arrays

---

## 4. `start()` Flow

`start()` is the required entry platter.

### Form

```platter
start() {
    <statements>
}
```

### Important restrictions

- `start()` takes **no parameters**.
- `start()` must appear once at the end of the file.
- Declarations after `start()` are invalid.

---

## 5. Statement Flow Inside a Platter

Inside a recipe body or `start()`, statements are parsed in this general order:

1. local declarations
2. assignments or recipe/built-in calls
3. control-flow statements
4. `serve`, `stop`, `next`

### Statement families

- local declarations
- assignments
- built-in or user-defined recipe calls
- `check / alt / instead`
- `menu / choice / usual`
- `pass`
- `repeat`
- `order ... repeat`
- `serve`
- `stop`
- `next`

### Important restriction

The current syntax does **not** accept a free-standing block like:

```platter
{
    x = 1;
}
```

Blocks are introduced only by constructs such as `start`, `prepare`, `check`, `pass`, `repeat`, `order`, and `menu`.

---

## 6. Local Declaration Syntax

Local declarations mirror global declarations.

### Primitive locals

```platter
piece of x;
piece of a = 1, b = 2, c;

chars of msg = "hello";
flag of done = down;
sip of pi = 3.14;
```

### Array locals

```platter
piece[] of nums = [1, 2, 3];
chars[] of names;
flag[][] of seen;
```

### Table locals

```platter
Student of s;
Student of t = [name = "Zed"; age = 21;];
Student[] of roster = [[name = "A"; age = 1;]];
```

---

## 7. Assignment Flow

Assignments can target:

- a plain identifier
- an array element
- a table field
- a nested field or indexed field

### Simple assignment

```platter
x = 5;
name = "Ada";
ready = up;
```

### Compound assignment

```platter
x += 1;
y -= 2;
z *= 3;
n /= 10;
r %= 2;
```

### Array assignment

```platter
nums[0] = 10;
matrix[i][j] = 5;
```

### Table field assignment

Platter uses `:` for field access, not `.`.

```platter
student:name = "Mia";
student:age += 1;
classList[0]:name = "Noah";
box:dim:w = 15;
```

---

## 8. Conditional Flow

### `check / alt / instead`

This is the Platter if/else-if/else chain.

```platter
check(score > 90) {
    bill("A");
} alt(score > 80) {
    bill("B");
} instead {
    bill("C");
}
```

### Notes

- `alt(...)` attaches to the previous `check(...)`.
- `instead { ... }` is optional.
- Conditions are enclosed in parentheses.

### Minimal forms

```platter
check(x) {
}

check(x > 0) {
} instead {
}
```

---

## 9. Menu Flow

`menu` is the switch-like construct.

### General form

```platter
menu(expr) {
    choice 1:
        <statements>
    choice 2:
        <statements>
    usual:
        <statements>
}
```

### Example

```platter
menu(day) {
    choice 1:
        bill("Mon");
        stop;
    choice 2:
        bill("Tue");
        stop;
    usual:
        bill("Other");
}
```

### Notes

- `choice` values are literal-style case labels in practice, commonly numbers or strings.
- `usual` is optional.
- Statements inside `choice` and `usual` do not require extra braces.
- `stop;` is commonly used to exit a `menu` branch.

---

## 10. Loop Flow

Platter currently supports three loop forms.

### A. `repeat` loop

This behaves like a `while`.

```platter
repeat(i < 10) {
    i += 1;
}
```

### B. `order ... repeat` loop

This behaves like a `do ... while`.

```platter
order {
    x += 1;
} repeat(x < 5);
```

### C. `pass` loop

This is the `for`-style loop, but its header order is parser-specific:

```platter
pass(<init>; <update>; <condition>) {
    <statements>
}
```

Example:

```platter
pass(i = 0; i += 1; i < 5) {
    bill(tochars(i));
}
```

### Important `pass` gotcha

The accepted order is:

1. initialization
2. update
3. condition

Not the usual C-style `init; condition; update`.

### Loop control

```platter
stop;
next;
```

- `stop;` exits the current loop, and is also used inside `menu`.
- `next;` skips to the next loop iteration.

---

## 11. Serve Flow

`serve` returns a value from a recipe or from `start()`.

```platter
serve x;
serve x + 1;
serve [1, 2, 3];
serve [name = "Ada"; age = 20;];
```

### Important note

The current language shape expects `serve` to be followed by a value expression. A bare `serve;` is not part of the normal accepted syntax.

---

## 12. Expression Flow

Platter expressions are **type-shaped** in the parser. In practice, you can think of them as four main expression families:

- piece-oriented numeric expressions
- sip-oriented decimal expressions
- chars-oriented string expressions
- flag-oriented boolean/relational expressions

There is also an `any` expression family used in broader assignment and call contexts.

### Common expression atoms

- identifiers
- literals
- parenthesized expressions
- recipe calls
- built-in calls
- array access
- table field access

### Numeric examples

```platter
x + 1
a * b
n % 2
(x + y) / 2
pow(2, 8)
fact(5)
sqrt(25)
topiece("32")
tosip(5)
```

### String examples

```platter
"Hello"
name
"Hi " + name
tochars(score)
copy(text, 1, 3)
cut(12.56, 2.0)
take()
```

### Boolean examples

```platter
up
down
x > 0
a == b
name == "Ada"
not done
(x > 0) and ready
(a < b) or (c == d)
matches(text, "")
```

### Operator vocabulary used by the current parser

- arithmetic: `+ - * / %`
- relational: `< > <= >= == !=`
- logical: `and or not`

Use `and`, `or`, and `not` instead of `&&`, `||`, and `!`.

---

## 13. Arrays

### Declaration

```platter
piece[] of nums;
piece[][] of grid;
Student[] of roster;
```

### Literal syntax

Array literals use square brackets and commas.

```platter
[1, 2, 3]
[]
[[1, 2], [3, 4]]
[[name = "A"; age = 1;], [name = "B"; age = 2;]]
```

### Access syntax

```platter
nums[0]
grid[1][2]
roster[0]:name
```

### Built-ins that work with arrays

The syntax test suite and parser recognize these as array-returning built-ins:

```platter
append(nums, 4)
remove(nums, 1)
sort(nums)
reverse(nums)
```

They may appear:

- in assignments
- in declarations
- as standalone statements

Examples:

```platter
nums = append(nums, 4);
append(nums, 4);
nums = sort(nums);
```

### Array indexing gotcha

Field access after an index is valid:

```platter
items[1]:id
```

Nested arithmetic directly inside an index is more parser-sensitive than a normal expression, so simple index expressions are safest:

```platter
arr[i]
arr[0]
```

---

## 14. Tables

Tables are declared with `table of Name = [ ... ];`.

### Table type example

```platter
table of Person = [
    chars of name;
    piece of age;
];
```

### Table literal syntax

Table literals also use square brackets, but use **semicolon-separated field assignments**:

```platter
[name = "Ada"; age = 20;]
[]
```

An empty table literal is also accepted for a table-typed variable:

```platter
Person of p = [];
```

### Field access syntax

Use `:`.

```platter
p:name
p:age
classroom:leader:name
```

### Nested arrays and tables

These combinations are accepted:

```platter
Transaction[] of logs = [[kind = 1; amount = 1.0; result = "ok"; balance = 2.0;]];
logs[0]:result
box:dim:w
```

---

## 15. Built-In Recipe Calls

The current parser recognizes a large built-in call set directly.

### Common built-ins seen in the grammar and tests

```platter
bill(...)
take()
copy(...)
cut(...)
tochars(...)
topiece(...)
tosip(...)
size(...)
search(...)
matches(...)
fact(...)
pow(...)
sqrt(...)
rand()
append(...)
remove(...)
sort(...)
reverse(...)
```

### Examples

```platter
bill("Hello");
chars of s = take();
piece of n = topiece("42");
sip of r = sqrt(25);
flag of ok = matches(name, "Ada");
piece of len = size(nums);
```

### User-defined recipe calls

User recipes use the same call form:

```platter
sum(1, 2)
makeStudent("Kai", 19)
merge(left, right)
```

---

## 16. Practical Syntax Templates

### Program template

```platter
table of Record = [
    piece of id;
    chars of name;
];

piece of counter = 0;

prepare piece of nextId(piece of current) {
    serve current + 1;
}

start() {
    Record of item = [id = 1; name = "Sample";];
    piece[] of nums = [1, 2, 3];

    check(item:id > 0) {
        bill(item:name);
    } instead {
        bill("invalid");
    }

    pass(counter = 0; counter += 1; counter < size(nums)) {
        bill(tochars(nums[counter]));
    }
}
```

### Table-heavy template

```platter
table of Dim = [
    piece of w;
];

table of Box = [
    Dim of d;
];

start() {
    Box of b = [d = [w = 15;];];
    bill(tochars(b:d:w));
}
```

### Array-heavy template

```platter
prepare piece[] of grow(piece[] of vals) {
    vals = append(vals, 4);
    vals = sort(vals);
    serve vals;
}

start() {
    piece[] of nums = [3, 1, 2];
    nums = grow(nums);
    bill(tochars(nums[0]));
}
```

---

## 17. Parser-Aligned Gotchas

These are the syntax issues most likely to surprise someone reading only the higher-level docs.

### 1. Field access uses `:`, not `.`

```platter
student:age
```

### 2. Logical operators are `and`, `or`, `not`

```platter
check(a > 0 and not done) {
}
```

### 3. `pass` uses `init; update; condition`

```platter
pass(i = 0; i += 1; i < 10) {
}
```

### 4. `start()` must be last

```platter
start() {
}
```

No global declarations or recipes may follow it.

### 5. Free-standing `{ ... }` blocks are not accepted

Use them only as part of a language construct.

### 6. `serve` is normally value-bearing

```platter
serve x;
```

### 7. Array literals and table literals both use `[...]`

Distinguish them by their contents:

- array literal: `[1, 2, 3]`
- table literal: `[name = "Ada"; age = 20;]`

### 8. Table declarations start with the table type name

```platter
Student of s;
```

### 9. Nested access mixes `[]` and `:`

```platter
logs[0]:result
box:dim:w
```

---

## 18. End-to-End Syntax Walkthrough

This example shows the normal flow of a real Platter file from top to bottom.

```platter
table of Item = [
    piece of id;
    chars of name;
];

piece of seed = 100;

prepare Item of makeItem(piece of offset, chars of label) {
    Item of temp = [id = seed + offset; name = label;];
    serve temp;
}

prepare piece of totalIds(Item[] of items) {
    piece of i = 0;
    piece of total = 0;

    repeat(i < size(items)) {
        total += items[i]:id;
        i += 1;
    }

    serve total;
}

start() {
    Item[] of items = [
        makeItem(1, "A"),
        makeItem(2, "B")
    ];

    check(size(items) > 1) {
        bill("many");
    } instead {
        bill("few");
    }

    menu(items[0]:id) {
        choice 101:
            bill("first");
            stop;
        usual:
            bill("other");
    }

    bill(tochars(totalIds(items)));
}
```

### Flow summary

1. Define table types first.
2. Define global variables next.
3. Define helper recipes after globals.
4. End with `start()`.
5. Inside platters, combine declarations, assignments, conditionals, loops, calls, and `serve`.

---

## Relationship to the Other Guides

- `LEXER_REFERENCE.md` explains token formation.
- `GRAMMAR.md` describes the broader grammar intent.
- `AST_FLOW_GUIDE.md` explains how valid syntax becomes AST.
- `SYMBOL_TABLE_FLOW_GUIDE.md` explains how declared names are collected.
- `SEMANTIC_FLOW_GUIDE.md` explains type, scope, and control-flow validation.
- `IR_FLOW_GUIDE.md` explains how validated syntax is lowered into TAC and quadruples.

Together, the implementation pipeline is:

```text
Source
  -> Lexing
  -> Syntax Parsing
  -> AST
  -> Symbol Table
  -> Semantic Analysis
  -> IR Generation
  -> Optimization / Execution
```
