# Platter Compiler: Lexer Flow Guide

## Overview

The lexer is the first compiler stage that reads raw source text and turns it into a stream of tokens.

In Platter, the lexer is implemented as a hand-written state machine split across several mixin classes. Its job is to:

1. scan characters left to right
2. group them into valid lexemes
3. classify each lexeme into a token type
4. attach line and column positions
5. report invalid characters or malformed lexemes early

The high-level flow is:

```text
Raw Source Text
   ->
Character-by-Character Scanning
   ->
Lexeme Recognition
   ->
Token Objects
   ->
Parser Input
```

In the full compiler pipeline:

```text
Source -> Lexer -> Tokens -> Parser -> AST -> Semantic Analysis -> IR
```

---

## Entry Point

**File:** `platter-compiler-sveltejs/static/python/app/lexer/lexer.py`  
**Class:** `Lexer`  
**Main methods:** `s0()` and `tokenize()`

### Core Loop

```python
def tokenize(self):
    tokens = []
    while self.current is not None:
        tok = self.s0()
        if not tok:
            break
        if isinstance(tok, list):
            tokens.extend(tok)
        else:
            tokens.append(tok)
    return tokens
```

### What This Means

- `tokenize()` repeatedly asks `s0()` for the next token
- scanning stops only when `self.current` becomes `None`
- most states return one `Token`
- some error paths return a list of tokens, so `tokenize()` is written to support both

### Code-Level Flow Inside `Lexer`

When reading the lexer code, the control flow is:

```text
tokenize()
   ->
s0()
   ->
one scanner family
   ->
one accepting/error state
   ->
Token
```

What that means in practice:

1. `tokenize()` drives the whole scan loop.
2. `s0()` looks only at the current first character and decides which scanner should try to consume the next lexeme.
3. That scanner advances through the source until it reaches either:
   - an accepting state, or
   - an error state
4. The accepting state builds the final `Token` using the saved start position.

---

## Core Data Structures

### Token

**File:** `lexer/token.py`

Every recognized lexeme becomes a `Token` object:

```python
Token(type_, value, line, col)
```

### Stored Fields

- `type`: token category such as `id`, `piece_lit`, `check`, `+`, `(`
- `value`: original lexeme text
- `line`: source line where the token starts
- `col`: source column where the token starts

### Error Token Types

The lexer can emit:

- `Invalid Character`
- `Invalid Lexeme`
- `Invalid Lexeme Exceeds`
- `Invalid Reserved Word Delimeter`

These are still tokens, which lets later tooling inspect exactly where lexical failure happened.

---

## Lexer Architecture

The `Lexer` class is built by combining several smaller components:

```python
class Lexer(
    LexerBase,
    LexerKeywords,
    LexerOperators,
    LexerIdentifier,
    LexerCharCom,
    LexerNumericals
)
```

### Component Responsibilities

- `base.py`:
  - cursor movement
  - line/column tracking
  - saved start position
  - delimiter tables
  - shared character classes
- `keywords.py`:
  - reserved words and keyword-like built-ins
- `operators.py`:
  - operators, punctuation, whitespace tokens
- `identifiers.py`:
  - identifiers and identifier length limits
- `char_com.py`:
  - string literals and comments
- `numericals.py`:
  - integer and decimal literals

This is a manually written DFA-style lexer: states are encoded as methods like `s1`, `s205`, `s354`, and so on.

---

## Shared Scanning State

### File

`lexer/base.py`

### Important Fields

```python
self.text
self.pos
self.line
self.col
self.start_pos
self.start_line
self.start_col
self.current
```

### Meaning

- `pos`: current index in the source text
- `line`, `col`: current cursor position
- `start_*`: where the current candidate lexeme began
- `current`: current character under inspection, or `None` at EOF

### Important Helpers

#### `advance()`

Moves one character forward and updates line/column correctly.

If the current character is a newline:

- `line += 1`
- `col = 1`

Otherwise:

- `col += 1`

#### `save_start()`

Marks the beginning of the next potential token.

#### `restore()`

Returns the cursor to the previously saved token start.

This is crucial because keyword recognition tries many paths first and may need to backtrack before falling back to identifier scanning.

#### `get_lexeme()`

Returns the exact source substring from `start_pos` up to the current cursor.

#### `_match_delimiter(delimiters)`

Checks whether the current character is a valid delimiter for an accepting state.

Delimiter checking is one of the most important parts of this lexer.

---

## Stage 1: Dispatch in `s0()`

`s0()` is the master dispatcher.

It begins every token scan with:

```python
self.save_start()
```

Then it chooses which scanner to try based on the first character.

### Dispatch Order

