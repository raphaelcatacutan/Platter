/**
 * Constants for the TAC compiler interface
 */

export const WEBHOOK_URL =
	'https://script.google.com/macros/s/AKfycbwkXRRIlnkZI2z5bXT08Lswe504TalqtJcA13CtbMZcgoH3EhYfWtJBlD4ql_hg9q4eWg/exec';
export const BATCH_DELAY = 10000; // 10 seconds
export const CTRL_ENTER_HINT_SEEN_KEY = 'platter_ctrl_enter_hint_seen_v1';

export const DEFAULT_CODE_SAMPLE = `start() {
	chars of name, age;
    
    bill("What's your name? ");
    name = take();
    
    bill("What's your age? ");
    age = take();
    
    age = take();
    
    bill("Hello ");
    bill(name);
    bill(", you are ");
    bill(age);
    bill(" years old!");
}`;
