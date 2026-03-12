/**
 * File Operations
 * Handles opening and saving .platter files
 */

import { readFileAsText, saveContent } from '$lib/utils/browser';
import type { TermMsg } from './types';

export class FileOperations {
	private fileInputEl: HTMLInputElement | null = null;
	private cmInstance: any = null;
	private onSuccess: (message: string) => void;
	private onError: (message: string) => void;

	constructor(
		onSuccess: (message: string) => void,
		onError: (message: string) => void
	) {
		this.onSuccess = onSuccess;
		this.onError = onError;
	}

	setFileInputElement(el: HTMLInputElement) {
		this.fileInputEl = el;
	}

	setCmInstance(instance: any) {
		this.cmInstance = instance;
	}

	/**
	 * Open file dialog for selecting .platter files
	 */
	openFileDialog() {
		this.fileInputEl?.click();
	}

	/**
	 * Handle file input change event
	 */
	async handleFileInput(onCodeUpdate: (code: string) => void) {
		const f = this.fileInputEl?.files?.[0];
		if (!f) return;

		if (!f.name || !f.name.toLowerCase().endsWith('.platter')) {
			this.onError('Please select a .platter file');
			if (this.fileInputEl) this.fileInputEl.value = '';
			return;
		}

		try {
			const text = await readFileAsText(f);
			onCodeUpdate(text);
			if (this.cmInstance && typeof this.cmInstance.setValue === 'function') {
				this.cmInstance.setValue(text);
			}
			this.onSuccess(`Opened ${f.name}`);
		} catch (err) {
			this.onError('Failed to read file');
		} finally {
			// Reset input so the same file can be selected again
			if (this.fileInputEl) this.fileInputEl.value = '';
		}
	}

	/**
	 * Save current editor content as a .platter file
	 */
	async saveFile(codeInput: string) {
		const content =
			this.cmInstance && typeof this.cmInstance.getValue === 'function'
				? this.cmInstance.getValue()
				: codeInput;

		try {
			const msg = await saveContent(content, 'program.platter');
			this.onSuccess(msg);
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Save cancelled or failed';
			this.onError(`Save failed: ${msg}`);
		}
	}
}
