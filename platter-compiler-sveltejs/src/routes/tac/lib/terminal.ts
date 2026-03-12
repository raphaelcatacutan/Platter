/**
 * Terminal Message and Error Marker Management
 * Handles terminal output, error highlighting, and CodeMirror markers
 */

import type { TermMsg, Token } from './types';

/**
 * Manages error markers in the CodeMirror editor
 */
export class ErrorMarkerManager {
	private errorMarkers: any[] = [];
	private cmInstance: any = null;

	setCmInstance(instance: any) {
		this.cmInstance = instance;
	}

	/**
	 * Clear all error markers from the editor
	 */
	clear() {
		if (!this.cmInstance) return;

		this.errorMarkers.forEach((marker) => marker.clear());
		this.errorMarkers = [];
	}

	/**
	 * Add error markers to the editor
	 */
	add(errors: Token[]) {
		if (!this.cmInstance) {
			console.warn('Cannot add error markers: CodeMirror instance not available');
			return;
		}

		console.log('addErrorMarkers called with', errors.length, 'errors');
		this.clear();

		errors.forEach((error, index) => {
			console.log(`Adding marker ${index + 1}:`, error);
			const line = error.line - 1; // CodeMirror uses 0-based line numbers
			const col = error.col - 1; // CodeMirror uses 0-based columns
			const valueLength = error.value?.length || 1;

			// Determine CSS class based on severity (case-insensitive)
			const severity = String(error.severity || '').toUpperCase();
			const cssClass = severity === 'WARNING' ? 'warning-underline' : 'error-underline';

			const marker = this.cmInstance.markText(
				{ line, ch: col },
				{ line, ch: col + valueLength },
				{
					className: cssClass,
					title: error.message || 'Error'
				}
			);
			this.errorMarkers.push(marker);
			console.log(`  [OK] Marker ${index + 1} added successfully with ${cssClass}`);
		});

		console.log(`Total ${this.errorMarkers.length} error markers active in editor`);
	}
}

/**
 * Normalize curly quotes to straight quotes in CodeMirror
 */
export function normalizeCurlyQuotes(cmInstance: any): void {
	if (!cmInstance) return;

	const content = cmInstance.getValue();

	// Replace curly quotes with straight quotes using Unicode
	const normalized = content
		.replace(/\u201C/g, '\u0022') // Left double curly quote → straight double quote
		.replace(/\u201D/g, '\u0022') // Right double curly quote → straight double quote
		.replace(/\u2018/g, '\u0027') // Left single curly quote → straight single quote
		.replace(/\u2019/g, '\u0027'); // Right single curly quote → straight single quote

	if (content !== normalized) {
		// Save cursor position
		const cursor = cmInstance.getCursor();

		// Update content
		cmInstance.setValue(normalized);

		// Restore cursor position
		cmInstance.setCursor(cursor);
	}
}

/**
 * Create terminal message helpers
 */
export function createTerminalHelpers(checkIcon: string, errorIcon: string) {
	return {
		createOkMessage: (message = 'No Error'): TermMsg[] => {
			return [{ icon: checkIcon, text: message }];
		},
		createErrorMessage: (message: string): TermMsg[] => {
			return [{ icon: errorIcon, text: message }];
		}
	};
}
