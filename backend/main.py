from __future__ import annotations

import json
import queue
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import multiprocessing as mp
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_ROOT = Path(__file__).resolve().parent.parent / "platter-compiler-sveltejs" / "static" / "python"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import ASTReader
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_for_console
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.output_formatter import IRFormatter
from app.code_optimization.optimizer_manager import OptimizerManager, OptimizationLevel

RUN_RESPONSE_TIMEOUT_SEC = 0.4


class CodeRequest(BaseModel):
    code: str


class SemanticRequest(BaseModel):
    code: str
    run_ir_pipeline: bool = False


class InputRequest(BaseModel):
    input: str


def normalize_curly_quotes(text: str) -> str:
    return (
        text.replace("\u201C", "\"")
        .replace("\u201D", "\"")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\r\n", "\n")
    )


def _format_execution_result(exec_result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "execution_output": exec_result.get("output", ""),
        "execution_success": bool(exec_result.get("success")),
        "execution_paused": bool(exec_result.get("paused")),
        "execution_error": exec_result.get("error", ""),
        "execution_exit_message": exec_result.get("exit_message", ""),
        "execution_terminate_message": exec_result.get("terminate_message", ""),
        "execution_globals": json.dumps(exec_result.get("globals", {}) or {}),
    }


def _worker_main(cmd_queue: mp.Queue, resp_queue: mp.Queue, app_root: str) -> None:
    if app_root not in sys.path:
        sys.path.insert(0, app_root)

    from app.interpreter.ir_interpreter import TACInterpreter

    interpreter: Optional[TACInterpreter] = None

    while True:
        cmd = cmd_queue.get()
        cmd_type = cmd.get("type")

        if cmd_type == "shutdown":
            break

        if cmd_type == "start":
            optimized_tac = cmd.get("optimized_tac")
            interpreter = TACInterpreter(optimized_tac)
            exec_result = interpreter.run()
            resp_queue.put(_format_execution_result(exec_result))
            continue

        if cmd_type == "input":
            if interpreter is None:
                resp_queue.put({"execution_error": "No active interpreter", "execution_success": False})
                continue
            interpreter.stdin_lines.append(cmd.get("input", ""))
            exec_result = interpreter.run()
            resp_queue.put(_format_execution_result(exec_result))
            continue

        if cmd_type == "stop":
            interpreter = None
            resp_queue.put({"execution_stopped": True})


class ExecutionManager:
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.process: Optional[mp.Process] = None
        self.cmd_queue: Optional[mp.Queue] = None
        self.resp_queue: Optional[mp.Queue] = None

    def _start_process(self) -> None:
        self.cmd_queue = mp.Queue()
        self.resp_queue = mp.Queue()
        self.process = mp.Process(
            target=_worker_main,
            args=(self.cmd_queue, self.resp_queue, str(self.app_root)),
            daemon=True,
        )
        self.process.start()

    def _ensure_process(self) -> None:
        if self.process is None or not self.process.is_alive():
            self._start_process()

    def _terminate_process(self) -> None:
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1)
        self.process = None
        self.cmd_queue = None
        self.resp_queue = None

    def start(self, optimized_tac: List[Any]) -> Optional[Dict[str, Any]]:
        self._terminate_process()
        self._ensure_process()
        if not self.cmd_queue or not self.resp_queue:
            return None
        self.cmd_queue.put({"type": "start", "optimized_tac": optimized_tac})
        return self._wait_for_result(RUN_RESPONSE_TIMEOUT_SEC)

    def send_input(self, line: str) -> Optional[Dict[str, Any]]:
        if not self.process or not self.process.is_alive() or not self.cmd_queue or not self.resp_queue:
            return None
        self.cmd_queue.put({"type": "input", "input": line})
        return self._wait_for_result(RUN_RESPONSE_TIMEOUT_SEC)

    def poll(self) -> Optional[Dict[str, Any]]:
        if not self.resp_queue:
            return None
        try:
            return self.resp_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self) -> None:
        self._terminate_process()

    def _wait_for_result(self, timeout: float) -> Optional[Dict[str, Any]]:
        if not self.resp_queue:
            return None
        try:
            return self.resp_queue.get(timeout=timeout)
        except queue.Empty:
            return None


