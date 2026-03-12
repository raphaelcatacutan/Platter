/**
 * CodeMirror Editor Setup and Configuration
 * Includes Platter language syntax highlighting mode
 */

import { loadScript, loadCSS } from '$lib/utils/browser';

/**
 * Define the Platter syntax highlighting mode for CodeMirror
 */
export function definePlatterMode(CodeMirror: any) {
	CodeMirror.defineMode('platter', function () {
		const keywords: Record<string, boolean> = {
			// Conditionals
			alt: true,
			check: true,
			instead: true,
			// Logical operators
			and: true,
			or: true,
			not: true,
			// Loops
			order: true,
			repeat: true,
			pass: true,
			menu: true,
			choice: true,
			stop: true,
			next: true,
			usual: true,
			// Function definition
			prepare: true,
			start: true,
			// Return
			serve: true,
			of: true,
			// Struct
			table: true
		};

		const builtinMethods: Record<string, boolean> = {
			append: true,
			bill: true,
			copy: true,
			cut: true,
			fact: true,
			matches: true,
			size: true,
			sort: true,
			sqrt: true,
			tochars: true,
			topiece: true,
			take: true,
			tosip: true,
			rand: true,
			pow: true,
			remove: true,
			reverse: true,
			search: true
		};

		const dataTypes: Record<string, boolean> = {
			chars: true,
			flag: true,
			piece: true,
			sip: true
		};

		const booleanLiterals: Record<string, boolean> = {
			down: true,
			up: true
		};

		const operators = /^(?:\+|-|\*|\/|%|>|<|=|==|>=|<=|!=|\+=|-=|\*=|\/=|%=)/;
		const delimiters = /^(?:,|\{|\}|\(|\)|\[|\]|;|:)/;

		return {
			token: function (stream: any, state: any) {
				// Whitespace
				if (stream.eatSpace()) return null;

				// Comments
				// Single line comment: # followed by space
				if (stream.match(/^#\s.*/)) return 'comment';

				// Multi-line comment start: ##
				if (stream.match(/^##/)) {
					if (state.inComment) {
						// End multi-line comment
						state.inComment = false;
					} else {
						// Start multi-line comment
						state.inComment = true;
					}
					return 'comment';
				}

				// Inside multi-line comment
				if (state.inComment) {
					// Check if ## appears on this line to end comment
					if (stream.match(/^.*?(?=##)/)) {
						// Found ##, will be handled on next token call
						return 'comment';
					} else {
						// No ## found, consume rest of line
						stream.skipToEnd();
						return 'comment';
					}
				}

				// String literals
				if (stream.match(/^"(?:[^"\\]|\\.)*"/)) return 'string';
				if (stream.match(/^'(?:[^'\\]|\\.)*'/)) return 'string';

				// Escape sequences in strings
				if (stream.match(/\\[nt'"\\]/)) return 'string-2';

				// Numbers
				if (stream.match(/^-?\d+\.?\d*/)) return 'number';

				// Operators
				if (stream.match(operators)) return 'operator';

				// Delimiters
				if (stream.match(delimiters)) return 'punctuation';

				// Keywords, types, methods, etc.
				if (stream.match(/^[a-zA-Z_]\w*/)) {
					const word: string = stream.current();
					if (keywords[word]) return 'keyword';
					if (dataTypes[word]) return 'type';
					if (booleanLiterals[word]) return 'atom';
					if (builtinMethods[word]) return 'builtin';
					return 'variable';
				}

				stream.next();
				return null;
			},
			startState: function () {
				return { inComment: false };
			}
		};
	});
}

/**
 * Initialize CodeMirror with Platter syntax highlighting
 */
export async function initializeCodeMirror(
	textareaEl: HTMLTextAreaElement,
	initialValue: string,
	onAnalyzeSemantic: (withInterpreter: boolean) => void,
	onAnalyzeLexical: () => void,
	onAnalyzeSyntax: () => void,
	onChange: (value: string) => void
): Promise<any> {
	try {
		// Load CodeMirror assets from CDN
		await loadCSS(
			'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css'
		);
		await loadScript(
			'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js'
		);

		if (!(window as any).CodeMirror) {
			throw new Error('CodeMirror failed to load');
		}

		const CM = (window as any).CodeMirror;

		// Define Platter syntax highlighting mode
		definePlatterMode(CM);

		// Create CodeMirror instance
		const cmInstance = CM.fromTextArea(textareaEl, {
			lineNumbers: true,
			lineWrapping: true,
			viewportMargin: Infinity,
			mode: 'platter',
			extraKeys: {
				'Ctrl-Enter': function () {
					onAnalyzeSemantic(true);
				},
				'Ctrl-1': function () {
					onAnalyzeLexical();
				},
				'Ctrl-2': function () {
					onAnalyzeSyntax();
				},
				'Ctrl-3': function () {
					onAnalyzeSemantic(false);
				}
			}
		});

		cmInstance.setSize('100%', '100%');
		cmInstance.on('change', () => {
			onChange(cmInstance.getValue());
		});

		return cmInstance;
	} catch (err) {
		console.warn('Failed to load CodeMirror from CDN:', err);
		return null;
	}
}
