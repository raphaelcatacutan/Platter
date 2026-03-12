/**
 * Type definitions for the TAC compiler interface
 */

export type Token = {
	type: string;
	value: string;
	line: number;
	col: number;
	message?: string;
	severity?: string;
};

export type TermMsg = {
	icon?: string;
	text: string;
	isInput?: boolean;
	isPrompt?: boolean;
};

export type LexerRow = {
	lexeme: string;
	token: string;
};

export type AnalysisResult = {
	status: 'success' | 'error' | 'not-implemented';
	output: string;
};

export type LogData = {
	user_id?: string;
	source_code: string;
	terminal_output: string;
	status: string;
	language: string;
	duration_ms: number;
};

export type Theme = 'dark' | 'light';

export type TabType = 'lexical' | 'syntax' | 'semantic';