#### Keyword entry letters

`a, b, c, d, f, i, m, n, o, p, r, s, t, u`

These branch into keyword-recognition states first.

#### Operators

`+ - * / % > < = !`

#### Whitespace and punctuation

- space
- tab
- newline
- `, : ; ( ) [ ] { }`

#### General categories

- identifiers: alphabetic or underscore
- numerics: `0` or nonzero digit
- strings: `"`
- comments: `#`

#### Fallback

If no rule matches:

```python
tok = Token(Token.InvalidCharacter, self.current, self.start_line, self.start_col)
self.advance()
```

So unknown characters become `Invalid Character` tokens and the lexer continues.

What this code block does:

- saves the starting position for the next lexeme
- tries reserved-word scanners before identifier scanning
- routes punctuation and operators to their own DFA states
- handles strings, comments, and numerics only when the starting character makes them possible
- guarantees that every character is either consumed into a token or turned into an error token

---

## Stage 2: Keyword Recognition

### File

`lexer/keywords.py`

### Strategy

Reserved words are recognized before general identifiers.

For example, when scanning `check`, `s0()` sees the first character `c` and calls `s19()`. That state machine tries to follow the exact keyword path:

```text
c -> ch -> che -> chec -> check
```

If the full reserved word matches and the next character is a valid delimiter, the lexer emits:

```python
Token("check", "check", line, col)
```

If the path fails, it calls `restore()` and returns `None`, allowing `s0()` to fall back to identifier scanning.

What this code does:

- speculatively tries the reserved-word path
- rewinds if the word is not actually a keyword
- prevents keywords and identifiers from being recognized by two independent passes
- uses delimiter checks to enforce that reserved words only appear in legal contexts

### Reserved Delimiter Rule

A reserved word is only accepted if the next character is allowed for that word.

Examples from the implementation:

- `check` requires `paren_dlm`
- `append` requires `paren_dlm`
- `next` requires `term_dlm`
- `chars`, `piece`, `sip`, `flag` require `dtype_dlm`

If the word text matches but the delimiter is illegal, the lexer emits:

```python
Token(Token.InvalidLexemeReserved, ...)
```

This prevents malformed reserved-word usage from silently turning into identifiers.

### Examples

#### Valid

```platter
check(
append(
piece[
next;
```

#### Invalid reserved-word delimiter

```platter
checkx
nextx
piece$
```

If the suffix is not a valid identifier continuation but still violates the reserved-word delimiter rule, the lexer reports it as a reserved-word delimiter error rather than a normal identifier.

### Keyword and Reserved Token Examples

The keyword machine recognizes tokens such as:

- `alt`
- `and`
- `append`
- `bill`
- `chars`
- `check`
- `choice`
- `copy`
- `cut`
- `fact`
- `flag`
- `instead`
- `matches`
- `menu`
- `next`
- `not`
- `or`
- `pass`
- `piece`
- `pow`
- `prepare`
- `rand`
- `remove`
- `repeat`
- `serve`
- `sip`
- `size`
- `sort`
- `sqrt`
- `start`
- `stop`
- `table`
- `take`
- `tochars`
- `topiece`
- `tosip`
- `up`
- `down`
- `usual`

The boolean literals `up` and `down` are emitted as:

- `flag_lit`

rather than plain keyword tokens.

---

## Stage 3: Identifier Recognition

### File

`lexer/identifiers.py`

### Token Type

Identifiers emit:

```python
Token("id", lexeme, line, col)
```

### Allowed Characters

The lexer uses:

```python
self.id_chars = self.alphanumeric + self.underscore
```

So an identifier may contain:

- lowercase letters
- uppercase letters
- digits
- underscore

### Start Characters

Because `s0()` only enters identifier scanning when:

```python
self.current in (self.alpha + self.underscore)
```

an identifier must start with:

- a letter, or
- `_`

but not a digit.

### Length Limit

The identifier scanner is manually unrolled into states `s257` through `s306`.

It accepts up to a fixed maximum length. If the identifier continues past the last allowed state, it emits:

```python
Token(Token.InvalidLexemeExceeds, ...)
```

What this code does:

- grows the identifier one character at a time
- checks after each step whether the lexeme may already end
- rejects overly long identifiers immediately instead of consuming an arbitrary-length name first

So very long identifiers are rejected lexically rather than later.

### Identifier Delimiters

An identifier is only accepted when followed by a valid identifier delimiter such as whitespace, punctuation, operators, or comment start.

If an illegal character appears after the identifier body, the lexer emits:

- `Invalid Lexeme`

### Example

```platter
student_count
_temp1
Point
```

All of these become `id` if they are not matched first as reserved words.

