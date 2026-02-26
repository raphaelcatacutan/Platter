# Code Generation Module

Comprehensive code generation system for the Platter compiler that converts optimized intermediate representation into executable target code for the Platter Virtual Machine.

## Overview

The code generation module is the final phase of the compiler pipeline:

```
Source Code → Lexer → Parser → AST → IR → Optimizer → Code Generator → Target Code
```

This module generates stack-based virtual machine code that can be:
- Executed by the Platter VM
- Saved as assembly text
- Compiled to binary bytecode
- Exported as JSON for analysis

## Architecture

### Components

```
code_generation/
├── target_instructions.py    # VM instruction set
├── memory_allocator.py        # Variable memory management
├── code_generator.py          # IR to target code conversion
├── code_emitter.py            # Output in multiple formats
└── code_generation_examples.py # Usage demonstrations
```

## Platter Virtual Machine (VM)

### VM Architecture

- **Stack-based**: Operations work on an operand stack
- **Memory model**: Global and local variable spaces
- **Function support**: Call stack with parameters and return values
- **Type system**: Supports piece (int), sip (float), flag (bool), chars (string)

### Instruction Set

#### Stack Operations
| Instruction | Description | Example |
|------------|-------------|---------|
| `PUSH value` | Push value onto stack | `PUSH 10` |
| `POP` | Pop value from stack | `POP` |
| `DUP` | Duplicate top value | `DUP` |
| `SWAP` | Swap top two values | `SWAP` |

#### Memory Operations
| Instruction | Description | Example |
|------------|-------------|---------|
| `LOADL var` | Load local variable | `LOADL x` |
| `STOREL var` | Store to local variable | `STOREL x` |
| `LOADG var` | Load global variable | `LOADG g_counter` |
| `STOREG var` | Store to global variable | `STOREG g_counter` |

#### Arithmetic Operations
| Instruction | Description | Stack Effect |
|------------|-------------|--------------|
| `ADD` | Addition | `a, b → a+b` |
| `SUB` | Subtraction | `a, b → a-b` |
| `MUL` | Multiplication | `a, b → a*b` |
| `DIV` | Division | `a, b → a/b` |
| `MOD` | Modulo | `a, b → a%b` |
| `NEG` | Negate | `a → -a` |

#### Comparison Operations
| Instruction | Description | Stack Effect |
|------------|-------------|--------------|
| `EQ` | Equal | `a, b → a==b` |
| `NE` | Not equal | `a, b → a!=b` |
| `LT` | Less than | `a, b → a<b` |
| `LE` | Less or equal | `a, b → a<=b` |
| `GT` | Greater than | `a, b → a>b` |
| `GE` | Greater or equal | `a, b → a>=b` |

#### Logical Operations
| Instruction | Description | Stack Effect |
|------------|-------------|--------------|
| `AND` | Logical AND | `a, b → a&&b` |
| `OR` | Logical OR | `a, b → a\|\|b` |
| `NOT` | Logical NOT | `a → !a` |

#### Control Flow
| Instruction | Description | Example |
|------------|-------------|---------|
| `LABEL name` | Define label | `LABEL L1` |
| `JUMP label` | Unconditional jump | `JUMP L1` |
| `JT label` | Jump if true | `JT L1` |
| `JF label` | Jump if false | `JF L1` |

#### Function Operations  
| Instruction | Description | Example |
|------------|-------------|---------|
| `ENTER func n` | Function prologue | `ENTER main 5` |
| `LEAVE` | Function epilogue | `LEAVE` |
| `CALL func n` | Call function | `CALL factorial 1` |
| `RETURN flag` | Return from function | `RETURN 1` |

#### Special Instructions
| Instruction | Description | Example |
|------------|-------------|---------|
| `HALT` | Stop execution | `HALT` |
| `NOP` | No operation | `NOP` |
| `COMMENT text` | Comment (ignored) | `COMMENT Loop start` |

## Usage

### Basic Code Generation

```python
from app.code_generation import CodeGenerator, CodeEmitter

# Assume we have optimized TAC instructions
code_gen = CodeGenerator()
code_section = code_gen.generate_from_tac(tac_instructions)

# Emit as text
emitter = CodeEmitter(code_section)
assembly_code = emitter.emit_text()
print(assembly_code)
```

### Complete Compilation Pipeline

```python
from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code import IRGenerator, OptimizerManager, OptimizationLevel
from app.code_generation import CodeGenerator, CodeEmitter, save_code

# Source code
source = """
start() {
    piece of x = 10;
    piece of y = 20;
    piece of sum = x + y;
    serve sum;
}
"""

# Compile
lexer = Lexer(source)
tokens = lexer.tokenize()

ast_parser = ASTParser(tokens)
ast = ast_parser.parse_program()

ir_gen = IRGenerator()
tac, quads = ir_gen.generate(ast)

optimizer = OptimizerManager(OptimizationLevel.STANDARD)
optimized_tac = optimizer.optimize_tac(tac)

code_gen = CodeGenerator()
code_section = code_gen.generate_from_tac(optimized_tac)

# Save in multiple formats
save_code(code_section, "output/program")
# Creates: program.asm, program.json, program.html, program.bin
```

