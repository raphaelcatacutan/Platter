/**
 * Pyodide Python Runtime Initialization
 * Handles loading and setting up the Python environment
 */

import { loadScript } from '$lib/utils/browser';

// List of Python files to load from static directory
const PYTHON_FILES = [
	'/python/app/__init__.py',
	'/python/app/lexer/__init__.py',
	'/python/app/lexer/token.py',
	'/python/app/lexer/protocol.py',
	'/python/app/lexer/base.py',
	'/python/app/lexer/keywords.py',
	'/python/app/lexer/identifiers.py',
	'/python/app/lexer/numericals.py',
	'/python/app/lexer/operators.py',
	'/python/app/lexer/char_com.py',
	'/python/app/lexer/lexer.py',
	'/python/app/parser/__init__.py',
	'/python/app/parser/error_handler.py',
	'/python/app/parser/predict_set.py',
	'/python/app/parser/parser_program.py',
	'/python/app/utils/FileHandler.py',
	'/python/app/parser/first_set.py',
	'/python/app/semantic_analyzer/__init__.py',
	'/python/app/semantic_analyzer/semantic_analyzer.py',
	'/python/app/semantic_analyzer/builtin_recipes.py',
	'/python/app/semantic_analyzer/ast/__init__.py',
	'/python/app/semantic_analyzer/ast/ast_nodes.py',
	'/python/app/semantic_analyzer/ast/ast_parser_program.py',
	'/python/app/semantic_analyzer/ast/ast_reader.py',
	'/python/app/semantic_analyzer/symbol_table/__init__.py',
	'/python/app/semantic_analyzer/symbol_table/types.py',
	'/python/app/semantic_analyzer/symbol_table/symbol_table.py',
	'/python/app/semantic_analyzer/symbol_table/symbol_table_builder.py',
	'/python/app/semantic_analyzer/symbol_table/symbol_table_output.py',
	'/python/app/semantic_analyzer/semantic_passes/__init__.py',
	'/python/app/semantic_analyzer/semantic_passes/error_handler.py',
	'/python/app/semantic_analyzer/semantic_passes/type_checker.py',
	'/python/app/semantic_analyzer/semantic_passes/scope_checker.py',
	'/python/app/semantic_analyzer/semantic_passes/control_flow_checker.py',
	'/python/app/semantic_analyzer/semantic_passes/function_checker.py',
	'/python/app/intermediate_code/__init__.py',
	'/python/app/intermediate_code/tac.py',
	'/python/app/intermediate_code/quadruple.py',
	'/python/app/intermediate_code/ir_generator.py',
	'/python/app/intermediate_code/output_formatter.py',
	'/python/app/intermediate_code/optimizer.py',
	'/python/app/intermediate_code/constant_folding.py',
	'/python/app/intermediate_code/propagation.py',
	'/python/app/intermediate_code/dead_code_elimination.py',
	'/python/app/intermediate_code/algebraic_simplification.py',
	'/python/app/intermediate_code/optimizer_manager.py',
	'/python/app/intermediate_code/ir_interpreter.py'
];

export class PyodideManager {
	private pyodide: any = null;
	private loading = false;
	private ready = false;

	get isReady(): boolean {
		return this.ready;
	}

	get isLoading(): boolean {
		return this.loading;
	}

	get instance(): any {
		return this.pyodide;
	}

	async initialize(basePath: string, onError?: (message: string) => void): Promise<void> {
		if (this.pyodide || this.loading) return;
		this.loading = true;

		try {
			// Load Pyodide from CDN
			await loadScript('https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js');
			this.pyodide = await (window as any).loadPyodide({
				indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/'
			});

			// Fetch and write Python files to Pyodide's virtual filesystem
			for (const file of PYTHON_FILES) {
				const response = await fetch(`${basePath}${file}`);
				if (!response.ok) {
					throw new Error(`Failed to load Python file: ${file} (HTTP ${response.status})`);
				}
				const content = await response.text();
				const path = file.replace('/python/', '');

				// Create directory structure
				const dirs = path.split('/').slice(0, -1);
				let currentPath = '';
				for (const dir of dirs) {
					currentPath += (currentPath ? '/' : '') + dir;
					try {
						this.pyodide.FS.mkdir(currentPath);
					} catch (e) {
						// Directory might already exist
					}
				}

				// Write file
				this.pyodide.FS.writeFile(path, content);
			}

			this.ready = true;
			console.log('Pyodide initialized successfully');
		} catch (err) {
			console.error('Failed to initialize Pyodide:', err);
			if (onError) {
				onError('Failed to initialize Python runtime');
			}
		} finally {
			this.loading = false;
		}
	}
}

export const pyodideManager = new PyodideManager();
