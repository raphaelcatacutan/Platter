"""
Code Emitter for Platter Virtual Machine

Outputs generated code in various formats:
- Assembly text format
- Binary bytecode
- JSON representation
- HTML formatted output
"""

import json
from typing import List, Dict, Any
from .target_instructions import CodeSection, TargetInstruction, OpCode


class CodeEmitter:
    """Emits target code in various formats"""
    
    def __init__(self, code_section: CodeSection):
        self.code_section = code_section
    
    def emit_text(self, include_addresses: bool = True) -> str:
        """Emit code as text assembly format"""
        lines = []
        lines.append("; Platter Virtual Machine Code")
        lines.append(f"; Section: {self.code_section.name}")
        lines.append(f"; Instructions: {len(self.code_section)}")
        lines.append("")
        
        for i, instr in enumerate(self.code_section):
            if include_addresses:
                line = f"{i:4d}: {instr}"
            else:
                line = str(instr)
            lines.append(line)
        
        return "\n".join(lines)
    
    def emit_bytecode(self) -> bytes:
        """Emit code as binary bytecode"""
        bytecode = bytearray()
        
        # Header (magic number + version)
        bytecode.extend(b'PLAT')  # Magic number
        bytecode.extend(b'\x01\x00')  # Version 1.0
        
        # Number of instructions
        num_instructions = len(self.code_section)
        bytecode.extend(num_instructions.to_bytes(4, 'little'))
        
        # Encode each instruction
        for instr in self.code_section:
            bytecode.extend(self._encode_instruction(instr))
        
        return bytes(bytecode)
    
    def _encode_instruction(self, instr: TargetInstruction) -> bytes:
        """Encode single instruction to bytes"""
        data = bytearray()
        
        # Opcode (1 byte)
        opcode_value = self._opcode_to_byte(instr.opcode)
        data.append(opcode_value)
        
        # Operands (variable length, null-terminated strings)
        if instr.operand1:
            data.extend(str(instr.operand1).encode('utf-8'))
            data.append(0)  # Null terminator
        
        if instr.operand2:
            data.extend(str(instr.operand2).encode('utf-8'))
            data.append(0)
        
        if instr.operand3:
            data.extend(str(instr.operand3).encode('utf-8'))
            data.append(0)
        
        return bytes(data)
    
    def _opcode_to_byte(self, opcode: OpCode) -> int:
        """Convert opcode to byte value"""
        opcode_map = {
            OpCode.PUSH: 0x01,
            OpCode.POP: 0x02,
            OpCode.LOAD_LOCAL: 0x10,
            OpCode.STORE_LOCAL: 0x11,
            OpCode.LOAD_GLOBAL: 0x12,
            OpCode.STORE_GLOBAL: 0x13,
            OpCode.ADD: 0x20,
            OpCode.SUB: 0x21,
            OpCode.MUL: 0x22,
            OpCode.DIV: 0x23,
            OpCode.MOD: 0x24,
            OpCode.NEG: 0x25,
            OpCode.EQ: 0x30,
            OpCode.NE: 0x31,
            OpCode.LT: 0x32,
            OpCode.LE: 0x33,
            OpCode.GT: 0x34,
            OpCode.GE: 0x35,
            OpCode.AND: 0x40,
            OpCode.OR: 0x41,
            OpCode.NOT: 0x42,
            OpCode.JUMP: 0x50,
            OpCode.JUMP_IF_TRUE: 0x51,
            OpCode.JUMP_IF_FALSE: 0x52,
            OpCode.LABEL: 0x53,
            OpCode.CALL: 0x60,
            OpCode.RETURN: 0x61,
            OpCode.ENTER: 0x62,
            OpCode.LEAVE: 0x63,
            OpCode.HALT: 0xFF,
            OpCode.NOP: 0x00,
            OpCode.COMMENT: 0xFE,
        }
        return opcode_map.get(opcode, 0x00)
    
    def emit_json(self) -> str:
        """Emit code as JSON"""
        data = {
            'section': self.code_section.name,
            'instruction_count': len(self.code_section),
            'labels': self.code_section.labels,
            'instructions': []
        }
        
        for i, instr in enumerate(self.code_section):
            instr_data = {
                'address': i,
                'opcode': instr.opcode.value,
                'operands': []
            }
            
            if instr.operand1 is not None:
                instr_data['operands'].append(str(instr.operand1))
            if instr.operand2 is not None:
                instr_data['operands'].append(str(instr.operand2))
            if instr.operand3 is not None:
                instr_data['operands'].append(str(instr.operand3))
            
            if instr.comment:
                instr_data['comment'] = instr.comment
            
            data['instructions'].append(instr_data)
        
        return json.dumps(data, indent=2)
    
    def emit_html(self) -> str:
        """Emit code as formatted HTML"""
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html>')
        html.append('<head>')
        html.append('    <meta charset="UTF-8">')
        html.append('    <title>Platter VM Code</title>')
        html.append('    <style>')
        html.append('        body { font-family: "Courier New", monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }')
        html.append('        .container { max-width: 1200px; margin: 0 auto; }')
        html.append('        h1 { color: #4ec9b0; }')
        html.append('        .stats { background: #252526; padding: 15px; border-radius: 5px; margin: 20px 0; }')
        html.append('        .code { background: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 5px; padding: 15px; }')
        html.append('        .instruction { margin: 2px 0; }')
        html.append('        .address { color: #858585; margin-right: 10px; }')
        html.append('        .opcode { color: #569cd6; font-weight: bold; }')
        html.append('        .operand { color: #ce9178; }')
        html.append('        .comment { color: #6a9955; font-style: italic; }')
        html.append('        .label { color: #dcdcaa; font-weight: bold; }')
        html.append('    </style>')
        html.append('</head>')
        html.append('<body>')
        html.append('    <div class="container">')
        html.append(f'        <h1>Platter Virtual Machine Code</h1>')
        html.append('        <div class="stats">')
        html.append(f'            <strong>Section:</strong> {self.code_section.name}<br>')
        html.append(f'            <strong>Instructions:</strong> {len(self.code_section)}<br>')
        html.append(f'            <strong>Labels:</strong> {len(self.code_section.labels)}')
        html.append('        </div>')
        html.append('        <div class="code">')
        
        for i, instr in enumerate(self.code_section):
            html.append('            <div class="instruction">')
            html.append(f'                <span class="address">{i:4d}:</span>')
            
            if instr.opcode == OpCode.LABEL:
                html.append(f'                <span class="label">{instr.operand1}:</span>')
            elif instr.opcode == OpCode.COMMENT:
                html.append(f'                <span class="comment">; {instr.operand1}</span>')
            else:
                html.append(f'                <span class="opcode">{instr.opcode.value}</span>')
                
                if instr.operand1 is not None:
                    html.append(f'                <span class="operand">{instr.operand1}</span>')
                if instr.operand2 is not None:
                    html.append(f'                <span class="operand">, {instr.operand2}</span>')
                if instr.operand3 is not None:
                    html.append(f'                <span class="operand">, {instr.operand3}</span>')
                
                if instr.comment:
                    html.append(f'                <span class="comment">  ; {instr.comment}</span>')
            
            html.append('            </div>')
        
        html.append('        </div>')
        html.append('    </div>')
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)
    
    def emit_statistics(self) -> str:
        """Generate code statistics"""
        lines = []
        lines.append("="*70)
        lines.append("CODE GENERATION STATISTICS")
        lines.append("="*70)
        
        lines.append(f"\nSection: {self.code_section.name}")
        lines.append(f"Total Instructions: {len(self.code_section)}")
        lines.append(f"Labels: {len(self.code_section.labels)}")
        
        # Count instruction types
        opcode_counts: Dict[str, int] = {}
        for instr in self.code_section:
            opcode = instr.opcode.value
            opcode_counts[opcode] = opcode_counts.get(opcode, 0) + 1
        
        lines.append("\nInstruction Distribution:")
        for opcode in sorted(opcode_counts.keys()):
            count = opcode_counts[opcode]
            percentage = (count / len(self.code_section)) * 100
            lines.append(f"  {opcode:15} {count:4d} ({percentage:5.1f}%)")
        
        lines.append("\nLabel Table:")
        for label, address in sorted(self.code_section.labels.items(), key=lambda x: x[1]):
            lines.append(f"  {label:20} -> {address:4d}")
        
        lines.append("="*70)
        
        return "\n".join(lines)
    
    def save_to_file(self, filename: str, format: str = 'text'):
        """Save code to file"""
        if format == 'text' or format == 'asm':
            content = self.emit_text()
            mode = 'w'
        elif format == 'bytecode' or format == 'bin':
            content = self.emit_bytecode()
            mode = 'wb'
        elif format == 'json':
            content = self.emit_json()
            mode = 'w'
        elif format == 'html':
            content = self.emit_html()
            mode = 'w'
        else:
            raise ValueError(f"Unknown format: {format}")
        
        with open(filename, mode) as f:
            f.write(content)


def save_code(code_section: CodeSection, base_filename: str):
    """
    Convenience function to save code in multiple formats
    
    Args:
        code_section: Generated code section
        base_filename: Base filename (without extension)
    """
    emitter = CodeEmitter(code_section)
    
    # Save in different formats
    emitter.save_to_file(f"{base_filename}.asm", 'text')
    emitter.save_to_file(f"{base_filename}.json", 'json')
    emitter.save_to_file(f"{base_filename}.html", 'html')
    emitter.save_to_file(f"{base_filename}.bin", 'bytecode')
    
    print(f"[OK] Code saved to:")
    print(f"  - {base_filename}.asm  (Assembly text)")
    print(f"  - {base_filename}.json (JSON format)")
    print(f"  - {base_filename}.html (HTML format)")
    print(f"  - {base_filename}.bin  (Binary bytecode)")
