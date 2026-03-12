/**
 * Code Analyzer
 * Orchestrates lexical, syntax, and semantic analysis
 */

import type { Token, TermMsg, AnalysisResult, LexerRow } from './types';
import {
	SEMANTIC_PYTHON_SCRIPT,
	SYNTAX_PYTHON_SCRIPT,
	LEXICAL_PYTHON_SCRIPT
} from './pythonScripts';

export interface AnalyzerContext {
	pyodide: any;
	pyodideReady: boolean;
	codeInput: string;
	errorIcon: string;
	checkIcon: string;
	accumulatedInputs?: string[];
	onAddErrorMarkers: (errors: Token[]) => void;
	onClearErrorMarkers: () => void;
	onSetTerminalOk: (message: string) => void;
	onSetTerminalError: (message: string) => void;
	onClearTerminal: () => void;
	onSetTerminalMessages?: (messages: TermMsg[]) => void;
	onAppendTerminalMessages?: (messages: TermMsg[]) => void;
}

/**
 * Group consecutive whitespace tokens for cleaner display
 */
function groupWhitespaceTokens(tokens: Token[]): LexerRow[] {
	const lexerRows: LexerRow[] = [];
	let i = 0;

	while (i < tokens.length) {
		const t = tokens[i];
		const tokenType = t.type.toLowerCase();

		if (tokenType === 'space' || tokenType === 'newline' || tokenType === 'tab') {
			let count = 1;
			let nextIdx = i + 1;

			while (nextIdx < tokens.length && tokens[nextIdx].type.toLowerCase() === tokenType) {
				const currentToken = tokens[i + count - 1];
				const nextToken = tokens[nextIdx];

				const hasGap =
					nextToken.line > currentToken.line + 1 ||
					(nextToken.line === currentToken.line && nextToken.col > currentToken.col + 1);

				if (hasGap) break;

				count++;
				nextIdx++;
			}

			const displayToken = count > 1 ? `${t.type} (${count})` : t.type;
			lexerRows.push({ lexeme: t.value ?? '', token: displayToken });
			i += count;
		} else {
			lexerRows.push({ lexeme: t.value ?? '', token: t.type });
			i++;
		}
	}

	return lexerRows;
}

/**
 * Format lexical error messages
 */
function formatLexicalErrors(invalidTokens: Token[], errorIcon: string): TermMsg[] {
	const combinedErrors: TermMsg[] = [];

	for (const current of invalidTokens) {
		let errorText = '';

		if (current.type === 'Invalid Character') {
			errorText = `Error at line ${current.line} col ${current.col} - Invalid Character: ${current.value}`;
		} else if (current.type === 'Invalid Reserved Word Delimeter') {
			errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: Invalid delimiter for reserved word '${current.value}'`;
		} else if (current.type === 'Invalid Identifier') {
			errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} cannot be an identifier`;
		} else if (current.type === 'Invalid Lexeme') {
			errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value}`;
		} else if (current.type.toLowerCase().startsWith('exceeds')) {
			const firstChar = current.value?.charAt(0) || '';
			const isIdentifier = /[a-zA-Z_]/.test(firstChar);
			const isLiteral = /[0-9]/.test(firstChar);

			let limitType = '';
			if (isIdentifier) {
				limitType = 'id';
			} else if (isLiteral) {
				limitType = 'piece/sip literal';
			} else {
				limitType = 'value';
			}

			errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} exceeds ${limitType} limit`;
		} else {
			errorText = `Error at line ${current.line} col ${current.col} - ${current.type}: ${current.value}`;
		}

		combinedErrors.push({
			icon: errorIcon,
			text: errorText
		});
	}

	return combinedErrors;
}

/**
 * Perform lexical analysis
 */