---

## Stage 4: Numeric Literal Recognition

### File

`lexer/numericals.py`

### Literal Token Types

- `piece_lit` for integer literals
- `sip_lit` for decimal literals

### Integer Scanning

Integers are recognized through a chain of states that count digits explicitly.

Examples:

```platter
0
7
12345
```

become `piece_lit`.

### Decimal Scanning

If the lexer encounters a `.` after the integer part, it enters decimal scanning and requires at least one digit after the decimal point.

Examples:

```platter
3.14
0.5
12.3456789
```

become `sip_lit`.

### Length Limits

The implementation enforces:

- up to 15 whole-number digits for `piece_lit`
- up to 7 fractional digits for `sip_lit`

If the number continues past those limits, the lexer emits:

- `Invalid Lexeme Exceeds`

### Delimiter Rule

Numeric literals are only accepted when followed by a valid numeric delimiter.

If an illegal trailing character appears, the lexer emits:

- `Invalid Lexeme`

### Negative Numbers

A useful implementation detail:

The minus state in `operators.py` can hand control directly to the numeric states.

That means source like:

```platter
-42
-3.5
```

is lexed as a single numeric literal token rather than two tokens `-` and number.

This behavior depends on what character follows `-`:

- if followed by `=` -> `-=`
- if followed by a digit -> numeric literal path
- otherwise -> normal `-` operator path

What this code does:

- makes `-` context-sensitive at the lexical level
- allows signed literals to be emitted as a single token
- avoids forcing the parser to always reconstruct negative numeric literals from two tokens

---

## Stage 5: Operators and Delimiters

### File

`lexer/operators.py`

### Arithmetic Operators

- `+`
- `-`
- `*`
- `/`
- `%`

### Compound Assignment

- `+=`
- `-=`
- `*=`
- `/=`
- `%=`

### Relational / Equality Operators

- `>`
- `>=`
- `<`
- `<=`
- `=`
- `==`
- `!=`

### Important Note About `!`

Plain `!` is not accepted as its own token.

The lexer only accepts:

```platter
!=
```

If `!` appears alone, it becomes:

- `Invalid Lexeme`

### Whitespace Tokens

The lexer emits whitespace as explicit tokens:

- `space`
- `tab`
- `newline`

Later stages often filter these out before parsing.

### Punctuation Tokens

- `,`
- `:`
- `;`
- `(`
- `)`
- `[`
- `]`
- `{`
- `}`

Each of these also uses delimiter validation to reject malformed adjacency patterns when required by the current formal specification.

---

## Stage 6: String Literal Recognition

### File

`lexer/char_com.py`

### Token Type

```python
Token("chars_lit", ...)
```

### Syntax

Strings must begin and end with double quotes:

```platter
"hello"
"Platter"
```

### Allowed Contents

Inside the string, the lexer accepts:

- printable ASCII characters except unescaped `\` and `"`
- escape sequences introduced by backslash

### Escape Handling

When the lexer sees `\`, it enters `s355()` and expects one following ASCII character, then resumes normal string scanning.

So forms like these are allowed lexically:

```platter
"line\nbreak"
"quote: \""
```

The lexer validates the shape of the escape, not the semantic meaning of every escape sequence.

### Unterminated or Malformed Strings

If EOF is reached before the closing `"`, or if an illegal character is found, the lexer emits:

- `Invalid Lexeme`

---

## Stage 7: Comment Recognition

### File

`lexer/char_com.py`

### Single-Line Comments

Single-line comments begin with:

```platter
# 
```

That is: `#` followed immediately by a space.

Then the lexer consumes characters until newline or EOF and emits:

```python
Token("comment_single", ...)
```

### Multi-Line Comments

Multi-line comments begin with:

```platter
###
```

The lexer then scans until it finds another closing:

```platter
###
```

and emits:

```python
Token("comment_multi", ...)
```

### Important Implementation Detail

A lone `#` that is not followed by either:

- a space, or
- another `#`

is treated as:

- `Invalid Lexeme`

So comment syntax is strict.

What this code does:

- distinguishes comment forms immediately from the second character
- keeps single-line and multi-line comment logic separate
- treats malformed comment starters as lexical errors instead of silently ignoring them

---

## Position Tracking Flow

Every token remembers where it started.

The process is:

1. `s0()` calls `save_start()`
2. the chosen state machine advances through the lexeme
3. the accepting state builds the token using `start_line` and `start_col`

Example:

```platter
piece of x = 5;
```

Possible token starts:

- `piece` at line 1, col 1
- `of` at line 1, col 7
- `x` at line 1, col 10
- `=` at line 1, col 12
- `5` at line 1, col 14

