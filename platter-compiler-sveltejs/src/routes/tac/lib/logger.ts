/**
 * Logger Service for Google Apps Script webhook
 * Handles batched logging of analysis results
 */

import type { LogData } from './types';
import { WEBHOOK_URL, BATCH_DELAY } from './constants';

class LoggerService {
	private logBatch: LogData[] = [];
	private logTimer: NodeJS.Timeout | null = null;

	addToLogBatch(logData: LogData) {
		this.logBatch.push(logData);

		// Clear existing timer
		if (this.logTimer) {
			clearTimeout(this.logTimer);
		}

		// Set new timer to send logs after delay of inactivity
		this.logTimer = setTimeout(() => {
			this.sendLogBatch();
		}, BATCH_DELAY);
	}

	async sendLogBatch() {
		if (this.logBatch.length === 0) return;

		const logsToSend = [...this.logBatch];
		this.logBatch = [];

		try {
			await fetch(WEBHOOK_URL, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(logsToSend),
				mode: 'no-cors' // Required for Google Apps Script
			});
			console.log('Logs sent successfully:', logsToSend.length);
		} catch (error) {
			console.error('Failed to send logs:', error);
		}
	}

	cleanup() {
		if (this.logTimer) {
			clearTimeout(this.logTimer);
		}
		if (this.logBatch.length > 0) {
			this.sendLogBatch();
		}
	}
}

/**
 * Generate unique session ID for tracking
 */
export function generateSessionId(): string {
	const timestamp = Date.now();
	const hash = (timestamp + Math.random() * 1000).toString(36).substring(2, 9);
	return `user_${hash}`;
}

export const logger = new LoggerService();