execution_manager = ExecutionManager(APP_ROOT)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/lexical")
def lexical(req: CodeRequest) -> Dict[str, Any]:
    code = normalize_curly_quotes(req.code)
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    result = []
    for token in tokens:
        if token is None:
            break
        result.append(
            {
                "type": token.type,
                "value": token.value or "\\0",
                "line": token.line,
                "col": token.col,
            }
        )
    return {"success": True, "tokens": result}


@app.post("/api/syntax")
def syntax(req: CodeRequest) -> Dict[str, Any]:
    code = normalize_curly_quotes(req.code)
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse_program()
        return {"success": True, "message": "No Syntax Error"}
    except SyntaxError as exc:
        error_msg = str(exc)
        match = re.search(r"line (\d+), col (\d+)", error_msg)
        if match:
            line = int(match.group(1))
            col = int(match.group(2))
            return {
                "success": False,
                "message": error_msg,
                "error": {"line": line, "col": col, "message": error_msg},
            }
        return {"success": False, "message": error_msg}
    except Exception as exc:
        return {"success": False, "message": f"Syntax analysis failed: {exc}"}


def _build_semantic_response(code: str, run_ir_pipeline: bool) -> Dict[str, Any]:
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    syntax_tokens = [
        t
        for t in tokens
        if t.type not in ("space", "tab", "newline", "comment_single", "comment_multi")
    ]
    syntax_parser = Parser(syntax_tokens)
    syntax_parser.parse_program()

    parser = ASTParser(tokens)
    ast = parser.parse_program()

    symbol_table, error_handler = analyze_program(ast)
    reader = ASTReader(ast)
    ast_json = reader.to_json(indent=2)

    symbol_table_data = format_symbol_table_for_console(symbol_table)
    symbol_table_json = json.dumps(symbol_table_data)

    ir_tac_text = ""
    ir_quads_text = ""
    ir_tac_optimized_text = ""

    error_list: List[str] = []
    error_markers: List[Dict[str, Any]] = []
    error_messages: List[str] = []
    warning_messages: List[str] = []

    if error_handler.has_errors():
        sorted_errors = sorted(
            error_handler.get_errors(),
            key=lambda e: 0 if e.severity.name == "ERROR" else 1,
        )
        for err in sorted_errors:
            error_list.append(str(err))
            severity_label = "ERROR" if err.severity.name == "ERROR" else "WARNING"
            if severity_label == "ERROR":
                error_messages.append(err.message)
            else:
                warning_messages.append(err.message)

            if err.line and err.column:
                error_markers.append(
                    {
                        "line": err.line,
                        "col": err.column,
                        "value": err.error_code or "semantic_error",
                        "message": err.message,
                        "severity": severity_label,
                    }
                )

        error_count = error_handler.get_error_count()
        warning_count = error_handler.get_warning_count()
        if error_count > 0:
            detailed_message = (
                f"Semantic analysis failed with {error_count} error(s) and {warning_count} warning(s)\n"
            )
        else:
            detailed_message = f"No semantic errors with {warning_count} warning(s)\n"

        for err in error_list:
            detailed_message += f"{err}\n"

        return {
            "success": False,
            "message": detailed_message.strip(),
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "errors": error_list,
            "semantic_errors": json.dumps(error_messages),
            "semantic_warnings": json.dumps(warning_messages),
            "error_markers": json.dumps(error_markers),
        }

    warning_messages_success: List[str] = []
    warning_markers_success: List[Dict[str, Any]] = []
    if error_handler.has_warnings():
        for warn in error_handler.get_errors():
            if warn.severity.name == "WARNING":
                warning_messages_success.append(warn.message)
                if warn.line and warn.column:
                    warning_markers_success.append(
                        {
                            "line": warn.line,
                            "col": warn.column,
                            "value": warn.error_code or "semantic_warning",
                            "message": warn.message,
                            "severity": "warning",
                        }
                    )

    warning_msg = (
        f" with {len(warning_messages_success)} warning(s)"
        if warning_messages_success
        else ""
    )

    if run_ir_pipeline:
        ir_gen = IRGenerator()
        tac_instructions, quad_table = ir_gen.generate(ast)
        formatter = IRFormatter()
        ir_tac_text = formatter.format_tac_text(tac_instructions)
        ir_quads_text = formatter.format_quadruples_text(quad_table)

        optimizer = OptimizerManager(OptimizationLevel.STANDARD)
        optimized_tac = optimizer.optimize_tac(tac_instructions)
        ir_tac_optimized_text = formatter.format_tac_text(optimized_tac)

        return {
            "success": True,
            "message": f"No semantic errors{warning_msg}",
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "optimized_tac": optimized_tac,
            "semantic_warnings": json.dumps(warning_messages_success),
            "error_markers": json.dumps(warning_markers_success),
        }

    return {
        "success": True,
        "message": f"No semantic errors{warning_msg}",
        "ast": ast_json,
        "symbol_table": symbol_table_json,
        "ir_tac": ir_tac_text,
        "ir_quads": ir_quads_text,
        "ir_tac_optimized": ir_tac_optimized_text,
        "semantic_warnings": json.dumps(warning_messages_success),
        "error_markers": json.dumps(warning_markers_success),
    }


