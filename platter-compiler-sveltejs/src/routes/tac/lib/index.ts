/**
 * TAC Compiler Library Index
 * Re-exports all core modules for easy importing
 */

// Types
export * from './types';

// Constants
export * from './constants';

// Logger Service
export { logger, generateSessionId } from './logger';

// Pyodide Manager
export { pyodideManager, PyodideManager } from './pyodide';

// CodeMirror
export { initializeCodeMirror, definePlatterMode } from './codemirror';

// Terminal Management
export { ErrorMarkerManager, normalizeCurlyQuotes, createTerminalHelpers } from './terminal';

// File Operations
export { FileOperations } from './fileOperations';

// Analyzers
export { analyzeLexical, analyzeSyntax, analyzeSemantic } from './analyzer';
export type { AnalyzerContext } from './analyzer';

// Utilities
export {
	fetchVersion,
	showFirstVisitCtrlEnterHint,
	syncTerminalPanelHeight,
	handleCopyToClipboard
} from './utils';

// Lifecycle
export { setupComponent } from './lifecycle';
export type { LifecycleContext } from './lifecycle';

// Page Controller
export { TACPageController } from './pageController';
