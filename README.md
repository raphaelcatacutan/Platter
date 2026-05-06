# Platter Programming Language - Comprehensive User Guide

A complete guide to the Platter programming language—a culinary-themed procedural language with static typing, compiled to Three-Address Code. This guide covers all language features, syntax rules, semantics, and practical examples.

## Table of Contents

- [Language Overview](#language-overview)
- [Quick Start](#quick-start)
- [Data Types & Type System](#data-types--type-system)
- [Variables & Declarations](#variables--declarations)
- [Functions & Recipes](#functions--recipes)
- [Control Flow Statements](#control-flow-statements)
- [Operators & Expressions](#operators--expressions)
- [Arrays & Collections](#arrays--collections)
- [Tables & Structures](#tables--structures)
- [Semantic Rules & Constraints](#semantic-rules--constraints)
- [Complete Examples](#complete-examples)
- [Common Patterns & Best Practices](#common-patterns--best-practices)
- [IDE Features & Development](#ide-features--development)
- [Technical Reference](#technical-reference)

---

## Language Overview

**Platter** is a statically-typed, procedural programming language designed with culinary metaphors to make code both functional and thematic. Every language construct uses cooking-related keywords, creating an intuitive and memorable syntax.

### Key Characteristics

| Characteristic | Details |
|---|---|
| **Paradigm** | Imperative/Procedural |
| **Type System** | Static, explicit type declarations |
| **Memory Model** | Automatic memory management |
| **Compilation** | Compiles to Three-Address Code (TAC) |
| **Execution** | Direct interpretation via Pyodide (Python in WebAssembly) |
| **Primary Use** | Educational language for learning compiler design |
| **File Extension** | `.platter` |

### Language Philosophy

Platter replaces common programming keywords with culinary terminology:

```
Function Declaration:  prepare  (instead of function, def, void)
Integer Type:          piece    (instead of int)
String Type:           chars    (instead of string, str)
Boolean Type:          flag     (instead of bool)
Float Type:            sip      (instead of float, double)
Boolean True:          up       (instead of true)
Boolean False:         down     (instead of false)
Return Statement:      serve    (instead of return)
Print Function:        bill     (instead of print)
If Statement:          check    (instead of if)
Else-if Statement:     alt      (instead of else if)
Else Statement:        instead  (instead of else)
Switch Statement:      menu     (instead of switch)
Case Label:            choice   (instead of case)
Default Case:          usual    (instead of default)
For Loop:              pass     (instead of for)
Do-While Loop:         order    (instead of do)
While Condition:       repeat   (instead of while)
Structure Type:        table    (instead of struct, class)
Exit Loop:             stop     (instead of break)
Skip Iteration:        next     (instead of continue)
```

---

## Quick Start

### Your First Program

```platter
start() {
    bill("Hello, Platter!");
}
```

Run this in the browser IDE to see output. The `start()` block is the program's entry point.

### A Simple Calculation

```platter
prepare piece of add(piece of a, piece of b) {
    serve a + b;
}

start() {
    piece of result = add(5, 3);
    bill(result);  // Output: 8
}
```

### Next Steps

1. Understand **Data Types** (piece, chars, flag, sip)
2. Learn **Variables** and **Scope**
3. Master **Functions/Recipes**
4. Apply **Control Flow** (if/switch/loops)
5. Use **Arrays** and **Tables** for complex data

---

## Data Types & Type System

Platter provides four primitive types and user-defined table types. All types are statically checked at compile time.

### Primitive Types

#### 1. piece (Integer)
32-bit signed integers for whole numbers.

```platter
piece of age = 25;
piece of count = 0;
piece of negativeNum = -42;
piece of largeNum = 999999;
```

**Characteristics:**
- Range: Approximately ±2.1 billion
- No fractional part
- Used for counting, indexing, and whole number math

#### 2. chars (String)
Text and character sequences enclosed in double quotes.

```platter
chars of name = "Alice";
chars of greeting = "Hello, World!";
chars of empty = "";
chars of multiWord = "The quick brown fox";
```

**Escape Sequences:**
- `\"` - Include double quote: `"She said \"Hi\""`
- `\\` - Include backslash: `"Path: C:\\Users"`
- `\n` - Newline character (printed as newline)
- `\t` - Tab character
- `\r` - Carriage return

**Example with Escapes:**
```platter
chars of message = "Line 1\nLine 2";  // Two lines
chars of path = "C:\\folder\\file.txt";
```

#### 3. flag (Boolean)
True/false values using `up` (true) and `down` (false).

```platter
flag of isReady = up;      // true
flag of isComplete = down; // false
flag of isEmpty = up;
```

**Usage:**
- Condition results from relational operators (`<`, `>`, `==`, etc.)
- Boolean expressions in if/while statements
- Logical operations (`&&`, `||`, `!`)

#### 4. sip (Floating-Point)
Double-precision decimal numbers for fractional values.

```platter
sip of pi = 3.14159;
sip of temperature = 98.6;
sip of discount = 0.25;
sip of negative = -3.14;
```

**Characteristics:**
- Double precision (64-bit IEEE 754)
- Supports fractional and very large/small numbers
- Default literal type for decimals

**Example:**
```platter
sip of result = 10 / 3;  // Result: 3.333...
```

### Type Literals & Initialization

| Type | Literal Form | Example |
|------|---|---|
| **piece** | Integer | `0`, `42`, `-5`, `999` |
| **chars** | Double-quoted string | `"hello"`, `"x"`, `""` |
| **flag** | `up` or `down` | `up`, `down` |
| **sip** | Decimal number | `3.14`, `-0.5`, `1.0` |

### Type Compatibility & Coercion

Platter enforces strict type safety. No automatic type conversion occurs.

```platter
piece of a = 5;
sip of b = 2.5;

piece of result = a + b;  // ❌ ERROR: Cannot add piece to sip
sip of result = a + b;    // ✅ OK: Mixed arithmetic returns sip
```

**Operator Type Rules:**
- `piece op piece` → `piece`
- `sip op sip` → `sip`
- `piece op sip` → `sip`
- String concatenation: Not supported via `+` operator
- Mixed-type assignments are forbidden

---

## Variables & Declarations

### Global Variables

Declared at the program level before recipes and `start()` block. Accessible from anywhere in the program.

#### Basic Declaration

```platter
piece of globalCount;           // Declaration only (uninitialized)
chars of globalName = "Platter"; // Declaration with initialization
```

#### Multiple Variables

Declare multiple variables of the same type on one line:

```platter
piece of x, y, z;               // All uninitialized
piece of a = 10, b = 20, c;     // a=10, b=20, c=uninitialized
sip of x = 1.5, y = 2.5, z;     // x=1.5, y=2.5, z=uninitialized
```

#### Type Declaration Syntax

All global declarations follow this pattern:

```
<type> of <identifier> [= <initializer>] [, <identifier> [= <initializer>]]*;
```

Where `<type>` is one of: `piece`, `chars`, `flag`, `sip`

#### Examples

```platter
piece of maxSize = 100;
piece of count = 0, total = 0, index;
chars of title = "User Management";
chars of description;
flag of isActive = up;
flag of debugMode = down;
sip of balance = 1000.50;
sip of rate = 0.05, tax = 0.10;
```

### Local Variables

Declared inside function bodies. Accessible only within that function.

```platter
prepare piece of calculate() {
    piece of result = 0;        // Local variable
    piece of temp;              // Local uninitialized
    sip of adjustment = 1.5;    // Local sip variable
    result = temp + 10;
    serve result;
}
```

### Variable Scope Rules

**Global Scope:**
- Variables declared at program level
- Accessible from all recipes and `start()` block
- Initialized before program execution

**Local Scope:**
- Variables declared inside recipes or `start()` block
- Accessible only within that block
- Shadowing forbidden: Cannot have same name as global

**Scope Violation Examples:**

```platter
piece of globalVar = 10;

prepare piece of doMath() {
    piece of globalVar = 20;  // ❌ ERROR: Cannot shadow global variable
    serve globalVar;
}
```

### Variable Initialization

**Initialized Variables:**
```platter
piece of count = 5;          // Initialized to 5
chars of name = "Alice";     // Initialized to "Alice"
flag of ready = up;          // Initialized to true
```

**Uninitialized Variables:**
```platter
piece of count;              // Uninitialized (undefined value)
chars of message;            // Uninitialized
```

**Using Uninitialized Variables:**
Accessing uninitialized variables may result in undefined behavior. Best practice: Always initialize before use.

### Variable Assignment

Update variables after declaration:

```platter
piece of x = 5;
x = 10;         // OK: Reassign
x = "hello";    // ❌ ERROR: Type mismatch

chars of name = "Alice";
name = "Bob";   // OK: String update
```

---

## Functions & Recipes

Functions in Platter are called **recipes**. They define reusable blocks of code with input parameters and return values.

### Recipe Declaration

**Basic Syntax:**
```platter
prepare <return-type> of <recipe-name>(<parameter-list>) {
    <local-declarations>
    <statements>
    serve <return-value>;
}
```

**Components:**
- `prepare` - Recipe declaration keyword
- `<return-type>` - `piece`, `chars`, `flag`, `sip`, or table type name
- `of` - Keyword separator
- `<recipe-name>` - Unique function identifier
- `<parameter-list>` - Comma-separated parameters (optional)
- `<local-declarations>` - Variable declarations (optional)
- `<statements>` - Recipe body
- `serve` - Return statement (must exist)

### No Parameters, Simple Return

```platter
prepare piece of getNumber() {
    serve 42;
}

prepare chars of greet() {
    serve "Hello!";
}

start() {
    piece of answer = getNumber();  // answer = 42
    chars of message = greet();     // message = "Hello!"
    bill(answer);
    bill(message);
}
```

### With Parameters

```platter
prepare piece of addNumbers(piece of a, piece of b) {
    serve a + b;
}

prepare sip of convertTemp(sip of celsius) {
    serve (celsius * 9 / 5) + 32;
}

prepare chars of createMessage(chars of prefix, piece of count) {
    serve prefix + " " + count;  // Note: String concat not directly supported
}
```

### Parameter Syntax

Parameters are declared like variables:

```
<type> of <parameter-name> [, <type> of <parameter-name>]*
```

**Multiple Parameters:**
```platter
prepare piece of max(piece of x, piece of y, piece of z) {
    piece of result = x;
    check (y > result) {
        result = y;
    }
    check (z > result) {
        result = z;
    }
    serve result;
}

start() {
    piece of largest = max(10, 25, 15);
    bill(largest);  // Output: 25
}
```

### Return Statements

Must use `serve` keyword:

```platter
prepare piece of calculate(piece of n) {
    check (n > 0) {
        serve n * 2;  // Return early
    }
    serve 0;  // Default return
}
```

### Function Naming Rules

- Must be unique (no overloading)
- Must not match keywords
- Case-sensitive: `add`, `Add`, `ADD` are different functions
- Can contain letters, digits, underscores

### Recursive Functions

Functions can call themselves:

```platter
prepare piece of fibonacci(piece of n) {
    check (n <= 1) {
        serve n;
    }
    serve fibonacci(n - 1) + fibonacci(n - 2);
}

start() {
    piece of result = fibonacci(10);
    bill(result);  // Output: 55
}
```

### Array Parameters

Functions can take arrays as parameters:

```platter
prepare piece of sum(piece[] of numbers) {
    piece of total = 0;
    piece of length = 5;  // Must manually specify length
    pass (piece of i = 0; i < length; i += 1) {
        total = total + numbers[i];
    }
    serve total;
}

start() {
    piece[] of values = [10, 20, 30, 40, 50];
    piece of result = sum(values);
    bill(result);  // Output: 150
}
```

### Table Return Types

Functions can return structured data:

```platter
table of Point = [
    piece of x;
    piece of y;
];

prepare Point of createPoint(piece of xVal, piece of yVal) {
    serve [
        x = xVal;
        y = yVal;
    ];
}

start() {
    Point of p = createPoint(5, 10);
    bill(p.x);  // Output: 5
    bill(p.y);  // Output: 10
}
```

---

## Control Flow Statements

Platter provides conditional execution and loop constructs using culinary keywords.

### Conditional: check/alt/instead

**Syntax:**
```platter
check (<condition>) {
    // statements if condition is true
} alt (<condition>) {
    // statements if first condition false and this true
} alt (<condition>) {
    // additional else-if branches
} instead {
    // statements if all conditions false
}
```

**Simple If:**
```platter
piece of age = 18;

check (age >= 18) {
    bill("You are an adult");
}
```

**If-Else:**
```platter
check (age >= 18) {
    bill("Adult");
} instead {
    bill("Minor");
}
```

**If-Else If-Else:** (using `alt`)
```platter
piece of score = 85;

check (score >= 90) {
    bill("Grade: A");
} alt (score >= 80) {
    bill("Grade: B");
} alt (score >= 70) {
    bill("Grade: C");
} instead {
    bill("Grade: F");
}
```

**Nested Conditions:**
```platter
piece of x = 5, y = 10;

check (x > 0) {
    check (y > 0) {
        bill("Both positive");
    } instead {
        bill("X positive, Y not");
    }
} instead {
    bill("X not positive");
}
```

### Switch: menu/choice/usual

**Syntax:**
```platter
menu (<expression>) {
    choice <value1>:
        <statements>
    choice <value2>:
        <statements>
    usual:
        <statements>
}
```

**Characteristics:**
- Evaluates expression once
- Falls through cases without `stop`
- `stop` exits the switch
- `usual` is the default case

**Integer Switch:**
```platter
piece of day = 2;

menu (day) {
    choice 1:
        bill("Monday");
        stop;
    choice 2:
        bill("Tuesday");
        stop;
    choice 3:
        bill("Wednesday");
        stop;
    usual:
        bill("Other day");
}
```

**String Switch:**
```platter
chars of command = "start";

menu (command) {
    choice "start":
        bill("Starting...");
        stop;
    choice "stop":
        bill("Stopping...");
        stop;
    usual:
        bill("Unknown command");
}
```

**Fall-Through Behavior:**
```platter
piece of option = 1;

menu (option) {
    choice 1:
        bill("Executing option 1");
        // No stop - will execute 2
    choice 2:
        bill("Executing option 2");
        stop;
    usual:
        bill("Default");
}
// Output: Executing option 1, then Executing option 2
```

### For Loop: pass

**Syntax:**
```platter
pass (<init>; <condition>; <update>) {
    <statements>
}
```

**Simple Count:**
```platter
pass (piece of i = 1; i <= 5; i += 1) {
    bill(i);
}
// Output: 1 2 3 4 5
```

**Backwards:**
```platter
pass (piece of i = 10; i > 0; i -= 1) {
    bill(i);
}
// Output: 10 9 8 7 6 5 4 3 2 1
```

**Array Iteration:**
```platter
piece[] of numbers = [10, 20, 30, 40, 50];

pass (piece of i = 0; i < 5; i += 1) {
    bill(numbers[i]);
}
// Output: 10 20 30 40 50
```

**Multiple Updates:**
```platter
pass (piece of i = 0, j = 10; i < 5; i += 1, j -= 1) {
    bill(i);
    bill(j);
}
```

### Do-While Loop: order/repeat

**Syntax:**
```platter
order {
    <statements>
} repeat (<condition>);
```

**Characteristics:**
- Execute body first, condition last
- Always executes at least once
- Condition checked after body

**Example:**
```platter
piece of count = 0;
order {
    bill(count);
    count = count + 1;
} repeat (count < 5);
// Output: 0 1 2 3 4
```

**User Input Simulation:**
```platter
piece of attempts = 0;
piece of maxAttempts = 3;

order {
    bill("Attempt");
    attempts = attempts + 1;
} repeat (attempts < maxAttempts);
// Executes exactly 3 times
```

### Loop Control: stop and next

**stop - Exit Loop:**
```platter
pass (piece of i = 1; i <= 10; i += 1) {
    check (i == 5) {
        stop;  // Exit when i=5
    }
    bill(i);
}
// Output: 1 2 3 4 (stops before 5)
```

**next - Skip Iteration:**
```platter
pass (piece of i = 1; i <= 5; i += 1) {
    check (i % 2 == 0) {
        next;  // Skip even numbers
    }
    bill(i);
}
// Output: 1 3 5 (skips 2, 4)
```

**In Nested Loops:**
```platter
pass (piece of i = 1; i <= 3; i += 1) {
    pass (piece of j = 1; j <= 3; j += 1) {
        check (j == 2) {
            next;  // Skips only inner loop iteration
        }
        bill(j);
    }
}
```

---

## Operators & Expressions

### Operator Precedence & Associativity

| Precedence | Operators | Type | Associativity |
|---|---|---|---|
| 1 (Highest) | `()` `[]` `.` | Postfix | Left |
| 2 | `!` `-` (unary) `+` | Prefix | Right |
| 3 | `*` `/` `%` | Multiplicative | Left |
| 4 | `+` `-` | Additive | Left |
| 5 | `<` `>` `<=` `>=` | Relational | Left |
| 6 | `==` `!=` | Equality | Left |
| 7 | `&&` | Logical AND | Left |
| 8 (Lowest) | `\|\|` | Logical OR | Left |

**Using Parentheses:**
```platter
piece of a = 2, b = 3, c = 4;

piece of result1 = a + b * c;     // 2 + (3*4) = 14
piece of result2 = (a + b) * c;   // (2+3)*4 = 20
piece of result3 = a * b + c;     // (2*3) + 4 = 10
```

### Arithmetic Operators

| Operator | Name | Operation | Example | Result |
|---|---|---|---|---|
| `+` | Addition | Add two operands | `5 + 3` | `8` |
| `-` | Subtraction | Subtract right from left | `10 - 4` | `6` |
| `*` | Multiplication | Multiply operands | `6 * 7` | `42` |
| `/` | Division | Divide left by right | `15 / 3` | `5` |
| `/` | Division (float) | Decimal division | `5 / 2` as `sip` | `2.5` |
| `%` | Modulo | Remainder of division | `17 % 5` | `2` |
| `-` | Unary Minus | Negate value | `-42` | `-42` |
| `+` | Unary Plus | Positive value | `+10` | `10` |

**Type Rules:**
- `piece + piece` → `piece`
- `sip + sip` → `sip`
- `piece + sip` → `sip`
- `sip + piece` → `sip`

**Examples:**
```platter
piece of a = 10, b = 3;
sip of x = 10.0, y = 3.0;

piece of p = a + b;        // 13
piece of q = a - b;        // 7
piece of r = a * b;        // 30
piece of s = a / b;        // 3 (integer division)
piece of t = a % b;        // 1

sip of f = x + y;          // 13.0
sip of g = x / y;          // 3.333...
sip of h = a + x;          // 20.0
```

### Relational Operators

Compare values; always return `flag` (boolean).

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `<` | Less than | `5 < 10` | `up` (true) |
| `>` | Greater than | `20 > 15` | `up` (true) |
| `<=` | Less or equal | `7 <= 7` | `up` (true) |
| `>=` | Greater or equal | `3 >= 5` | `down` (false) |
| `==` | Equal | `42 == 42` | `up` (true) |
| `!=` | Not equal | `10 != 5` | `up` (true) |

**Examples:**
```platter
piece of age = 20;
flag of isAdult = (age >= 18);    // up (true)
flag of isTeen = (age < 13);      // down (false)
flag of isExact = (age == 20);    // up (true)

chars of name = "Alice";
flag of match = (name == "Alice"); // up
```

### Logical Operators

Operate on boolean values; return `flag`.

| Operator | Meaning | Short-circuit | Example |
|---|---|---|---|
| `&&` | AND | Both must be true | `(x > 0) && (y < 10)` |
| `\|\|` | OR | At least one true | `(a == 5) \|\| (b == 5)` |
| `!` | NOT | Invert boolean | `!(flag == down)` |

**AND Truth Table:**
```
up && up = up
up && down = down
down && up = down
down && down = down
```

**OR Truth Table:**
```
up || up = up
up || down = up
down || up = up
down || down = down
```

**NOT Truth Table:**
```
!up = down
!down = up
```

**Examples:**
```platter
piece of age = 25;
piece of score = 85;

flag of eligible = (age >= 18) && (score > 80);  // Check both

check ((age < 13) || (age >= 65)) {
    bill("Special rate");
}

flag of opposite = !(age < 18);  // true if >= 18
```

**Short-Circuit Behavior:**
```platter
flag of result = down && (10 / 0);  // Second part not evaluated
flag of result2 = up || (10 / 0);   // Second part not evaluated
```

### Assignment Operators

Modify variables; all are left-associative.

| Operator | Equivalent | Example | After |
|---|---|---|---|
| `=` | Direct assignment | `x = 5` | `x` is `5` |
| `+=` | Add and assign | `x += 3` | `x = x + 3` |
| `-=` | Subtract and assign | `x -= 2` | `x = x - 2` |
| `*=` | Multiply and assign | `x *= 4` | `x = x * 4` |
| `/=` | Divide and assign | `x /= 2` | `x = x / 2` |
| `%=` | Modulo and assign | `x %= 3` | `x = x % 3` |

**Examples:**
```platter
piece of count = 10;
count += 5;     // count = 15
count -= 3;     // count = 12
count *= 2;     // count = 24
count /= 4;     // count = 6
count %= 4;     // count = 2

sip of value = 100.0;
value *= 1.5;   // value = 150.0
```

### Expression Evaluation

**Simple Expressions:**
```platter
piece of result = 2 + 3 * 4;      // 14 (multiplication first)
piece of result2 = (2 + 3) * 4;   // 20 (parentheses first)
```

**Complex Expressions:**
```platter
piece of a = 10, b = 5, c = 2;
piece of result = a + b * c - 3;  // 10 + (5*2) - 3 = 17

flag of condition = (a > b) && (b > c);  // true && true = true
flag of condition2 = (a == b) || (c < b); // false || true = true

sip of x = 3.5, y = 2.0;
sip of calc = (x * y) + (10 / y);  // (3.5*2) + (10/2) = 12.0
```

---

## Arrays & Collections

Arrays store multiple values of the same type with index-based access.

### Array Declaration

**Syntax:**
```platter
<type>[] of <name>;              // 1D array
<type>[][] of <name>;            // 2D array
<type>[][][] of <name>;          // 3D array (and so on)
```

**Examples:**
```platter
piece[] of numbers;              // 1D array of integers
sip[] of measurements;           // 1D array of floats
chars[] of words;                // 1D array of strings
flag[] of toggles;               // 1D array of booleans

piece[][] of matrix;             // 2D array (matrix)
sip[][][] of tensor;             // 3D array
```

### Array Initialization

**With Literals:**
```platter
piece[] of primes = [2, 3, 5, 7, 11, 13];
sip[] of decimals = [1.1, 2.2, 3.3];
chars[] of names = ["Alice", "Bob", "Charlie"];
flag[] of states = [up, down, up, up, down];
```

**Multi-Dimensional:**
```platter
piece[][] of matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];

sip[][] of table = [
    [1.0, 2.0],
    [3.0, 4.0],
    [5.0, 6.0]
];
```

**Empty Arrays:**
```platter
piece[] of empty;        // Uninitialized array
```

### Array Access

**Single Element:**
```platter
piece[] of numbers = [10, 20, 30, 40, 50];

piece of first = numbers[0];     // 10 (first element)
piece of second = numbers[1];    // 20
piece of last = numbers[4];      // 50 (last element)
```

**Modification:**
```platter
numbers[0] = 100;        // Change first element
numbers[2] = 35;         // Change middle element
numbers[4] = 500;        // Change last element
```

**2D Array Access:**
```platter
piece[][] of matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
];

piece of cell = matrix[0][0];    // 1
piece of cell2 = matrix[1][2];   // 6
piece of cell3 = matrix[2][1];   // 8

matrix[0][0] = 100;              // Modify element
```

**Index Expressions:**
```platter
piece[] of arr = [10, 20, 30, 40, 50];
piece of i = 2;

piece of value = arr[i];         // 30 (index from variable)
piece of value2 = arr[i + 1];    // 40 (computed index)
piece of value3 = arr[2 * 1];    // 30 (expression as index)
```

### Arrays in Functions

**Pass Array as Parameter:**
```platter
prepare piece of listSum(piece[] of numbers) {
    piece of total = 0;
    piece of length = 5;
    pass (piece of i = 0; i < length; i += 1) {
        total = total + numbers[i];
    }
    serve total;
}

start() {
    piece[] of values = [10, 20, 30, 40, 50];
    piece of result = listSum(values);  // 150
    bill(result);
}
```

**Find Maximum:**
```platter
prepare piece of findMax(piece[] of nums) {
    piece of max = nums[0];
    piece of length = 5;
    pass (piece of i = 1; i < length; i += 1) {
        check (nums[i] > max) {
            max = nums[i];
        }
    }
    serve max;
}

start() {
    piece[] of scores = [45, 92, 67, 88, 76];
    piece of highest = findMax(scores);
    bill(highest);  // 92
}
```

**Array Reversing:**
```platter
prepare chars[] of reverseArray(chars[] of input) {
    chars[] of output = ["", "", "", "", ""];
    piece of length = 5;
    piece of j = 0;
    pass (piece of i = 4; i >= 0; i -= 1) {
        output[j] = input[i];
        j = j + 1;
    }
    serve output;
}
```

### Important Array Limitations

1. **No Dynamic Size:** Arrays are fixed-size after creation
2. **Manual Length Tracking:** No built-in `.length` property
3. **Index-Based Only:** No iteration syntax like `for each`
4. **Type Consistency:** All elements must be same type

---

## Tables & Structures

Tables define custom record types that group related fields together (similar to structs in C or classes without methods).

### Table Declaration

**Syntax:**
```platter
table of <TableName> = [
    <type> of <field1>;
    <type> of <field2>;
    // ... more fields
];
```

**Example:**
```platter
table of Student = [
    chars of name;
    piece of age;
    sip of gpa;
];

table of Point = [
    piece of x;
    piece of y;
];

table of Person = [
    chars of firstName;
    chars of lastName;
    piece of birthYear;
    chars of email;
];
```

### Table Variable Declaration

```platter
Student of alice;           // Declare instance
Point of origin;            // Another instance

alice = [                   // Initialize with literal
    name = "Alice";
    age = 20;
    gpa = 3.8;
];
```

### Field Access

**Read Fields:**
```platter
chars of studentName = alice.name;  // "Alice"
piece of studentAge = alice.age;    // 20
sip of studentGpa = alice.gpa;      // 3.8
```

**Modify Fields:**
```platter
alice.age = 21;
alice.gpa = 3.9;
alice.name = "Alice Smith";
```

### Functions Returning Tables

```platter
prepare Student of createStudent(chars of n, piece of a, sip of g) {
    serve [
        name = n;
        age = a;
        gpa = g;
    ];
}

start() {
    Student of bob = createStudent("Bob", 19, 3.5);
    bill(bob.name);     // "Bob"
    bill(bob.age);      // 19
    bill(bob.gpa);      // 3.5
}
```

### Arrays of Tables

**Declare Array of Tables:**
```platter
Student[] of classList;
```

**Initialize:**
```platter
Student[] of classList = [
    [
        name = "Alice";
        age = 20;
        gpa = 3.8;
    ],
    [
        name = "Bob";
        age = 19;
        gpa = 3.5;
    ],
    [
        name = "Charlie";
        age = 21;
        gpa = 4.0;
    ]
];
```

**Access Elements:**
```platter
Student of first = classList[0];             // Alice record
chars of firstName = classList[0].name;      // "Alice"
piece of secondAge = classList[1].age;       // 19
sip of thirdGpa = classList[2].gpa;          // 4.0
```

**Iterate Through Tables:**
```platter
Student[] of roster = [
    [name = "Alice"; age = 20; gpa = 3.8;],
    [name = "Bob"; age = 19; gpa = 3.5;]
];

pass (piece of i = 0; i < 2; i += 1) {
    bill(roster[i].name);
    bill(roster[i].age);
}
```

### Nested Tables

Tables can contain other tables:

```platter
table of Address = [
    chars of street;
    chars of city;
];

table of Employee = [
    chars of name;
    piece of id;
    Address of workAddress;
];

start() {
    Employee of worker = [
        name = "John";
        id = 123;
        workAddress = [
            street = "123 Main St";
            city = "Portland";
        ];
    ];
    
    bill(worker.name);              // "John"
    bill(worker.workAddress.city);  // "Portland"
}
```

---

## Semantic Rules & Constraints

### Type Safety

Platter enforces strict compile-time type checking.

**Type Incompatibility:**
```platter
piece of x = 5;
chars of y = "hello";

piece of result = x + y;  // ❌ ERROR: Cannot add piece and chars
```

**Type Checking in Conditions:**
```platter
piece of count = 10;

check (count) {          // ❌ ERROR: check requires flag, not piece
    bill("Done");
}

check (count > 5) {      // ✅ OK: Comparison returns flag
    bill("Greater");
}
```

### Scope Rules

**No Global Shadowing:**
```platter
piece of globalX = 10;

prepare piece of calculate() {
    piece of globalX = 20;  // ❌ ERROR: Cannot shadow global
    serve globalX;
}
```

**Local Scope Only:**
```platter
prepare piece of test() {
    piece of localVar = 5;
    serve localVar;
}

start() {
    bill(localVar);        // ❌ ERROR: localVar not in scope
}
```

### Function Rules

**No Overloading:**
```platter
prepare piece of add(piece of a, piece of b) {
    serve a + b;
}

prepare sip of add(sip of a, sip of b) {  // ❌ ERROR: Duplicate function name
    serve a + b;
}
```

**All Paths Must Return:**
```platter
prepare piece of getValue(piece of x) {
    check (x > 0) {
        serve x * 2;
    }
    // Missing return for x <= 0 - may cause error
}
```

### Control Flow Constraints

**stop/next Only in Loops:**
```platter
prepare piece of bad() {
    stop;  // ❌ ERROR: stop outside of loop
    serve 0;
}

prepare piece of good() {
    pass (piece of i = 0; i < 5; i += 1) {
        check (i == 2) {
            stop;  // ✅ OK: stop inside loop
        }
    }
    serve 0;
}
```

**serve Must Match Return Type:**
```platter
prepare piece of getValue() {
    serve "hello";  // ❌ ERROR: chars doesn't match piece return type
}

prepare piece of getValue() {
    serve 42;       // ✅ OK: piece matches
}
```

---

## Complete Examples

### Example 1: Fibonacci Sequence

Calculate Fibonacci numbers with recursion:

```platter
prepare piece of fibonacci(piece of n) {
    check (n <= 1) {
        serve n;
    }
    serve fibonacci(n - 1) + fibonacci(n - 2);
}

start() {
    pass (piece of i = 0; i <= 10; i += 1) {
        piece of result = fibonacci(i);
        bill(result);
    }
}
// Output: 0 1 1 2 3 5 8 13 21 34 55
```

### Example 2: Grade Calculator with Tables

```platter
table of GradeRecord = [
    chars of studentName;
    piece of score;
    chars of grade;
];

prepare chars of getGrade(piece of score) {
    check (score >= 90) {
        serve "A";
    } alt (score >= 80) {
        serve "B";
    } alt (score >= 70) {
        serve "C";
    } alt (score >= 60) {
        serve "D";
    } instead {
        serve "F";
    }
}

prepare GradeRecord of gradeStudent(chars of name, piece of s) {
    serve [
        studentName = name;
        score = s;
        grade = getGrade(s);
    ];
}

start() {
    GradeRecord[] of results = [
        [studentName = "Alice"; score = 95; grade = "A";],
        [studentName = "Bob"; score = 87; grade = "B";],
        [studentName = "Charlie"; score = 72; grade = "C";]
    ];
    
    pass (piece of i = 0; i < 3; i += 1) {
        bill(results[i].studentName);
        bill(results[i].grade);
    }
}
```

### Example 3: Matrix Operations

```platter
prepare piece of matrixSum(piece[][] of matrix) {
    piece of total = 0;
    pass (piece of i = 0; i < 3; i += 1) {
        pass (piece of j = 0; j < 3; j += 1) {
            total = total + matrix[i][j];
        }
    }
    serve total;
}

start() {
    piece[][] of m = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ];
    
    piece of sum = matrixSum(m);
    bill(sum);  // 45
}
```

### Example 4: Prime Number Checker

```platter
prepare flag of isPrime(piece of n) {
    check (n < 2) {
        serve down;  // Not prime
    }
    
    pass (piece of i = 2; i * i <= n; i += 1) {
        check (n % i == 0) {
            serve down;  // Found divisor
        }
    }
    
    serve up;  // No divisors found
}

start() {
    piece[] of numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    
    pass (piece of i = 0; i < 10; i += 1) {
        flag of prime = isPrime(numbers[i]);
        check (prime == up) {
            bill(numbers[i]);
        }
    }
}
// Output: 2 3 5 7 11
```

### Example 5: Temperature Conversion System

```platter
table of TemperatureReading = [
    sip of celsius;
    sip of fahrenheit;
    sip of kelvin;
];

prepare TemperatureReading of convertTemperature(sip of c) {
    sip of f = (c * 9 / 5) + 32;
    sip of k = c + 273.15;
    
    serve [
        celsius = c;
        fahrenheit = f;
        kelvin = k;
    ];
}

start() {
    piece[] of tempsCelsius = [0, 25, 100];
    
    pass (piece of i = 0; i < 3; i += 1) {
        sip of c = tempsCelsius[i];
        TemperatureReading of reading = convertTemperature(c);
        
        bill(reading.celsius);
        bill(reading.fahrenheit);
        bill(reading.kelvin);
    }
}
```

### Example 6: Bubble Sort implementation

```platter
prepare piece[] of bubbleSort(piece[] of arr) {
    piece of length = 5;
    
    pass (piece of i = 0; i < length; i += 1) {
        pass (piece of j = 0; j < length - i - 1; j += 1) {
            check (arr[j] > arr[j + 1]) {
                // Swap
                piece of temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    
    serve arr;
}

start() {
    piece[] of unsorted = [64, 34, 25, 12, 22];
    piece[] of sorted = bubbleSort(unsorted);
    
    pass (piece of i = 0; i < 5; i += 1) {
        bill(sorted[i]);
    }
}
// Output: 12 22 25 34 64
```

---

## Common Patterns & Best Practices

### Pattern 1: Input Validation

```platter
prepare flag of isValidAge(piece of age) {
    check ((age >= 0) && (age <= 150)) {
        serve up;
    }
    serve down;
}

start() {
    piece of userAge = 25;
    flag of isValid = isValidAge(userAge);
    
    check (isValid == up) {
        bill("Valid age");
    } instead {
        bill("Invalid age");
    }
}
```

### Pattern 2: Counter and Accumulator

```platter
prepare piece of countMatches(piece[] of nums, piece of target) {
    piece of count = 0;
    piece of length = 5;
    
    pass (piece of i = 0; i < length; i += 1) {
        check (nums[i] == target) {
            count = count + 1;
        }
    }
    
    serve count;
}

start() {
    piece[] of numbers = [1, 2, 2, 3, 2];
    piece of matches = countMatches(numbers, 2);
    bill(matches);  // 3
}
```

### Pattern 3: Finding Element

```platter
prepare piece of findIndex(piece[] of arr, piece of target) {
    piece of length = 5;
    
    pass (piece of i = 0; i < length; i += 1) {
        check (arr[i] == target) {
            serve i;  // Return index immediately
        }
    }
    
    serve -1;  // Not found
}

start() {
    piece[] of data = [10, 20, 30, 40, 50];
    piece of idx = findIndex(data, 30);
    bill(idx);  // 2
}
```

### Pattern 4: Default Values

```platter
prepare chars of getStatus(piece of code) {
    menu (code) {
        choice 1:
            serve "Active";
        choice 2:
            serve "Inactive";
        choice 3:
            serve "Pending";
        usual:
            serve "Unknown";
    }
}

start() {
    piece of statusCode = 5;
    chars of status = getStatus(statusCode);
    bill(status);  // "Unknown"
}
```

### Pattern 5: State Machine

```platter
table of State = [
    piece of current;
    chars of description;
];

prepare State of nextState(State of current) {
    piece of next = current.current;
    menu (current.current) {
        choice 1:
            next = 2;
        choice 2:
            next = 3;
        choice 3:
            next = 1;
    }
    
    serve [
        current = next;
        description = "State " + next;
    ];
}
```

### Best Practice 1: Clear Variable Names

```platter
// ❌ Unclear
piece of a = 25;
piece of b = 1000;
flag of c = up;

// ✅ Clear
piece of userAge = 25;
piece of accountBalance = 1000;
flag of isVerified = up;
```

### Best Practice 2: Function Documentation

Use comments to explain complex logic:

```platter
// Calculate compound interest: A = P(1 + r/n)^(nt)
prepare sip of compoundInterest(sip of principal, sip of rate, piece of years) {
    // Note: Simplified without exponentiation
    sip of interest = principal * rate * years;
    sip of total = principal + interest;
    serve total;
}
```

### Best Practice 3: Bounds Checking

```platter
prepare piece of safeArrayAccess(piece[] of arr, piece of index) {
    check ((index >= 0) && (index < 5)) {
        serve arr[index];
    }
    serve -1;  // Invalid index
}
```

### Best Practice 4: Early Returns

```platter
prepare piece of processNumber(piece of n) {
    // Early exit for invalid input
    check (n < 0) {
        serve 0;
    }
    
    // Early exit for special case
    check (n == 0) {
        serve 1;
    }
    
    // Normal processing
    serve n * 2;
}
```

---

## IDE Features & Development

### Browser-Based Compiler IDE

The Platter Compiler Webapp provides a complete development environment in your web browser with real-time analysis and no server dependency.

### Core Features

**✨ Code Editor**
- Syntax highlighting for Platter syntax
- Line numbering for reference
- Automatic indentation
- Code folding for large files
- Dark/light theme support
- Keyboard bindings (Ctrl+Z undo, Ctrl+Y redo, Ctrl+F find)

**📁 File Operations**
- Create new Platter files
- Open `.platter` files from disk
- Save files locally
- Download compiled results

**🔍 Compilation Pipeline**

The IDE performs complete compilation with analysis at each stage:

1. **Lexical Analysis** - Tokenizes source code
   - Token type, value, position
   - Error detection for invalid characters

2. **Syntax Analysis** - Parses tokens into structure
   - Abstract Syntax Tree generation
   - Grammar rule validation
   - Syntax error reporting

3. **Semantic Analysis** - Type and scope checking
   - Symbol table construction
   - Type compatibility validation
   - Scope rule enforcement
   - Control flow verification

4. **Intermediate Code Generation** - TAC creation
   - Three-Address Code instructions
   - Optimization passes (constant folding, dead code elimination)

**⚡ Real-Time Validation**
- Errors update as you type
- Progressive error reporting
- Clear error messages with line references

**🎨 Output Display**
- Token stream visualization
- AST (Abstract Syntax Tree) view
- Symbol table inspection
- TAC output with optimization details

### Getting Started with IDE

1. **Write Code:** Type Platter code in the editor
2. **View Tokens:** See lexical analysis result
3. **Check Syntax:** Verify parsing without errors
4. **Analyze Semantics:** View type and scope information
5. **Generate IR:** See Three-Address Code output

### Example Workflow

```
Source Code:
    piece of count = 10;
    bill(count);

↓ Lexical Analysis

Tokens:
    keyword: piece
    keyword: of
    identifier: count
    operator: =
    number: 10
    ...

↓ Syntax Analysis

AST:
    Program
    ├── VarDecl(count, piece, 10)
    └── Call(bill, [Var(count)])

↓ Semantic Analysis

Errors: None
Symbol Table: count → piece

↓ TAC Generation

Instructions:
    t1 = 10
    count = t1
    call bill(count)
```

---

## Technical Reference

### Compilation Phases

1. **Lexer (Lexical Analyzer)**
   - Input: Raw source text
   - Output: Token stream
   - Handles: Comments, whitespace, literal parsing

2. **Parser (Syntax Analyzer)**
   - Input: Token stream
   - Output: Abstract Syntax Tree
   - Validates: Grammar rules, syntax correctness

3. **Semantic Analyzer**
   - Input: AST
   - Output: Enhanced AST with type/scope information
   - Validates: Types, scopes, control flow

4. **TAC Generator**
   - Input: Semantic AST
   - Output: Three-Address Code
   - Optimizes: Constants, dead code

### Related Documentation

For detailed technical information:

- **[AST & Parse Tree Guide](docs/AST_GUIDE.md)** - Tree structure details
- **[Grammar Specification](docs/GRAMMAR.md)** - Complete grammar rules
- **[Lexical Analysis Reference](docs/LEXER_REFERENCE.md)** - Token definitions
- **[Intermediate Code Guide](docs/INTERMEDIATE_CODE.md)** - TAC format
- **[IDE Features](docs/IDE_FEATURES.md)** - Detailed IDE capabilities

### File Organization

```
platter-compiler-webapp/
├── README.md                    (This file - Language Guide)
├── docs/
│   ├── GRAMMAR.md              (Context-free grammar)
│   ├── LEXER_REFERENCE.md      (Token types & lexical rules)
│   ├── AST_GUIDE.md            (AST node reference)
│   ├── INTERMEDIATE_CODE.md    (TAC instruction set)
│   ├── IDE_FEATURES.md         (IDE capabilities)
│   └── DOCUMENTATION_INDEX.md  (Documentation guide)
└── platter-compiler-sveltejs/
    └── static/python/app/
        ├── lexer/              (Tokenization)
        ├── parser/             (Parsing)
        ├── semantic_analyzer/  (Type & scope checking)
        └── intermediate_code/  (TAC generation)
```

---

## 🚀 Quick Reference Card

### Data Types
| Type | Keyword | Example |
|------|---------|---------|
| Integer | `piece` | `piece of x = 42;` |
| String | `chars` | `chars of s = "hi";` |
| Boolean | `flag` | `flag of b = up;` |
| Float | `sip` | `sip of f = 3.14;` |

### Control Flow
| Statement | Keyword | Usage |
|---|---|---|
| If | `check()` | Conditional execution |
| Else-if | `alt()` | Additional condition |
| Else | `instead` | Default branch |
| Switch | `menu()` | Multi-way branch |
| For Loop | `pass()` | Fixed iteration |
| Do-While | `order...repeat()` | Loop at least once |

### Operators
| Category | Operators | Example |
|---|---|---|
| Arithmetic | `+` `-` `*` `/` `%` | `a + b` |
| Relational | `<` `>` `<=` `>=` `==` `!=` | `x > 0` |
| Logical | `&&` `||` `!` | `(a > 0) && (b < 10)` |
| Assignment | `=` `+=` `-=` `*=` `/=` `%=` | `x += 5` |

### Keywords Summary
| Purpose | Keywords |
|---|---|
| Declarations | `piece`, `chars`, `flag`, `sip`, `table`, `of` |
| Functions | `prepare`, `serve` |
| Entry Point | `start` |
| Conditions | `check`, `alt`, `instead` |
| Switch | `menu`, `choice`, `usual` |
| Loops | `pass`, `order`, `repeat` |
| Control | `stop`, `next` |
| Output | `bill` |
| Boolean | `up`, `down` |

---

## 📚 Additional Resources

- **Browser IDE:** Open `index.html` in browser for development environment
- **Test Programs:** See `static/python/tests/` for example Platter code
- **Documentation:** Full technical docs in `docs/` directory
- **Architecture:** See `platter-compiler-sveltejs/README.md`

---

## 📝 License

MIT License - See LICENSE file for details

---

**Happy Cooking with Platter! 🍽️👨‍🍳**


**Platter** is a culinary-themed procedural programming language designed with an intuitive, metaphor-based syntax. Every program uses cooking-related keywords to express computational logic, making code both functional and thematic.

### Key Characteristics:
- **Procedural**: Follows imperative programming paradigm
- **Statically Typed**: Variables must be declared with explicit types
- **Compiled to TAC**: Generates Three-Address Code for execution
- **Semantic Analysis**: Comprehensive type checking and scope validation
- **No Automatic Type Conversion**: Maintains strict type safety

---

## Data Types

Platter supports four primitive data types and custom table types:

### Primitive Types

| Type | Keyword | Description | Example |
|------|---------|-------------|---------|
| **Integer** | `piece` | Whole numbers (32-bit signed) | `piece of count = 42;` |
| **String** | `chars` | Text/character sequences | `chars of name = "Alice";` |
| **Boolean** | `flag` | True/False values (`up`=true, `down`=false) | `flag of ready = up;` |
| **Floating-Point** | `sip` | Decimal numbers (double precision) | `sip of weight = 3.14;` |

### Type Literals

- **Integers**: `0`, `-5`, `100`
- **Strings**: `"Hello, World!"` (double-quoted)
- **Booleans**: `up` (true), `down` (false)
- **Floats**: `1.5`, `0.25`, `-3.14`

---

## Variables

### Global Variables

Declared at the program level (before recipes and `start()` block):

```platter
piece of globalCounter;           // Declaration only
piece of initialCount = 10;        // Declaration with initialization
chars of message = "Hello";
flag of isRunning = up;
sip of pi = 3.14159;
```

Multiple variables of the same type can be declared together:

```platter
piece of x = 5, y = 10, z;        // x=5, y=10, z=uninitialized
sip of a, b = 2.5, c = 1.0;       // a=uninitialized, b=2.5, c=1.0
```

### Local Variables

Declared within function bodies:

```platter
prepare piece of calculateSum() {
    piece of result = 0;           // Local variable
    piece of temp;                 // Local uninitialized variable
    result = result + 5;
    serve result;
}
```

### Variable Scope Rules

- **Global scope**: Accessible from any recipe
- **Local scope**: Accessible only within the recipe they're declared in
- **No shadowing allowed**: Local variables cannot have the same name as globals
- **All variables must be declared**: Implicit declarations are not permitted

---

## Functions (Recipes)

Functions in Platter are called **recipes** and use the `prepare` keyword.

### Syntax

```platter
prepare <return_type> of <recipe_name>(<param1>, <param2>, ...) {
    // recipe body
    serve <return_value>;
}
```

### Declaration Rules

- **Return type**: Must be one of the four primitive types (or a table type)
- **Parameters**: Optional; use type declarations matching variable syntax
- **Return statement**: Must use `serve` keyword
- **No overloading**: Function names must be unique

### Examples

```platter
// No parameters, returns piece
prepare piece of getNumber() {
    serve 42;
}

// Two parameters, returns piece
prepare piece of addNumbers(piece of a, piece of b) {
    serve a + b;
}

// Finds maximum of three pieces
prepare piece of maximum(piece of x, piece of y, piece of z) {
    piece of max = x;
    check (y > max) {
        max = y;
    }
    check (z > max) {
        max = z;
    }
    serve max;
}

// Returns string based on condition
prepare chars of greet(piece of hour) {
    check (hour < 12) {
        serve "Good morning";
    } alt (hour < 18) {
        serve "Good afternoon";
    } instead {
        serve "Good evening";
    }
    serve "";
}
```

### Built-in Recipe: `bill()`

The `bill()` function outputs values to console (like `print()`):

```platter
bill("Hello");                    // Print string
bill(42);                         // Print number
bill(up);                         // Print boolean
```

---

## Control Flow

### Conditional: `check`/`alt`/`instead`

Platter uses `check`, `alt` (else-if), and `instead` (else) for conditionals.

**Syntax:**
```platter
check (<condition>) {
    // statements
} alt (<condition>) {
    // statements
} instead {
    // statements
}
```

**Example:**
```platter
prepare piece of categorize(piece of score) {
    check (score >= 90) {
        serve 4;
    } alt (score >= 80) {
        serve 3;
    } alt (score >= 70) {
        serve 2;
    } alt (score >= 60) {
        serve 1;
    } instead {
        serve 0;
    }
}
```

### Switch: `menu`/`choice`/`usual`

Use `menu` for switch-case statements with `choice` for cases and `usual` for default.

**Syntax:**
```platter
menu (<expression>) {
    choice <value1>:
        // statements
    choice <value2>:
        // statements
    usual:
        // statements
}
```

**Example:**
```platter
prepare chars of getDayName(piece of day) {
    menu (day) {
        choice 1:
            serve "Monday";
        choice 2:
            serve "Tuesday";
        choice 3:
            serve "Wednesday";
        usual:
            serve "Unknown";
    }
    serve "";
}

// Switch on strings too
menu (command) {
    choice "start":
        bill("Starting...");
    choice "stop":
        bill("Stopping...");
    usual:
        bill("Unknown command");
}
```

**Flow Control in Switch:**
- `stop`: Exits the switch (like `break`)
- Without `stop`: Falls through to next case
- `usual` serves as the default case

### Loop: `pass` (For Loop)

Use `pass` for traditional for-loop-style iteration.

**Syntax:**
```platter
pass (<init>; <condition>; <update>) {
    // statements
}
```

**Example:**
```platter
prepare piece of sum(piece of n) {
    piece of total = 0;
    pass (piece of i = 1; i <= n; i += 1) {
        total = total + i;
    }
    serve total;
}

// Countdown
start() {
    pass (piece of x = 10; x > 0; x -= 1) {
        bill(x);
    }
}
```

### Loop: `order`/`repeat` (Do-While Loop)

Execute statements first, then check condition.

**Syntax:**
```platter
order {
    // statements
} repeat (<condition>);
```

**Example:**
```platter
prepare piece of factorial(piece of n) {
    piece of result = 1;
    pass (piece of i = 2; i <= n; i += 1) {
        result = result * i;
    }
    serve result;
}

// Using order/repeat
start() {
    piece of count = 0;
    order {
        bill(count);
        count = count + 1;
    } repeat (count < 5);
}
```

### Loop Control: `stop` and `next`

- `stop`: Exits the current loop (like `break`)
- `next`: Skips to the next iteration (like `continue`)

```platter
// Using stop
pass (piece of i = 1; i <= 10; i += 1) {
    check (i == 5) {
        stop;  // Exit loop when i equals 5
    }
    bill(i);
}

// Using next
pass (piece of i = 1; i <= 10; i += 1) {
    check (i % 2 == 0) {
        next;  // Skip even numbers
    }
    bill(i);  // Print only odd numbers
}
```

---

## Operators

### Arithmetic Operators

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `+` | Addition | `5 + 3` | `8` |
| `-` | Subtraction | `10 - 4` | `6` |
| `*` | Multiplication | `6 * 7` | `42` |
| `/` | Division | `15 / 3` | `5` |
| `%` | Modulo | `17 % 5` | `2` |

**Type Rules:**
- Operations on `piece` return `piece`
- Operations on `sip` return `sip`
- Mixed `piece`/`sip` operations return `sip`
- String concatenation not supported via `+`

### Relational Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `<` | Less than | `x < 10` |
| `>` | Greater than | `y > 5` |
| `<=` | Less than or equal | `count <= 100` |
| `>=` | Greater than or equal | `age >= 18` |
| `==` | Equal | `status == up` |
| `!=` | Not equal | `flag != down` |

**Result Type:** Always `flag` (boolean)

### Logical Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `&&` | Logical AND | `(x > 0) && (y < 10)` |
| `\|\|` | Logical OR | `(flag == up) \|\| (counter > 99)` |
| `!` | Logical NOT | `!(flag == down)` |

**Result Type:** Always `flag`

### Assignment Operators

| Operator | Example | Equivalent |
|----------|---------|------------|
| `=` | `x = 5;` | Assignment |
| `+=` | `x += 3;` | `x = x + 3` |
| `-=` | `x -= 2;` | `x = x - 2` |
| `*=` | `x *= 4;` | `x = x * 4` |
| `/=` | `x /= 2;` | `x = x / 2` |
| `%=` | `x %= 3;` | `x = x % 3` |

---

## Arrays

Arrays store multiple values of the same type in a single variable.

### Array Declaration

```platter
piece[] of numbers;                      // 1D array
sip[][] of matrix;                       // 2D array
chars[] of words;                        // Array of strings
flag[] of toggles;                       // Array of booleans
```

### Array Initialization

```platter
piece[] of primes = [2, 3, 5, 7, 11];
sip[][] of table = [
    [1.0, 2.0, 3.0],
    [4.0, 5.0, 6.0]
];
chars[] of colors = ["red", "green", "blue"];
flag[] of states = [up, down, up];
```

### Array Access

```platter
piece of first = primes[0];               // Get element at index 0
piece of second = primes[1];              // Get element at index 1

sip of cell = matrix[0][1];               // 2D array access

primes[2] = 13;                           // Modify element
matrix[1][0] = 99.5;                      // 2D modification
```

### Array in Functions

```platter
prepare piece of listSum(piece[] of numbers) {
    piece of total = 0;
    piece of length = 5;  // Hardcoded for example
    pass (piece of i = 0; i < length; i += 1) {
        total = total + numbers[i];
    }
    serve total;
}

start() {
    piece[] of values = [10, 20, 30, 40, 50];
    piece of result = listSum(values);
    bill(result);  // Output: 150
}
```

---

## Tables

Tables are custom record types that group related fields (like structs in C or classes in OOP).

### Table Definition

```platter
table of Student = [
    chars of name;
    piece of age;
    sip of gpa;
];
```

### Using Tables

```platter
// Declare table variable
Student of alice;

// Initialize in function
prepare Student of createStudent() {
    serve [
        name = "Alice";
        age = 20;
        gpa = 3.8;
    ];
}

// Access fields
start() {
    Student of bob = createStudent();
    bill(bob.name);     // Output: "Alice"
    bill(bob.age);      // Output: 20
    bill(bob.gpa);      // Output: 3.8
    
    bob.age = 21;       // Modify field
    bill(bob.age);      // Output: 21
}
```

### Arrays of Tables

```platter
Student[] of classList = [
    [
        name = "Alice";
        age = 20;
        gpa = 3.8;
    ],
    [
        name = "Bob";
        age = 21;
        gpa = 3.5;
    ]
];

start() {
    bill(classList[0].name);  // Output: "Alice"
    bill(classList[1].age);   // Output: 21
}
```

---

## Built-in Functions

### Output: `bill()`

Outputs a value to console.

```platter
bill("Hello, Platter!");
bill(42);
bill(up);                    // Prints: up
bill(3.14);
```

### Return: `serve`

Returns a value from a recipe. Acts like `return` in other languages.

```platter
prepare piece of double(piece of x) {
    serve x * 2;  // Return 2*x
}

prepare chars of reverseGreeting() {
    serve "Goodbye";
}
```

### Loop Control: `stop`

Exits from a loop or switch statement immediately.

```platter
pass (piece of i = 0; i < 100; i += 1) {
    check (i == 50) {
        stop;  // Exit loop
    }
    bill(i);
}
```

### Loop Control: `next`

Skips the current iteration and continues with the next.

```platter
pass (piece of i = 1; i <= 5; i += 1) {
    check (i % 2 == 0) {
        next;  // Skip even numbers
    }
    bill(i);  // Output: 1, 3, 5
}
```

---

## Complete Examples

### Example 1: Fibonacci Sequence

```platter
prepare piece of fibonacci(piece of n) {
    check (n <= 1) {
        serve n;
    }
    serve fibonacci(n - 1) + fibonacci(n - 2);
}

start() {
    bill(fibonacci(10));  // Output: 55
}
```

### Example 2: Grade Calculator

```platter
prepare chars of getGrade(piece of score) {
    check (score >= 90) {
        serve "A";
    } alt (score >= 80) {
        serve "B";
    } alt (score >= 70) {
        serve "C";
    } instead {
        serve "F";
    }
    serve "X";
}

start() {
    piece of myScore = 85;
    chars of grade = getGrade(myScore);
    bill(grade);  // Output: B
}
```

### Example 3: Array Processing

```platter
prepare piece of findMax(piece[] of nums) {
    piece of max = nums[0];
    pass (piece of i = 1; i < 5; i += 1) {
        check (nums[i] > max) {
            max = nums[i];
        }
    }
    serve max;
}

start() {
    piece[] of values = [3, 7, 2, 9, 5];
    piece of maximum = findMax(values);
    bill(maximum);  // Output: 9
}
```

### Example 4: Temperature Converter

```platter
prepare sip of celsiusToFahrenheit(sip of celsius) {
    serve (celsius * 9 / 5) + 32;
}

start() {
    sip of tempC = 25;
    sip of tempF = celsiusToFahrenheit(tempC);
    bill(tempF);  // Output: 77.0
}
```

### Example 5: Table Usage

```platter
table of Book = [
    chars of title;
    chars of author;
    piece of year;
];

prepare Book of createBook() {
    serve [
        title = "To Kill a Mockingbird";
        author = "Harper Lee";
        year = 1960;
    ];
}

start() {
    Book of myBook = createBook();
    bill(myBook.title);     // Output: To Kill a Mockingbird
    bill(myBook.author);    // Output: Harper Lee
    bill(myBook.year);      // Output: 1960
}
```

---

## IDE Features

The Platter Compiler Webapp provides a modern, browser-based development environment:

### ✨ Core Features

- **Browser-Based**: Runs completely in your browser, no server required
- **Lexical Analysis**: Tokenize Platter code with detailed token information
- **Syntax Analysis**: Parse and validate code structure
- **Semantic Analysis**: Type checking, scope validation, and error detection
- **Intermediate Code**: Generate and view Three-Address Code (TAC)
- **File Operations**: Open and save `.platter` files
- **Modern UI**: Dark/light theme support
- **Syntax Highlighting**: Automatic code formatting and highlighting
- **Real-time Validation**: Instant error reporting as you type

### Performance

- **Fast**: All analysis runs client-side via WebAssembly (Pyodide)
- **No Server**: Zero latency, works offline
- **Optimized IR**: Constant folding, dead code elimination, strength reduction

---

## Quick Start

### Windows

```cmd
Platter-Start.bat
```

### Command Line

```bash
npm start
# Edit files in:
platter-compiler-sveltejs/static/python/app/lexer/
platter-compiler-sveltejs/static/python/app/parser/

# Refresh browser to see changes - no build needed!
```

### Testing
```bash
npm run test              # Python unit tests (runs automatically)
npm run test:frontend     # E2E tests
```

**Note**: The test command automatically runs Python unit tests using unittest. No Python environment setup required!

### Building
```bash
npm run build            # Build for production
npm run preview          # Preview build locally
```

Deploy `platter-compiler-sveltejs/build/` to any static host.

## 🛠️ Technology Stack

- **Frontend**: SvelteKit 2.x, Tailwind CSS 4.x
- **Editor**: CodeMirror 5
- **Python Runtime**: Pyodide 0.29.x (WebAssembly)
- **Build Tool**: Vite 7.x

## 📖 Documentation

- [Architecture.md](Architecture.md) - Technical architecture details
- [platter-compiler-sveltejs/README.md](platter-compiler-sveltejs/README.md) - Frontend docs
- [platter-compiler-sveltejs/python-dev/README.md](platter-compiler-sveltejs/python-dev/README.md) - Python development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes in `platter-compiler-sveltejs/static/python/app/`
4. Test your changes
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## ❓ FAQ

**Q: Do I need Python installed?**  
A: Yes for the backend. The FastAPI server runs the compiler pipeline and interpreter.

**Q: Why is the first analysis slow?**  
A: The backend starts the Python runtime on first request and may warm caches. Subsequent runs are faster.

**Q: Can I deploy to GitHub Pages?**  
A: Yes! Run `npm run build` and deploy the `platter-compiler-sveltejs/build/` directory.

**Q: Where is the backend?**  
A: In the root-level backend/ folder. Start it with Uvicorn (see backend/requirements.txt).
