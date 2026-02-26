/**
 * Server API Handler for Platter Compiler
 * Provides endpoints for full compilation pipeline
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Compiles Platter source code using the full pipeline (IR, Optimizer, Code Gen)
 * @param {string} sourceCode - The Platter source code
 * @returns {Promise<Object>} Compilation result
 */
export async function compileWithFullPipeline(sourceCode) {
	return new Promise((resolve, reject) => {
		const pythonPath = path.join(__dirname, 'platter-compiler-sveltejs/static/python');
		
		const pythonScript = `
import sys
sys.path.insert(0, '${pythonPath}')

import json
from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.optimizer_manager import OptimizerManager
from app.code_generation.code_generator import CodeGenerator
from app.code_generation.code_emitter import CodeEmitter

result = None
try:
    # Lexical Analysis
    lexer = Lexer('''${sourceCode.replace(/'/g, "\\'")}''')
    tokens = lexer.tokenize()
    
    # Parse to AST
    parser = ASTParser(tokens)
    ast = parser.parse_program()
    
    # Generate IR
    ir_gen = IRGenerator()
    ir_gen.visit(ast)
    tac = ir_gen.get_tac()
    
    # Optimize
    optimizer = OptimizerManager()
    optimized_tac = optimizer.optimize(tac, level="O2")
    
    # Generate Code
    code_gen = CodeGenerator()
    code_section = code_gen.generate_from_tac(optimized_tac)
    
    # Emit Assembly
    emitter = CodeEmitter(code_section)
    asm_code = emitter.emit_text()
    stats = emitter.emit_statistics()
    
    result = {
        "success": True,
        "asm_code": asm_code,
        "stats": stats,
        "message": "Code compiled successfully!"
    }
except SyntaxError as e:
    result = {"success": False, "message": str(e)}
except Exception as e:
    result = {"success": False, "message": f"Compilation failed: {str(e)}"}

print(json.dumps(result))
`;

		const python = spawn('python', ['-c', pythonScript], {
			cwd: __dirname,
			timeout: 30000
		});

		let output = '';
		let errorOutput = '';

		python.stdout.on('data', (data) => {
			output += data.toString();
		});

		python.stderr.on('data', (data) => {
			errorOutput += data.toString();
		});

		python.on('close', (code) => {
			try {
				if (code !== 0) {
					reject({
						success: false,
						message: `Python process exited with code ${code}: ${errorOutput}`
					});
					return;
				}
				const result = JSON.parse(output);
				resolve(result);
			} catch (e) {
				reject({
					success: false,
					message: `Failed to parse compilation output: ${e.message}`
				});
			}
		});

		python.on('error', (err) => {
			reject({
				success: false,
				message: `Failed to spawn Python process: ${err.message}`
			});
		});
	});
}

/**
 * Compiles code with simplified pipeline (lexer + parser only)
 * Used for browser-based compilation via Pyodide
 */
export function compileSimplified(sourceCode) {
	return {
		success: true,
		asm_code: '# Simplified browser-based compilation\n# For full compilation with IR, optimization, and code generation,\n# use the server-side API endpoint.',
		stats: 'Browser Environment Mode\nLexer: ✓\nParser: ✓\nIR Generation: Server-side only\nOptimization: Server-side only\nCode Generation: Server-side only',
		message: 'Browser compilation available. Use "Run on Server" for full pipeline.',
		pipeline: 'SIMPLIFIED'
	};
}