export async function analyzeLexical(
	context: AnalyzerContext,
	skipLogging = false
): Promise<AnalysisResult & { tokens?: Token[]; lexerRows?: LexerRow[] }> {
	const { pyodide, pyodideReady, codeInput, errorIcon, checkIcon } = context;
	let analysisStatus: 'success' | 'error' = 'error';
	let terminalOutput = '';

	if (!codeInput) {
		const errorMsg = 'Editor is empty';
		if (!skipLogging) context.onSetTerminalError(errorMsg);
		return { status: 'error', output: errorMsg };
	}

	if (!pyodideReady) {
		const errorMsg = 'Python runtime not ready. Please wait...';
		if (!skipLogging) context.onSetTerminalError(errorMsg);
		return { status: 'error', output: errorMsg };
	}

	try {
		pyodide.globals.set('code_input', codeInput);

		const tokensProxy = await pyodide.runPythonAsync(LEXICAL_PYTHON_SCRIPT);
		const received = tokensProxy.toJs({ dict_converter: Object.fromEntries });

		const invalidTokens = received.filter(
			(t: Token) =>
				typeof t.type === 'string' &&
				(t.type.toLowerCase().startsWith('invalid') || t.type.toLowerCase().startsWith('exceeds'))
		);

		const tokens = received.filter(
			(t: Token) =>
				!(
					typeof t.type === 'string' &&
					(t.type.toLowerCase().startsWith('invalid') ||
						t.type.toLowerCase().startsWith('exceeds'))
				)
		);

		const lexerRows = groupWhitespaceTokens(tokens);

		if (invalidTokens.length) {
			const combinedErrors = formatLexicalErrors(invalidTokens, errorIcon);
			context.onAddErrorMarkers(invalidTokens);
			analysisStatus = 'error';
			terminalOutput = combinedErrors.map((e) => e.text).join('; ');

			if (!skipLogging) {
				// Set terminal messages in the calling component
				return {
					status: analysisStatus,
					output: terminalOutput,
					tokens,
					lexerRows
				};
			}
		} else {
			context.onClearErrorMarkers();
			const okMessage = tokens.length
				? `Lexical OK • ${tokens.length} token(s)`
				: 'No tokens produced';

			if (!skipLogging) {
				context.onSetTerminalOk(okMessage);
			}

			analysisStatus = 'success';
			terminalOutput = okMessage;
		}

		return {
			status: analysisStatus,
			output: terminalOutput,
			tokens,
			lexerRows
		};
	} catch (err) {
		const msg = err instanceof Error ? err.message : 'Unknown error';
		const errorMessage = `Lexical analysis failed: ${msg}`;
		if (!skipLogging) context.onSetTerminalError(errorMessage);
		return { status: 'error', output: errorMessage };
	}
}

/**
 * Perform syntax analysis
 */
export async function analyzeSyntax(
	context: AnalyzerContext,
	lexicalAnalyzer: typeof analyzeLexical
): Promise<void> {
	const { pyodide, pyodideReady, codeInput, errorIcon } = context;
	let analysisStatus: 'success' | 'error' = 'error';
	let terminalOutput = '';

	// Run lexical analysis first
	const lexicalResult = await lexicalAnalyzer(context, true);

	if (lexicalResult.status === 'success') {
		context.onClearTerminal();

		if (!pyodideReady) {
			const errorMsg = 'Python runtime not ready';
			context.onSetTerminalError(errorMsg);
			return;
		}

		try {
			pyodide.globals.set('code_input', codeInput);
			const result = await pyodide.runPythonAsync(SYNTAX_PYTHON_SCRIPT);
			const data = result.toJs({ dict_converter: Object.fromEntries });

			if (data.success) {
				context.onClearErrorMarkers();
				const syntaxMessage = data.message || 'Syntax analysis completed successfully';
				context.onSetTerminalOk(syntaxMessage);
			} else {
				if (data.error && data.error.line && data.error.col) {
					const errorToken: Token = {
						type: 'Syntax Error',
						value: 'error',
						line: data.error.line,
						col: data.error.col
					};
					context.onAddErrorMarkers([errorToken]);
				}
				const syntaxError = data.message || 'Syntax analysis failed';
				context.onSetTerminalError(syntaxError);
			}
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Unknown error';
			const syntaxError = `Syntax analysis failed: ${msg}`;
			context.onSetTerminalError(syntaxError);
		}
	} else {
		// Lexical errors found
		// Handle in the calling component
	}
}

