/**
 * Page Controller
 * Manages all state and business logic for the TAC page
 */

import type {
	Theme,
	TabType,
	TermMsg,
	Token,
	LexerRow
} from './types';
import type { AnalyzerContext } from './analyzer';
import type { LifecycleContext } from './lifecycle';
import { writable, type Writable } from 'svelte/store';
import { DEFAULT_CODE_SAMPLE } from './constants';
import { logger, generateSessionId } from './logger';
import { pyodideManager } from './pyodide';
import { ErrorMarkerManager, normalizeCurlyQuotes as normalizeCurlyQuotesUtil, createTerminalHelpers } from './terminal';
import { FileOperations } from './fileOperations';
import {
	analyzeLexical as lexicalAnalyzer,
	analyzeSyntax as syntaxAnalyzer,
	analyzeSemantic as semanticAnalyzer
} from './analyzer';
import { setupComponent } from './lifecycle';

export class TACPageController {
	// Stores
	public sessionId = generateSessionId();
	public appVersion: Writable<string> = writable('1.0.0');
	public theme: Writable<Theme> = writable('dark');
	public activeTab: Writable<TabType> = writable('lexical');
	public codeInput: Writable<string> = writable(DEFAULT_CODE_SAMPLE);
	public lexerRows: Writable<LexerRow[]> = writable([]);
	public tokens: Writable<Token[]> = writable([]);
	public termMessages: Writable<TermMsg[]> = writable([]);
	public tacExecutionPaused: Writable<boolean> = writable(false);
	public currentInputLine: Writable<string> = writable('');
	public errorCount: Writable<number> = writable(0);

	// DOM references
	public textareaEl: HTMLTextAreaElement | null = null;
	public cmInstance: any = null;
	public editorPanelEl: HTMLElement | null = null;
	public terminalPanelEl: HTMLElement | null = null;
	public terminalInputEl: HTMLInputElement | null = null;
	public fileInputEl!: HTMLInputElement;

	// Internal state
	private isResumingExecution = false;
	private accumulatedInputs: string[] = [];
	private cleanupFn: (() => void) | null = null;
	private currentCodeInput = DEFAULT_CODE_SAMPLE;
	private currentTermMessages: TermMsg[] = [];
	private currentTheme: Theme = 'dark';

	// Managers
	public errorMarkerManager: ErrorMarkerManager;
	private terminalHelpers: ReturnType<typeof createTerminalHelpers>;
	public fileOps: FileOperations;

	// Icons (injected)
	private icons!: {
		check: string;
		errorIcon: string;
	};

	constructor() {
		this.errorMarkerManager = new ErrorMarkerManager();
		this.terminalHelpers = createTerminalHelpers('', ''); // Will be updated with real icons
		this.fileOps = new FileOperations(
			(msg) => this.setTerminalOk(msg),
			(msg) => this.setTerminalError(msg)
		);

		// Subscribe to stores to keep internal state synced
		this.codeInput.subscribe((value) => {
			this.currentCodeInput = value;
		});

		this.termMessages.subscribe((value) => {
			this.currentTermMessages = value;
			// Calculate error count
			const count = value.filter(
				(m) =>
					!(
						typeof m.text === 'string' &&
						(m.text.startsWith('Lexical OK') ||
							m.text.startsWith('No Syntax Error') ||
							m.text.startsWith('Warning:'))
					)
			).length;
			this.errorCount.set(count);
		});

		this.theme.subscribe((value) => {
			this.currentTheme = value;
		});
	}

	public setIcons(icons: { check: string; errorIcon: string }) {
		this.icons = icons;
		this.terminalHelpers = createTerminalHelpers(icons.check, icons.errorIcon);
	}

	// Terminal message helpers
	public setTerminalOk(message = 'No Error') {
		this.termMessages.set(this.terminalHelpers.createOkMessage(message));
	}

	public setTerminalError(message: string) {
		this.termMessages.set(this.terminalHelpers.createErrorMessage(message));
	}

	public clearTerminal() {
		this.termMessages.set([]);
	}

	// Normalize curly quotes
	public normalizeCurlyQuotes() {
		if (this.cmInstance) {
			normalizeCurlyQuotesUtil(this.cmInstance);
			this.codeInput.set(this.cmInstance.getValue());
		}
	}

	// File operations
	public openFileDialog() {
		this.normalizeCurlyQuotes();
		this.fileOps.openFileDialog();
	}

	public async handleFileInput() {
		await this.fileOps.handleFileInput((code) => {
			this.codeInput.set(code);
		});
	}

