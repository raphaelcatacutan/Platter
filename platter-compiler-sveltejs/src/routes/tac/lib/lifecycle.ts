/**
 * Lifecycle Management
 * Handles component mount/unmount logic
 */

import type { PyodideManager } from './pyodide';
import type { FileOperations } from './fileOperations';
import type { ErrorMarkerManager } from './terminal';
import { fetchVersion, showFirstVisitCtrlEnterHint, syncTerminalPanelHeight } from './utils';
import { initializeCodeMirror } from './codemirror';
import { logger } from './logger';

export interface LifecycleContext {
	textareaEl: HTMLTextAreaElement;
	codeInput: string;
	basePath: string;
	editorPanelEl: HTMLElement | null;
	terminalPanelEl: HTMLElement | null;
	pyodideManager: PyodideManager;
	errorMarkerManager: ErrorMarkerManager;
	fileOps: FileOperations;
	fileInputEl: HTMLInputElement;
	onCodeChange: (value: string) => void;
	onVersionFetched: (version: string) => void;
	onInitError: (error: string) => void;
	analyzeSemantic: (runTac: boolean) => void;
	analyzeLexical: () => void;
	analyzeSyntax: () => void;
}

export async function setupComponent(context: LifecycleContext) {
	const {
		textareaEl,
		codeInput,
		basePath,
		editorPanelEl,
		terminalPanelEl,
		pyodideManager,
		errorMarkerManager,
		fileOps,
		fileInputEl,
		onCodeChange,
		onVersionFetched,
		onInitError,
		analyzeSemantic,
		analyzeLexical,
		analyzeSyntax
	} = context;

	// Show first-visit hint
	showFirstVisitCtrlEnterHint();

	// Set up keyboard shortcuts
	const handleGlobalCtrlEnter = (event: KeyboardEvent) => {
		if (event.defaultPrevented || event.repeat) return;
		if (event.ctrlKey && event.key === 'Enter') {
			event.preventDefault();
			analyzeSemantic(true);
		} else if (event.ctrlKey && event.key === '1') {
			event.preventDefault();
			analyzeLexical();
		} else if (event.ctrlKey && event.key === '2') {
			event.preventDefault();
			analyzeSyntax();
		} else if (event.ctrlKey && event.key === '3') {
			event.preventDefault();
			analyzeSemantic(false);
		}
	};
	window.addEventListener('keydown', handleGlobalCtrlEnter);
	window.addEventListener('resize', () => syncTerminalPanelHeight(editorPanelEl, terminalPanelEl));

	// Initialize CodeMirror
	const cmInstance = await initializeCodeMirror(
		textareaEl,
		codeInput,
		analyzeSemantic,
		analyzeLexical,
		analyzeSyntax,
		onCodeChange
	);

	// Set cmInstance for managers
	errorMarkerManager.setCmInstance(cmInstance);
	fileOps.setCmInstance(cmInstance);
	fileOps.setFileInputElement(fileInputEl);

	// Fetch app version
	const appVersion = await fetchVersion(basePath);
	onVersionFetched(appVersion);

	// Initialize Pyodide
	await pyodideManager.initialize(basePath, onInitError);

	// Set up panel height sync
	let panelSyncObserver: ResizeObserver | null = null;
	requestAnimationFrame(() => {
		syncTerminalPanelHeight(editorPanelEl, terminalPanelEl);
		if (typeof ResizeObserver !== 'undefined') {
			panelSyncObserver = new ResizeObserver(() =>
				syncTerminalPanelHeight(editorPanelEl, terminalPanelEl)
			);
			if (editorPanelEl) panelSyncObserver.observe(editorPanelEl);
			if (terminalPanelEl?.parentElement)
				panelSyncObserver.observe(terminalPanelEl.parentElement);
		}
	});

	// Return cleanup function
	return {
		cmInstance,
		handleGlobalCtrlEnter,
		panelSyncObserver,
		cleanup: () => {
			// Cleanup event listeners
			window.removeEventListener('resize', () =>
				syncTerminalPanelHeight(editorPanelEl, terminalPanelEl)
			);
			if (panelSyncObserver) {
				panelSyncObserver.disconnect();
			}

			if (handleGlobalCtrlEnter) {
				window.removeEventListener('keydown', handleGlobalCtrlEnter);
			}

			// Cleanup CodeMirror
			if (cmInstance && typeof cmInstance.toTextArea === 'function') {
				cmInstance.toTextArea();
			}

			// Cleanup logger
			logger.cleanup();
		}
	};
}