/**
 * Perform semantic analysis with optional IR execution
 */
export async function analyzeSemantic(
	context: AnalyzerContext,
	lexicalAnalyzer: typeof analyzeLexical,
	runTacInterpreter = false,
	isResumingExecution = false
): Promise<{
	success: boolean;
	tacExecutionPaused: boolean;
}> {
	const { pyodide, pyodideReady, codeInput, errorIcon, checkIcon, accumulatedInputs = [] } =
		context;

	console.log('[analyzeSemantic] START', { runTacInterpreter, isResumingExecution, accumulatedInputs });

	// Run lexical analysis first
	const lexicalResult = await lexicalAnalyzer(context, true);
	console.log('[analyzeSemantic] Lexical result:', lexicalResult.status);

	if (lexicalResult.status === 'success') {
		if (!isResumingExecution) {
			context.onClearTerminal();
		}

		if (!pyodideReady) {
			const errorMsg = 'Python runtime not ready';
			context.onSetTerminalError(errorMsg);
			console.error('[analyzeSemantic] Pyodide not ready');
			return { success: false, tacExecutionPaused: false };
		}

		console.log('[analyzeSemantic] Running Python script...');
		try {
			pyodide.globals.set('code_input', codeInput);
			pyodide.globals.set('run_ir_pipeline', runTacInterpreter);
			pyodide.globals.set('is_resuming_execution', isResumingExecution);
			pyodide.globals.set('accumulated_inputs_json', JSON.stringify(accumulatedInputs));

			const result = await pyodide.runPythonAsync(
				SEMANTIC_PYTHON_SCRIPT.replace(/\t/g, '    ')
			);
			const data = result.toJs({ dict_converter: Object.fromEntries });

			console.log('[analyzeSemantic] Python result:', {
				success: data.success,
				execution_success: data.execution_success,
				execution_paused: data.execution_paused,
				has_output: !!data.execution_output,
				execution_error: data.execution_error
			});

			// Check if there's a general error message
			if (!data.success && data.message &&!data.execution_paused) {
				console.error('[analyzeSemantic] Error from Python:', data.message);
			}

			// Log AST to console
			if (data.ast) {
				try {
					const astObj = JSON.parse(data.ast);
					console.log(
						'\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🌳 AST\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
						'color: #00ff00; font-weight: bold'
					);
					console.log(astObj);
				} catch (e) {
					console.warn('Failed to parse AST JSON:', e);
				}
			}

			// Log Symbol Table
			if (data.symbol_table) {
				try {
					const symbolTableData = JSON.parse(data.symbol_table);
					console.table(symbolTableData);
				} catch (e) {
					console.warn('Failed to parse Symbol Table JSON:', e);
				}
			}

			// Log IR outputs if available
			if (data.ir_tac) {
				console.log('\n%c⚙️  TAC\n', 'color: #ff9800; font-weight: bold');
				console.log(data.ir_tac);
			}

			if (data.ir_tac_optimized) {
				console.log('\n%c✨ Optimized TAC\n', 'color: #80cbc4; font-weight: bold');
				console.log(data.ir_tac_optimized);
			}

			// Handle paused execution first (even though success=false when paused)
			if (runTacInterpreter && data.execution_paused) {
				console.log('[analyzeSemantic] Execution paused - showing input prompt');
				context.onClearErrorMarkers();
				// Execution is paused waiting for input
				// Show output accumulated so far + prompt
				const termMsgs: TermMsg[] = [];
				if (data.execution_output) {
					const output = data.execution_output;
					// Check if output ends with a prompt-like pattern (no newline at end)
					if (output && !output.endsWith('\n')) {
						// Split by newlines but keep the last part for the prompt
						const lines = output.split('\n');
						// Add all complete lines (except the last)
						for (let i = 0; i < lines.length - 1; i++) {
							if (lines[i].trim()) {
								termMsgs.push({
									text: lines[i],
									isInput: false
								});
							}
						}
						// Last line is the prompt - will have input field attached
						if (lines[lines.length - 1]) {
							termMsgs.push({
								text: lines[lines.length - 1],
								isInput: false,
								isPrompt: true
							});
						} else {
							// Empty last line, add empty prompt
							termMsgs.push({
								text: '',
								isPrompt: true
							});
						}
					} else {
						// Output ends with newline or is empty - show all lines + empty prompt
						const outputLines = output.split('\n').filter((line: string) => line.trim());
						termMsgs.push(...outputLines.map((line: string) => ({
							text: line,
							isInput: false
						})));
						// Add empty prompt on new line
						termMsgs.push({
							text: '',
							isPrompt: true
						});
					}
				} else {
					// No output yet - just show empty prompt
					termMsgs.push({
						text: '',
						isPrompt: true
					});
				}
                    // Ensure the prompt is always the last message before input
                    if (!termMsgs.length || !termMsgs[termMsgs.length - 1].isPrompt) {
                        termMsgs.push({
                            text: '',
                            isPrompt: true
                        });
                    }
				// Use append when resuming, set when first run
				if (isResumingExecution && context.onAppendTerminalMessages) {
					console.log('[analyzeSemantic] Appending messages (resuming)');
					context.onAppendTerminalMessages(termMsgs);
				} else if (context.onSetTerminalMessages) {
					console.log('[analyzeSemantic] Setting messages (first run)');
					context.onSetTerminalMessages(termMsgs);
				}
				
				return {
					success: true,
					tacExecutionPaused: true
				};
			}

			if (data.success) {
				console.log('[analyzeSemantic] Execution successful');
				context.onClearErrorMarkers();
				
				// Display execution output when IR interpreter ran
				if (runTacInterpreter && data.execution_output) {
					// Execution completed with output
					const outputLines = data.execution_output.split('\n').filter((line: string) => line.trim());
					const termMsgs: TermMsg[] = outputLines.map((line: string) => ({
						text: line,
						isInput: false
					}));
					// Use append when resuming, set when first run  
					if (isResumingExecution && context.onAppendTerminalMessages) {
						context.onAppendTerminalMessages(termMsgs);
					} else if (context.onSetTerminalMessages) {
						context.onSetTerminalMessages(termMsgs);
					}
				} else if (runTacInterpreter && data.execution_success && !data.execution_output) {
					// No output but execution was successful
					// Don't overwrite terminal when resuming - just means no new output
					if (!isResumingExecution) {
						context.onSetTerminalOk('No Semantic Error • Program executed successfully (no output)');
					}
				} else if (!runTacInterpreter) {
					// Semantic analysis only (no interpreter)
					const message = data.message || 'No Semantic Error';
					context.onSetTerminalOk(message);
				}
				
				return {
					success: true,
					tacExecutionPaused: Boolean(runTacInterpreter && data.execution_paused)
				};
			} else {
				// Error case - parse and display errors
				const parsedMarkers = data.error_markers ? JSON.parse(data.error_markers) : [];

				if (parsedMarkers.length > 0) {
					context.onClearErrorMarkers();
					const semanticTokens = parsedMarkers.map((marker: any) => ({
						type: 'semantic_error',
						value: marker.value,
						line: marker.line,
						col: marker.col,
						message: marker.message,
						severity: marker.severity
					}));
					context.onAddErrorMarkers(semanticTokens);
				}

				return { success: false, tacExecutionPaused: false };
			}
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Unknown error';
			const semanticError = `Semantic analysis failed: ${msg}`;
			console.error('[analyzeSemantic] Error:', err);
			context.onSetTerminalError(semanticError);
			return { success: false, tacExecutionPaused: false };
		}
	} else {
		// Lexical errors found
		console.log('[analyzeSemantic] Lexical errors found');
		return { success: false, tacExecutionPaused: false };
	}
}