	public async saveFileDialog() {
		this.normalizeCurlyQuotes();
		await this.fileOps.saveFile(this.currentCodeInput);
	}

	// Theme toggle
	public toggleTheme() {
		this.normalizeCurlyQuotes();
		this.theme.update((t) => (t === 'dark' ? 'light' : 'dark'));
	}

	// Clear error markers
	public clearErrorMarkers() {
		this.errorMarkerManager.clear();
	}

	// Copy to clipboard
	public async handleCopyToClipboard() {
		this.normalizeCurlyQuotes();
		try {
			if (this.cmInstance) {
				const selectedText = this.cmInstance.getSelection();
				const textToCopy = selectedText || this.currentCodeInput;
				await navigator.clipboard.writeText(textToCopy);
				this.setTerminalOk('Code copied to clipboard!');
			} else if (this.currentCodeInput) {
				await navigator.clipboard.writeText(this.currentCodeInput);
				this.setTerminalOk('Code copied to clipboard!');
			} else {
				this.setTerminalError('No code to copy');
			}
		} catch (err) {
			this.setTerminalError('Failed to copy to clipboard');
		}
	}

	// Clear all
	public clearAll() {
		this.normalizeCurlyQuotes();
		if (this.cmInstance) this.cmInstance.setValue('');
		this.codeInput.set('');
		this.clearTerminal();
		this.clearErrorMarkers();
		this.lexerRows.set([]);
		this.tokens.set([]);
	}

	// Terminal input handling
	public handleTerminalInputKeydown(event: KeyboardEvent) {
		if (!(event.key === 'Enter' && !event.shiftKey)) return;
		let paused = false;
		this.tacExecutionPaused.subscribe((v) => (paused = v))();
		if (!paused) return;
		event.preventDefault();
		this.resumeExecution();
	}

