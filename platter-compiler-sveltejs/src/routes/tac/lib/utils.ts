/**
 * General Utilities
 * Version fetching, theme management, clipboard operations, etc.
 */

import { copyToClipboard } from '$lib/utils/browser';
import { CTRL_ENTER_HINT_SEEN_KEY } from './constants';

/**
 * Fetch application version from version.json
 */
export async function fetchVersion(basePath: string): Promise<string> {
	try {
		const response = await fetch(`${basePath}/version.json`);
		const versionData = await response.json();
		return `${versionData.major}.${versionData.minor}.${versionData.patch}`;
	} catch (err) {
		console.warn('Failed to fetch version:', err);
		return '1.0.0';
	}
}

/**
 * Show first-visit hint for Ctrl+Enter shortcut
 */
export function showFirstVisitCtrlEnterHint() {
	if (typeof window === 'undefined') return;

	try {
		if (window.localStorage.getItem(CTRL_ENTER_HINT_SEEN_KEY) === '1') return;
		window.alert('Ctrl+Enter to run TAC and interpreter');
		window.localStorage.setItem(CTRL_ENTER_HINT_SEEN_KEY, '1');
	} catch {
		// Ignore storage restrictions (private mode, blocked storage, etc.)
	}
}

/**
 * Sync terminal panel height with editor panel
 */
export function syncTerminalPanelHeight(
	editorPanelEl: HTMLElement | null,
	terminalPanelEl: HTMLElement | null
) {
	if (!editorPanelEl || !terminalPanelEl) return;

	const editorRect = editorPanelEl.getBoundingClientRect();
	const terminalRect = terminalPanelEl.getBoundingClientRect();
	const targetHeight = Math.round(editorRect.bottom - terminalRect.top);

	if (targetHeight > 0) {
		terminalPanelEl.style.height = `${targetHeight + 10}px`;
		terminalPanelEl.style.minHeight = `${targetHeight + 10}px`;
	}
}

/**
 * Copy content to clipboard
 */
export async function handleCopyToClipboard(
	cmInstance: any,
	codeInput: string,
	onSuccess: (msg: string) => void,
	onError: (msg: string) => void
) {
	const content =
		cmInstance && typeof cmInstance.getValue === 'function' ? cmInstance.getValue() : codeInput;

	try {
		await copyToClipboard(content);
		onSuccess('Content copied to clipboard');
	} catch (err) {
		onError('Failed to copy to clipboard');
	}
}