@app.post("/api/semantic")
def semantic(req: SemanticRequest) -> Dict[str, Any]:
    code = normalize_curly_quotes(req.code)

    try:
        payload = _build_semantic_response(code, req.run_ir_pipeline)
    except SyntaxError as exc:
        error_msg = str(exc)
        match = re.search(r"line (\d+), col (\d+)", error_msg)
        if match:
            line = int(match.group(1))
            col = int(match.group(2))
            return {"success": False, "message": error_msg, "error": {"line": line, "col": col}}
        return {"success": False, "message": error_msg}
    except Exception as exc:
        return {"success": False, "message": f"Semantic analysis failed: {exc}"}

    if not payload.get("success") or not req.run_ir_pipeline:
        payload.update(
            {
                "execution_output": "",
                "execution_success": False,
                "execution_paused": False,
                "execution_error": "",
                "execution_exit_message": "",
                "execution_terminate_message": "",
                "execution_globals": json.dumps({}),
                "execution_running": False,
            }
        )
        payload.pop("optimized_tac", None)
        return payload

    optimized_tac = payload.pop("optimized_tac", None)
    if optimized_tac is None:
        payload["execution_error"] = "No IR available for execution"
        payload["execution_running"] = False
        payload["execution_success"] = False
        payload["execution_paused"] = False
        payload["execution_output"] = ""
        payload["execution_exit_message"] = ""
        payload["execution_terminate_message"] = ""
        payload["execution_globals"] = json.dumps({})
        return payload

    try:
        exec_result = execution_manager.start(optimized_tac)
    except Exception as exc:
        payload["execution_error"] = f"Execution start failed: {exc}"
        payload["execution_running"] = False
        payload["execution_success"] = False
        payload["execution_paused"] = False
        payload["execution_output"] = ""
        payload["execution_exit_message"] = ""
        payload["execution_terminate_message"] = ""
        payload["execution_globals"] = json.dumps({})
        return payload

    if exec_result:
        payload.update(exec_result)
        payload["execution_running"] = False
        return payload

    payload["execution_running"] = True
    payload["execution_output"] = ""
    payload["execution_success"] = False
    payload["execution_paused"] = False
    payload["execution_error"] = ""
    payload["execution_exit_message"] = ""
    payload["execution_terminate_message"] = ""
    payload["execution_globals"] = json.dumps({})
    return payload


@app.post("/api/execution/input")
def execution_input(req: InputRequest) -> Dict[str, Any]:
    exec_result = execution_manager.send_input(req.input)
    if exec_result is None:
        return {"execution_running": True}

    exec_result["execution_running"] = False
    return exec_result


@app.get("/api/execution/status")
def execution_status() -> Dict[str, Any]:
    exec_result = execution_manager.poll()
    if exec_result is None:
        return {"execution_running": True}
    exec_result["execution_running"] = False
    return exec_result


@app.post("/api/execution/stop")
def execution_stop() -> Dict[str, Any]:
    execution_manager.stop()
    return {"execution_stopped": True}