	public resumeExecution() {
		console.log('[PageController.resumeExecution] Called');
		let paused = false;
		this.tacExecutionPaused.subscribe((v) => (paused = v))();
		console.log('[PageController.resumeExecution] Paused state:', paused);
		if (!paused) return;

		let inputLine = '';
		this.currentInputLine.subscribe((v) => (inputLine = v))();
		console.log('[PageController.resumeExecution] Input line:', inputLine);

		// Always add input to accumulated inputs (even if empty)
		this.accumulatedInputs = [...this.accumulatedInputs, inputLine];
		console.log('[PageController.resumeExecution] Accumulated inputs:', this.accumulatedInputs);
		
		// Add the user's input to the terminal display
		this.termMessages.update((msgs) => {
			const newMsgs = [...msgs];
			// Merge the prompt and input into a single line (like a real terminal)
			if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].isPrompt) {
				const lastMsg = newMsgs[newMsgs.length - 1];
				// Combine prompt text with user input on the same line
				newMsgs[newMsgs.length - 1] = {
					text: (lastMsg.text || '') + inputLine,
					isInput: false
				};
			} else {
				// No prompt found - just add the input as a new line
				newMsgs.push({
					text: inputLine,
					isInput: true
				});
			}
			return newMsgs;
		});
		
		this.currentInputLine.set('');

		this.tacExecutionPaused.set(false);
		this.isResumingExecution = true;
		this.analyzeSemantic(true);
	}

	// Create analyzer context
	private createAnalyzerContext(): AnalyzerContext {
		return {
			pyodide: pyodideManager.instance,
			pyodideReady: pyodideManager.isReady,
			codeInput: this.currentCodeInput,
			errorIcon: this.icons.errorIcon,
			checkIcon: this.icons.check,
			accumulatedInputs: this.accumulatedInputs,
			onAddErrorMarkers: (errors: Token[]) => this.errorMarkerManager.add(errors),
			onClearErrorMarkers: () => this.errorMarkerManager.clear(),
			onSetTerminalOk: (msg: string) => this.setTerminalOk(msg),
			onSetTerminalError: (msg: string) => this.setTerminalError(msg),
			onClearTerminal: () => this.clearTerminal(),
			onSetTerminalMessages: (messages: TermMsg[]) => this.termMessages.set(messages),
			onAppendTerminalMessages: (messages: TermMsg[]) => this.termMessages.update(msgs => [...msgs, ...messages])
		};
	}

	// Analysis functions
	public async handleAnalyzeLexical() {
		this.normalizeCurlyQuotes();
		this.activeTab.set('lexical');
		const startTime = performance.now();

		const context = this.createAnalyzerContext();
		const result = await lexicalAnalyzer(context, false);

		if (result.tokens) this.tokens.set(result.tokens);
		if (result.lexerRows) this.lexerRows.set(result.lexerRows);

		if (result.status === 'error' && result.output) {
			const errorLines = result.output.split('; ');
			this.termMessages.set(errorLines.map((text) => ({ icon: this.icons.errorIcon, text })));
		}

		const duration = performance.now() - startTime;
		let appVer = '1.0.0';
		this.appVersion.subscribe((v) => (appVer = v))();

		logger.addToLogBatch({
			user_id: this.sessionId,
			source_code: this.currentCodeInput,
			terminal_output: result.output,
			status: result.status,
			language: `lexical-v${appVer}`,
			duration_ms: Math.round(duration)
		});
	}

	public async handleAnalyzeSyntax() {
		this.normalizeCurlyQuotes();
		this.activeTab.set('syntax');
		const startTime = performance.now();

		const context = this.createAnalyzerContext();
		await syntaxAnalyzer(context, lexicalAnalyzer);

		const duration = performance.now() - startTime;
		const terminalOutput = this.currentTermMessages.map((m) => m.text).join('; ');
		const analysisStatus = this.currentTermMessages.some((m) => m.icon === this.icons.errorIcon)
			? 'error'
			: 'success';

		let appVer = '1.0.0';
		this.appVersion.subscribe((v) => (appVer = v))();

		logger.addToLogBatch({
			user_id: this.sessionId,
			source_code: this.currentCodeInput,
			terminal_output: terminalOutput,
			status: analysisStatus,
			language: `syntax-v${appVer}`,
			duration_ms: Math.round(duration)
		});
	}

	public async analyzeSemantic(runTacInterpreter = false) {
		console.log('[PageController.analyzeSemantic] START', { runTacInterpreter, isResumingExecution: this.isResumingExecution });
		this.normalizeCurlyQuotes();
		const startTime = performance.now();

		if (!this.isResumingExecution) {
			this.tacExecutionPaused.set(false);
			// Clear accumulated inputs when starting fresh (not resuming)
			this.accumulatedInputs = [];
		}

		const context = this.createAnalyzerContext();
		console.log('[PageController.analyzeSemantic] Context created, accumulated inputs:', this.accumulatedInputs);

		const result = await semanticAnalyzer(
			context,
			lexicalAnalyzer,
			runTacInterpreter,
			this.isResumingExecution
		);

		this.tacExecutionPaused.set(result.tacExecutionPaused);
		this.isResumingExecution = false;
		this.activeTab.set('semantic');

		const duration = performance.now() - startTime;
		const terminalOutput = this.currentTermMessages.map((m) => m.text).join('; ');
		const analysisStatus = result.success ? 'success' : 'error';

		let appVer = '1.0.0';
		this.appVersion.subscribe((v) => (appVer = v))();

		logger.addToLogBatch({
			user_id: this.sessionId,
			source_code: this.currentCodeInput,
			terminal_output: terminalOutput,
			status: analysisStatus,
			language: `${runTacInterpreter ? 'semantic-ir' : 'semantic'}-v${appVer}`,
			duration_ms: Math.round(duration)
		});
	}

	// Lifecycle: Component mount
	public async initialize(basePath: string) {
		if (!this.textareaEl) return;

		const context: LifecycleContext = {
			textareaEl: this.textareaEl,
			codeInput: this.currentCodeInput,
			basePath,
			editorPanelEl: this.editorPanelEl,
			terminalPanelEl: this.terminalPanelEl,
			pyodideManager,
			errorMarkerManager: this.errorMarkerManager,
			fileOps: this.fileOps,
			fileInputEl: this.fileInputEl,
			onCodeChange: (value: string) => {
				this.codeInput.set(value);
			},
			onVersionFetched: (version: string) => {
				this.appVersion.set(version);
			},
			onInitError: (msg: string) => this.setTerminalError(msg),
			analyzeSemantic: (runTac: boolean) => this.analyzeSemantic(runTac),
			analyzeLexical: () => this.handleAnalyzeLexical(),
			analyzeSyntax: () => this.handleAnalyzeSyntax()
		};

		const result = await setupComponent(context);
		this.cmInstance = result.cmInstance;
		this.cleanupFn = result.cleanup;

		// Set cmInstance for managers after initialization
		this.errorMarkerManager.setCmInstance(this.cmInstance);
		this.fileOps.setCmInstance(this.cmInstance);
		this.fileOps.setFileInputElement(this.fileInputEl);
	}

	// Lifecycle: Component cleanup
	public cleanup() {
		if (this.cleanupFn) {
			this.cleanupFn();
		}
	}
}
