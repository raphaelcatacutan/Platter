<script lang="ts">
	// Icons and assets
	import {
		check,
		copy,
		copy1,
		darkmode,
		darkmode1,
		darkBg,
		lightBg,
		errorIcon,
		lightmode,
		logo,
		newFile,
		newFile1,
		openFile,
		openFile1,
		refresh,
		refresh1,
		saveFile,
		saveFile1,
		synSemLexIcon,
		synSemLexIcon1,
		table,
		warning
	} from '$lib';
	import { editor as editorSvg } from '$lib/assets';

	// Svelte lifecycle
	import { onMount, onDestroy } from 'svelte';

	// Page Controller
	import { TACPageController } from './lib';

	export let data;

	// Initialize controller
	const controller = new TACPageController();
	controller.setIcons({ check, errorIcon });

	// Reactive stores from controller (extract for Svelte reactivity)
	const { theme, activeTab, codeInput, lexerRows, tokens, termMessages, tacExecutionPaused, currentInputLine, errorCount } = controller;

	// Auto-focus the terminal input when execution pauses
	$: if ($tacExecutionPaused && controller.terminalInputEl) {
		setTimeout(() => controller.terminalInputEl?.focus(), 0);
	}

	// Lifecycle
	onMount(async () => {
		await controller.initialize(data.basePath);
	});

	onDestroy(() => {
		controller.cleanup();
	});
</script>

