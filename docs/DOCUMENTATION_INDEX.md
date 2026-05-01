# Platter Compiler Documentation

Complete documentation for the Platter programming language compiler and IDE.

## 📚 Documentation Guide

### User Documentation

- **[Platter Language User Guide](../README.md)** - Comprehensive guide to the Platter programming language
  - Language syntax and semantics
  - Data types (piece, chars, flag, sip)
  - Functions and recipes
  - Control flow statements
  - Operators and expressions
  - Arrays and tables
  - Complete code examples

### Technical Documentation

#### Intermediate Representation & Compilation

- **[Intermediate Code Generation](INTERMEDIATE_CODE.md)** - Overview of TAC (Three-Address Code) generation
  - TAC instruction types
  - Three-address code format
  - Intermediate representation structure
  - Optimization passes

#### Parser & AST

- **[AST & Parse Tree Guide](AST_GUIDE.md)** - Understanding Abstract Syntax Trees
  - AST node structure
  - Parse tree relationships
  - Grammar specification
  - AST construction rules

- **[Syntax Flow Guide](../platter-compiler-sveltejs/docs/SYNTAX_FLOW_GUIDE.md)** - Parser-aligned language flow reference
  - Top-level program order
  - Global, local, recipe, and `start()` syntax
  - Arrays, tables, accessors, and built-ins
  - Control-flow and parser-specific gotchas

#### Language Specification

- **[Lexical Analysis Reference](LEXER_REFERENCE.md)** - Tokenization and lexical rules
  - Token types and classifications
  - Keywords and identifiers
  - Literal formats
  - Comment syntax

- **[Grammar Specification](GRAMMAR.md)** - Context-free grammar for Platter
  - Production rules
  - Precedence and associativity
  - Parsing algorithm

### Architecture Documentation

- **[Compiler Architecture](../platter-compiler-sveltejs/README.md)** - Overview of the compiler structure
  - Frontend components (Lexer, Parser, Semantic Analyzer)
  - Intermediate code generation
  - IDE integration

### IDE Features

- **[Browser IDE Features](IDE_FEATURES.md)** - Web-based development environment
  - Code editor capabilities
  - Real-time analysis
  - Error reporting

## 🚀 Getting Started

New to Platter? Start with:

1. **[Platter Language User Guide](../README.md)** - Learn the language syntax
2. **[Quick Examples](#quick-examples)** - See working code samples
3. **Language Features** - Understand datatypes, functions, and control flow

## 📋 Quick Reference

### Data Types
| Type | Keyword | Purpose |
|------|---------|---------|
| Integer | `piece` | Whole numbers |
| String | `chars` | Text data |
| Boolean | `flag` | True/false values |
| Float | `sip` | Decimal numbers |
| Record | `table` | Structured data |

### Keywords
| Keyword | Usage |
|---------|-------|
| `prepare` | Define a function/recipe |
| `start()` | Entry point/main function |
| `serve` | Return from function |
| `check` | If condition |
| `alt` | Else-if condition |
| `instead` | Else condition |
| `menu` | Switch statement |
| `choice` | Case in switch |
| `usual` | Default case |
| `pass` | For loop |
| `repeat` | Loop control (do-while) |
| `order` | Do-while block |
| `bill` | Print to output |
| `stop` | Break from loop |
| `next` | Continue to next iteration |
| `up` | Boolean true |
| `down` | Boolean false |

## 📖 Documentation Sections

### Language Concepts

1. **Type System**
   - Primitive types
   - Array types
   - Table (struct) types
   - Type compatibility

2. **Functions & Recipes**
   - Function declaration
   - Parameters and return types
   - Scope rules
   - Recursion

3. **Control Flow**
   - Conditional statements
   - Switch statements
   - Loop constructs
   - Loop control flow

4. **Data Structures**
   - Arrays (1D and multi-dimensional)
   - Tables (records)
   - Nested structures

### Compiler Implementation

1. **Lexical Analysis**
   - Tokenization process
   - Token classifications
   - Whitespace and comments

2. **Syntax Analysis**
   - Parsing algorithms
   - Abstract syntax tree construction
   - Error recovery

3. **Semantic Analysis**
   - Symbol table construction
   - Scope checking
   - Type checking
   - Control flow validation

4. **Code Generation**
   - Intermediate code generation
   - Optimization passes
   - Code output

## 🔗 Related Resources

- [GitHub Repository](https://github.com/your-org/platter-compiler-webapp)
- [Web IDE](https://your-domain.com)
- [Issue Tracker](https://github.com/your-org/platter-compiler-webapp/issues)

## 📝 Document Maintenance

Documentation is maintained in the `docs/` directory. Please keep documentation synchronized with code changes.

### Contributing Documentation

1. Write clear, concise documentation
2. Include code examples where appropriate
3. Update the index when adding new documents
4. Ensure examples are tested
5. Follow Markdown formatting standards

---

Last Updated: March 2026