### Generated Code Example

Input Platter Code:
```platter
start() {
    piece of x = 10;
    piece of y = 20;
    piece of sum = x + y;
    serve sum;
}
```

Generated VM Code:
```assembly
   0: COMMENT  === Platter Program ===
   1: COMMENT  Generated from TAC
   2: COMMENT  
   3: LABEL    func_start                     # Function: start
   4: ENTER    start 3                        # 3 local variables
   5: PUSH     10                             # x = 10
   6: STOREL   x
   7: PUSH     20                             # y = 20
   8: STOREL   y
   9: LOADL    x                              # Load x
  10: LOADL    y                              # Load y
  11: ADD                                     # x + y
  12: STOREL   sum                            # Store to sum
  13: LOADL    sum                            # Load return value
  14: RETURN   1                              # return sum
  15: LEAVE                                   # End of start
  16: HALT                                    # End of program
```

## Memory Allocation

### Variable Scopes

```python
from app.code_generation import MemoryAllocator, Scope

allocator = MemoryAllocator()

# Global variable
allocator.allocate_global("g_counter", "piece")

# Function scope
allocator.enter_function("main")
allocator.allocate_local("x", "piece")
allocator.allocate_local("array", "piece", is_array=True, size=10)
allocator.allocate_parameter("param1", "piece")
allocator.allocate_temporary("t0")
allocator.exit_function()

# Print allocation table
allocator.print_allocation_table()
```

Output:
```
======================================================================
VARIABLE ALLOCATION TABLE
======================================================================

Globals:
  g_counter:piece @0 (global)

Locals:
  x:piece @0 (local)
  array:piece[10] @1 (local)
  param1:piece @0 (parameter)
  t0:piece @0 (temporary)

Statistics:
  Total variables: 5
  Global variables: 1
  Local variables: 11
  Parameters: 1
  Temporaries: 1
======================================================================
```

## Code Emission Formats

### 1. Assembly Text (.asm)

Human-readable assembly format with addresses and comments.

```python
emitter = CodeEmitter(code_section)
asm_code = emitter.emit_text(include_addresses=True)
with open("output.asm", "w") as f:
    f.write(asm_code)
```

### 2. Binary Bytecode (.bin)

Compact binary format for VM execution.

```python
bytecode = emitter.emit_bytecode()
with open("output.bin", "wb") as f:
    f.write(bytecode)
```

Bytecode format:
```
Header:
  - Magic: "PLAT" (4 bytes)
  - Version: 1.0 (2 bytes)
  - Instruction count (4 bytes)

Instructions:
  - Opcode (1 byte)
  - Operands (null-terminated strings)
```

### 3. JSON Format (.json)

Structured format for analysis and debugging.

```python
json_code = emitter.emit_json()
with open("output.json", "w") as f:
    f.write(json_code)
```

Example JSON:
```json
{
  "section": "main",
  "instruction_count": 16,
  "labels": {
    "func_start": 3
  },
  "instructions": [
    {
      "address": 0,
      "opcode": "COMMENT",
      "operands": ["=== Platter Program ==="]
    },
    {
      "address": 5,
      "opcode": "PUSH",
      "operands": ["10"],
      "comment": "x = 10"
    }
  ]
}
```

### 4. HTML Format (.html)

Formatted HTML with syntax highlighting.

```python
html_code = emitter.emit_html()
with open("output.html", "w") as f:
    f.write(html_code)
```

Features:
- Syntax highlighting for opcodes, operands, comments
- Instruction addresses
- Label visualization
- Statistics panel

## Code Statistics

```python
stats = emitter.emit_statistics()
print(stats)
```

Output:
```
======================================================================
CODE GENERATION STATISTICS
======================================================================

Section: main
Total Instructions: 16
Labels: 1

Instruction Distribution:
  ADD                4 (25.0%)
  COMMENT            3 (18.8%)
  ENTER              1 ( 6.2%)
  HALT               1 ( 6.2%)
  LABEL              1 ( 6.2%)
  LEAVE              1 ( 6.2%)
  LOADL              3 (18.8%)
  PUSH               2 (12.5%)
  RETURN             1 ( 6.2%)
  STOREL             3 (18.8%)

Label Table:
  func_start       ->    3
======================================================================
```

## Optimization Impact

Code generation works best with optimized IR:

### Without Optimization
```assembly
  0: PUSH     2
  1: PUSH     3
  2: ADD
  3: STOREL   t0                     # Temporary
  4: LOADL    t0                     # Unnecessary load
  5: STOREL   x
  6: LOADL    x
  7: PUSH     0
  8: ADD                             # x + 0
  9: STOREL   y
```