This position information is what later parser and semantic error reporting relies on.

---

## Error Flow

The lexer can fail in several different ways.

### 1. Invalid Character

If `s0()` cannot classify the current character at all:

```python
Token(Token.InvalidCharacter, self.current, ...)
```

Example:

```platter
piece of x = 5 € ;
```

If `€` is not recognized, it becomes `Invalid Character`.

### 2. Invalid Lexeme

Used when a token started in a valid category but became malformed before acceptance.

Examples:

- malformed operator
- unterminated string
- invalid comment start
- illegal trailing character after a literal

### 3. Invalid Lexeme Exceeds

Used when a valid token shape exceeds an implementation limit.

Examples:

- identifier too long
- integer too many digits
- decimal too many fractional digits

### 4. Invalid Reserved Word Delimeter

Used when a reserved word text is followed by an illegal delimiter.

This is how the lexer protects keyword boundaries.

---

## Example Walkthrough

### Source

```platter
piece of x = -12;
bill("hello");
# note
```

### Step 1: `piece`

- `s0()` sees `p`
- keyword automaton in `keywords.py` matches `piece`
- delimiter is valid
- emits:

```text
Token("piece", "piece", 1, 1)
```

### Step 2: space and `of`

- space becomes `space`
- `of` is recognized as reserved word token

### Step 3: identifier `x`

- `s0()` sees `x`
- no keyword branch exists for `x`
- falls to identifier scanner
- emits:

```text
Token("id", "x", 1, 10)
```

### Step 4: `=`

- operator scanner emits `=`

### Step 5: `-12`

- `s0()` sees `-`
- minus state sees a digit next
- control is redirected to numeric scanning
- emits:

```text
Token("piece_lit", "-12", 1, 14)
```

### Step 6: `bill("hello");`

- `bill` is recognized as keyword/built-in token
- `(` is recognized
- `"hello"` becomes `chars_lit`
- `)` and `;` are recognized

### Step 7: comment

- `# ` begins a single-line comment
- lexer consumes until newline or EOF
- emits `comment_single`

### Resulting Token Stream

If whitespace and comments are kept:

```text
piece, space, of, space, id, space, =, space, piece_lit, ;,
newline,
bill, (, chars_lit, ), ;,
newline,
comment_single
```

If whitespace/comments are filtered for parsing, only the parser-relevant tokens remain.

---

## Integration with the Rest of the Compiler

### In `main.py`

The compiler runs:

```python
lexer = Lexer(source)
tokens = lexer.tokenize()
```

Then it usually filters out:

- `comment`
- `space`
- `newline`
- `tab`

before parsing.

### Why This Matters

The lexer itself is richer than the parser input stream:

- lexer output preserves formatting/comment tokens if needed
- parser usually receives a cleaned token stream
- diagnostics can still refer back to lexer-produced positions

---

## File Reference

| Component | File | Responsibility |
|-----------|------|----------------|
| Main dispatcher | `lexer/lexer.py` | Chooses which token machine to run |
| Shared state/helpers | `lexer/base.py` | Cursor, line/col tracking, delimiters |
| Token structure | `lexer/token.py` | Token object and lexical error token names |
| Protocol/type contract | `lexer/protocol.py` | Shared lexer interface and fields |
| Reserved words | `lexer/keywords.py` | Keyword DFA states |
| Operators/punctuation | `lexer/operators.py` | Operator and symbol states |
| Identifiers | `lexer/identifiers.py` | Identifier scanning and length limit |
| Numerics | `lexer/numericals.py` | Integer and decimal literal scanning |
| Strings/comments | `lexer/char_com.py` | `chars_lit`, single-line, multi-line comments |

---

## Relationship to the Other Guides

- [SYNTAX_FLOW_GUIDE.md](./SYNTAX_FLOW_GUIDE.md) explains the valid source-level forms built from the tokens described here.
- [AST_FLOW_GUIDE.md](./AST_FLOW_GUIDE.md) explains how the parser transforms the token stream into AST nodes.
- [SYMBOL_TABLE_FLOW_GUIDE.md](./SYMBOL_TABLE_FLOW_GUIDE.md) explains how declarations from the AST are collected into scopes and symbols.
- [SEMANTIC_FLOW_GUIDE.md](./SEMANTIC_FLOW_GUIDE.md) explains how the compiler validates meaning after tokenization and parsing.
- [IR_FLOW_GUIDE.md](./IR_FLOW_GUIDE.md) explains how the validated AST is lowered into intermediate code.

Together, the pipeline is:

```text
Source -> Lexer -> Tokens -> Parser -> AST -> Symbol Table -> Semantic Validation -> IR
```