<div class="ide" data-theme={$theme} style={`--bg-img: url(${$theme === 'dark' ? darkBg : lightBg})`}>
	<!-- Top bar -->
	<header class="titlebar">
		<div class="brand">
			<img class="logo" src={logo} alt="Platter logo" />
			<a href="/cfg" target="_blank" class="name" title="View CFG Visualization">Platter IDE</a>
		</div>
		<div class="win-controls">
			<span class="dot" title="minimize"></span>
			<span class="dot" title="maximize"></span>
			<span class="dot" title="close"></span>
		</div>
	</header>

	<!-- Main grid: left workspace and right sidebar -->
	<div class="grid">
		<!-- LEFT WORKSPACE -->
		<section class="left">
			<!-- Toolbar row -->
			<div class="toolbar">
				<button class="pill active" on:click={() => controller.analyzeSemantic(true)}>
					{#if $theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Run Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Run Icon" />
					{/if}
					<span>Run Code</span>
				</button>

				<div class="spacer"></div>
				<!-- replace icons based on theme -->
				<button
					class="icon-btn"
					title="refresh"
					on:click={() => controller.clearAll()}
					>{#if $theme === 'dark'}
						<img class="icon" src={refresh} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={refresh1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="copy" on:click={() => controller.handleCopyToClipboard()}
					>{#if $theme === 'dark'}
						<img class="icon" src={copy} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={copy1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="Theme" on:click={() => controller.toggleTheme()}>
					{#if $theme === 'dark'}
						<img class="icon" src={lightmode} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={darkmode} alt="Light Theme Icon" />
					{/if}
				</button>
			</div>

			<!-- Editor canvas -->
			<div class="panel editor" style={`--editor-img: url(${editorSvg})`} bind:this={controller.editorPanelEl}>
				<img class="editor-frame" src={editorSvg} alt="" aria-hidden="true" />
				<textarea
					class="editor-area"
					bind:this={controller.textareaEl}
					bind:value={$codeInput}
					placeholder="Write your Platter code here..."
					spellcheck="false"
				></textarea>
			</div>

		</section>

		<!-- RIGHT SIDEBAR -->
		<aside class="right">
			<div class="actions">
				<button
					class="btn"
					on:click={() => {
					controller.normalizeCurlyQuotes();
						const newWindow = window.open(window.location.href, '_blank');
						if (newWindow) setTimeout(() => (newWindow.document.body.style.zoom = '80%'), 100);
					}}
				>
					{#if $theme === 'dark'}
						<img class="icon" src={newFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={newFile1} alt="Light Theme Icon" />
					{/if} <span>New Tab</span></button
				>
				<button class="btn" type="button" on:click={() => controller.openFileDialog()}>
					{#if $theme === 'dark'}
						<img class="icon" src={openFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={openFile1} alt="Light Theme Icon" />
					{/if}
					<span>Open File</span></button
				>
				<!-- hidden file input for opening .platter files -->
				<input
					type="file"
					accept=".platter"
					bind:this={controller.fileInputEl}
					on:change={() => controller.handleFileInput()}
					style="display:none"
				/>
				<button class="btn" type="button" on:click={() => controller.saveFileDialog()}>
					{#if $theme === 'dark'}
						<img class="icon" src={saveFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={saveFile1} alt="Light Theme Icon" />
					{/if} <span>Save File</span></button
				>
			</div>

			<div class="panel table" style={`--table-img: url(${table})`} bind:this={controller.terminalPanelEl}>
				<div class="table-title-row">
					<div class="table-title">Terminal</div>
					<div class="counter">
						<span>Errors: {$errorCount}</span>
						{#if $errorCount > 0}
							<img class="icon" src={warning} alt="warning" />
						{/if}
					</div>
				</div>
				<div class="table-body">
					{#if $termMessages.length === 0 && !$tacExecutionPaused}
						<div class="empty">No output yet. Press Ctrl+Enter to run.</div>
					{:else}
						<div class="terminal-content">
							{#each $termMessages as e, i}
								{#if e.icon}
									<div class="trow">
										<img class="ticon-img" src={e.icon} alt="" />
										<span class="tmsg" class:user-input={e.isInput}>{e.text}</span>
									</div>
								{:else}
									<!-- Output without icon - show inline with potential input -->
									<div class="terminal-line">
										<span class="tmsg" class:user-input={e.isInput}>{e.text}</span>{#if $tacExecutionPaused && i === $termMessages.length - 1}<input
											type="text"
											class="terminal-input"
											bind:this={controller.terminalInputEl}
											bind:value={$currentInputLine}
											on:keydown={(e) => controller.handleTerminalInputKeydown(e)}
										/>{/if}
									</div>
								{/if}
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</aside>
	</div>
</div>

<style>
	:global(html) {
		height: 100%;
	}

	:global(body) {
		margin: 0;
		min-height: 100%;
	}

	.ide {
		--bg: #2b2b2f;
		--bg-soft: #2f2f34;
		--ink: #f2f2f2;
		--ink-muted: #c9c9cf;
		--accent: #ffffff;
		--outline: #ffffff;
		--panel: rgba(255, 255, 255, 0.03);
		--shadow: 0 0 0 2px var(--outline) inset;
		--layout-gap: 20px;
		--layout-pad: 16px;
		--frame-height: 842px;
		--editor-inset-x: 30px;
		--editor-inset-y: 24px;
		min-height: 100vh;
		width: 100%;
		min-width: 0;
		box-sizing: border-box;
		background-image: var(--bg-img);
		background-size: auto;
		background-position: top left;
		background-repeat: repeat;
		background-color: #26262a;
		color: var(--ink);
		font-family: 'Inter', Roboto, sans-serif;
		font-weight: 700;
	}

	.ide[data-theme='light'] {
		--bg: #f7f7fb;
		--bg-soft: #fff;
		--ink: #1f1f23;
		--ink-muted: #555;
		--accent: #111;
		--outline: #111;
		background-image: var(--bg-img);
		background-color: #e8e8ed;
	}

	.titlebar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: #77787e;
		color: #fff;
		padding: 8px 12px;
		user-select: none;
		width: 100%;
		box-sizing: border-box;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 600;
	}

	.logo {
		filter: grayscale(0.1);
		width: 30px;
		height: 30px;
		object-fit: contain;
	}

	.name {
		letter-spacing: 0.2px;
	}

	.win-controls {
		display: flex;
		gap: 8px;
	}

	.dot {
		width: 12px;
		height: 12px;
		border-radius: 999px;
		background: #cfcfd6;
		display: inline-block;
	}

	.grid {
		display: grid;
		width: 100%;
		max-width: 100%;
		box-sizing: border-box;
		grid-template-columns: minmax(0, 1.8fr) minmax(320px, 0.85fr);
		gap: var(--layout-gap);
		padding: var(--layout-pad);
	}

	.toolbar {
		display: flex;
		width: 100%;
		align-items: center;
		gap: 8px;
		flex-wrap: wrap;
		background: transparent;
		color: var(--ink);
		border-radius: 8px;
		cursor: pointer;
		margin: 0 0 8px 0;
	}

	.pill {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 28px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
	}

	.pill.active {
		background: rgba(255, 255, 255, 0.08);
	}

	.spacer {
		flex: 1;
	}

	.icon-btn {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
	}

	.icon {
		width: 18px;
		height: 18px;
		object-fit: contain;
	}

	.left {
		display: flex;
		flex-direction: column;
		gap: var(--layout-gap);
		min-width: 0;
		width: 100%;
		padding: 0;
		margin: 0;
	}

	.panel {
		border-radius: 14px;
		padding: 10px;
		border: 4px solid var(--outline);
		box-shadow: var(--shadow);
	}

	.editor {
		position: relative;
		overflow: hidden;
		height: var(--frame-height);
		min-height: var(--frame-height);
		padding: 0;
		border: none;
		box-shadow: none;
	}

	.editor-frame {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: fill;
		object-position: left top;
		pointer-events: none;
		z-index: 0;
	}

	.editor-area {
		position: absolute;
		inset: var(--editor-inset-y) var(--editor-inset-x);
		background: transparent;
		z-index: 1;
		box-sizing: border-box;
		margin: 0;
		border: none;
	}

	.table-title-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 8px;
		color: var(--ink);
		border: none;
		box-shadow: none;
	}

	.counter {
		display: flex;
		align-items: center;
		gap: 8px;
		border-radius: 10px;
		margin: 0;
		transform: scale(0.85);
		transform-origin: right center;
	}

	.terminal-content {
		display: flex;
		flex-direction: column;
		gap: 0;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace;
		font-size: 13px;
		line-height: 1.5;
	}

	.terminal-line {
		display: flex;
		flex-direction: row;
		align-items: baseline;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace;
		font-size: 13px;
		line-height: 1.5;
		white-space: pre-wrap;
	}

	.trow {
		display: flex;
		gap: 8px;
		align-items: flex-start;
		padding: 0;
		margin: 0;
		color: var(--ink);
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace;
		font-size: 13px;
		line-height: 1.5;
	}

	.terminal-input {
		border: none;
		background: transparent;
		color: var(--ink);
		padding: 0;
		margin: 0;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace;
		font-size: 13px;
		font-weight: 400;
		outline: none;
		line-height: 1.5;
		flex: 1;
		min-width: 100px;
	}

	.terminal-input:focus {
		outline: none;
	}

	.ticon-img {
		width: 16px;
		height: 16px;
		object-fit: contain;
	}

	.tmsg {
		white-space: pre-wrap;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace;
		font-size: 13px;
		line-height: 1.5;
		font-weight: 400;
		tab-size: 4;
		-moz-tab-size: 4;
		-o-tab-size: 4;
	}

	.right {
		display: flex;
		width: 100%;
		flex-direction: column;
		gap: var(--layout-gap);
		min-width: 0;
		background: transparent;
		color: var(--ink);
		padding: 0;
		margin: 0;
		border-radius: 8px;
	}

	.actions {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
		justify-content: space-between;
		margin: 0;
	}

	.btn {
		flex: 1 1 180px;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 10px;
		cursor: pointer;
		scale: 1;
	}

	.table {
		height: auto;
		min-height: var(--frame-height);
		display: flex;
		flex-direction: column;
		background-position: left;
		background-repeat: no-repeat;
		border: none;
		box-shadow: none;
	}

	.table-title {
		text-align: left;
		font-weight: 700;
		margin-bottom: 0;
		border: none;
		box-shadow: none;
	}

	.table-body {
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 6px;
		flex: 1;
		min-height: 0;
		overflow-y: auto;
		overflow-x: hidden;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.empty {
		opacity: 0.7;
		text-align: center;
		padding: 12px;
	}

	.user-input {
		color: #69f0ae !important;
	}

	@media (max-width: 1280px) {
		.grid {
			grid-template-columns: 1fr;
		}
		.ide {
			--frame-height: 700px;
		}
	}

	/* CodeMirror Global Overrides */
	:global(.CodeMirror),
	:global(.CodeMirror-scroll),
	:global(.CodeMirror-gutters),
	:global(.CodeMirror pre) {
		background: transparent !important;
		color: inherit !important;
	}

	:global(.CodeMirror) {
		position: absolute !important;
		inset: var(--editor-inset-y) var(--editor-inset-x) !important;
		width: auto !important;
		height: auto !important;
		box-shadow: none !important;
		border: none !important;
		z-index: 1 !important;
		outline: none !important;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace !important;
		margin: 0 !important;
	}

	:global(.CodeMirror-scroll) {
		overflow-x: hidden !important;
		overflow-y: auto !important;
		white-space: pre-wrap !important;
	}

	:global(.CodeMirror pre) {
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono',
			monospace !important;
		font-size: 18px !important;
		line-height: 20px !important;
		padding: 0 8px !important;
		margin: 0 !important;
		white-space: pre-wrap !important;
	}

	/* CodeMirror Theme-Specific Styles */
	:global(.ide[data-theme='dark'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #ffffff !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #000000 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror) {
		color: #d4d4d4 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror) {
		color: #1f1f23 !important;
	}

	/* Error/Warning Markers */
	:global(.error-underline) {
		border-bottom: 2px solid #ff0000 !important;
		background-color: rgba(255, 0, 0, 0.1) !important;
	}

	:global(.warning-underline) {
		border-bottom: 2px solid #ffa500 !important;
		background-color: rgba(255, 165, 0, 0.08) !important;
	}

	/* Platter Syntax Highlighting - Dark Theme */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-keyword) {
		color: #c586c0 !important;
		font-weight: 500 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-type) {
		color: #4ec9b0 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-builtin) {
		color: #dcdcaa !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-atom) {
		color: #569cd6 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-variable) {
		color: #9cdcfe !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-string) {
		color: #ce9178 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-string-2) {
		color: #d7ba7d !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-number) {
		color: #b5cea8 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-operator) {
		color: #d4d4d4 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-punctuation) {
		color: #d4d4d4 !important;
	}

	:global(.ide[data-theme='dark'] .CodeMirror .cm-comment) {
		color: #999999 !important;
		font-style: italic !important;
	}

	/* Platter Syntax Highlighting - Light Theme */
	:global(.ide[data-theme='light'] .CodeMirror .cm-keyword) {
		color: #7c00a8 !important;
		font-weight: 500 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-type) {
		color: #1a5c6f !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-builtin) {
		color: #5c4a1e !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-atom) {
		color: #0000cc !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-variable) {
		color: #000c5a !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-string) {
		color: #7d0e0e !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-string-2) {
		color: #cc0000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-number) {
		color: #07603f !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-operator) {
		color: #000000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-punctuation) {
		color: #000000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-comment) {
		color: #666666 !important;
		font-style: italic !important;
	}
</style>