### With Optimization (O2)
```assembly
  0: PUSH     5                      # Constant folded (2+3)
  1: STOREL   x                      # Direct assignment
  2: LOADL    x                      # Copy propagated
  3: STOREL   y                      # Algebraic simplified (x+0 = x)
```

## Advanced Features

### CustomInstruction Builder

```python
from app.code_generation import InstructionBuilder, CodeSection

section = CodeSection("custom")

# Build instructions fluently
section.emit(InstructionBuilder.comment("Start of custom code"))
section.emit(InstructionBuilder.push("42", "Answer to everything"))
section.emit(InstructionBuilder.store_var("answer", "global"))
section.emit(InstructionBuilder.label("loop_start"))
section.emit(InstructionBuilder.load_var("counter", "local"))
section.emit(InstructionBuilder.push("1"))
section.emit(InstructionBuilder.binary_op("+", "Increment counter"))
section.emit(InstructionBuilder.jump("loop_start"))
```

### Label Resolution

The code generator automatically resolves labels:

```python
# IR contains symbolic labels
tac_goto = TACGoto("L5")

# Generated code uses correct addresses
# JUMP L5  →  JUMP 42  (if L5 is at address 42)
```

### Function Call Convention

```assembly
# Caller
PUSH 10                # Push argument
PUSH 20                # Push argument
CALL func_add 2        # Call with 2 arguments
STOREL result          # Store return value

# Callee (func_add)
func_add:
ENTER func_add 1       # 1 local variable
LOADL param_0          # Load first parameter
LOADL param_1          # Load second parameter
ADD
RETURN 1               # Return with value
LEAVE
```

## Error Handling

The code generator handles various edge cases:

```python
try:
    code_gen = CodeGenerator()
    code_section = code_gen.generate_from_tac(tac_instructions)
except Exception as e:
    print(f"Code generation error: {e}")
```

Common issues:
- Undefined variables → Automatically allocated as temporaries
- Missing return statements → Implicit return added
- Unreachable code → Passed through (optimizer should remove)

## Performance Considerations

- **Code size**: Optimized IR produces ~20-40% smaller target code
- **Generation speed**: Linear O(n) in number of IR instructions
- **Memory usage**: Proportional to variable count and instruction count
- **Label resolution**: O(1) lookup after initial O(n) construction

## Integration with VM

The generated code is designed for the Platter Virtual Machine:

### VM Execution Model

1. **Initialization**: Load bytecode, setup memory
2. **Main loop**: Fetch-decode-execute cycle
3. **Stack operations**: Push/pop operand stack
4. **Memory access**: Load/store from variable space
5. **Control flow**: Jump instruction pointer
6. **Function calls**: Manage call stack
7. **Termination**: HALT instruction

### VM Memory Layout

```
+------------------+
| Global Variables |  Fixed addresses
+------------------+
| Call Stack       |  Dynamic growth
+------------------+
| Local Variables  |  Per-function frame
+------------------+
| Operand Stack    |  Evaluation stack
+------------------+
```

## Examples

See [code_generation_examples.py](code_generation_examples.py) for comprehensive examples:

1. **Simple Arithmetic** - Basic operations
2. **Conditional Statements** - If-else control flow
3. **Loops** - While/repeat loops
4. **Optimization Comparison** - Impact of optimization on code size
5. **File Output** - Saving code in multiple formats

Run examples:
```bash
cd app/code_generation
python code_generation_examples.py
```

## Future Enhancements

Potential improvements:

1. **Register Allocation**: Use virtual registers instead of pure stack
2. **Instruction Selection**: Pattern matching for efficient code sequences
3. **Peephole Optimization**: Local optimization on generated code
4. **Debug Information**: Source line mappings, symbol tables
5. **Target Backends**: x86, ARM, WASM code generation
6. **JIT Compilation**: Runtime code generation

## API Reference

### CodeGenerator

```python
class CodeGenerator:
    def generate_from_tac(instructions: List[TACInstruction]) -> CodeSection
    def generate_from_quads(quad_table: QuadrupleTable) -> CodeSection
```

### CodeEmitter

```python
class CodeEmitter:
    def emit_text(include_addresses: bool = True) -> str
    def emit_bytecode() -> bytes
    def emit_json() -> str
    def emit_html() -> str
    def emit_statistics() -> str
    def save_to_file(filename: str, format: str)
```

### MemoryAllocator

```python
class MemoryAllocator:
    def allocate_global(name, data_type, is_array, size) -> Variable
    def allocate_local(name, data_type, is_array, size) -> Variable
    def allocate_parameter(name, data_type) -> Variable
    def allocate_temporary(temp_name) -> Variable
    def get_variable(name) -> Optional[Variable]
    def enter_function(func_name)
    def exit_function()
```

## Version

Current Version: 1.0.0

## Authors

Platter Compiler Team
