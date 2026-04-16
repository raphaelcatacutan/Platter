import unittest
from pathlib import Path

from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.intermediate_code.ir_generator import IRGenerator
from app.code_optimization.optimizer_manager import OptimizationLevel, OptimizerManager
from app.interpreter.ir_interpreter import run_tac


MACHINE_PROBLEMS_DIR = Path(__file__).resolve().parent / "machine_problems"
RUNTIME_FIXES_DIR = Path(__file__).resolve().parent / "runtime_fixes"


def parse_machine_problem_file(file_path: Path) -> dict:
    """
    Parse a machine problem file with this format:

    source code
    --end
    input1
    input2
    --end
    output line 1
    output line 2
    """
    raw_text = file_path.read_text(encoding="utf-8-sig")
    lines = raw_text.splitlines()

    end_indexes = [i for i, line in enumerate(lines) if line.strip() == "--end"]
    if len(end_indexes) < 2:
        raise ValueError(
            f"{file_path.name}: expected exactly two '--end' separators for "
            "source/inputs/output blocks."
        )

    first_end = end_indexes[0]
    second_end = end_indexes[1]

    code = "\n".join(lines[:first_end]).strip()
    inputs = lines[first_end + 1:second_end]
    expected_output = "\n".join(lines[second_end + 1:])

    return {
        "name": file_path.name,
        "code": code,
        "inputs": inputs,
        "expected_output": expected_output,
    }


def load_cases(directory: Path) -> list[dict]:
    case_files = sorted(directory.glob("*.platter"))
    return [parse_machine_problem_file(path) for path in case_files]


def parse_runtime_expectations(expected_block: str) -> dict:
    """
    Parse runtime-fixes expectations from the expected output block.

    Supported directives:
    [[RUNTIME_ERROR]]<message>
    [[EXIT_MESSAGE]]<message>

    Any non-directive lines are treated as expected runtime output.
    """
    runtime_error = None
    exit_message = None
    output_lines = []

    for raw_line in expected_block.splitlines():
        line = raw_line.strip()
        if line.startswith("[[RUNTIME_ERROR]]"):
            runtime_error = line.replace("[[RUNTIME_ERROR]]", "", 1).strip()
        elif line.startswith("[[EXIT_MESSAGE]]"):
            exit_message = line.replace("[[EXIT_MESSAGE]]", "", 1).strip()
        else:
            output_lines.append(raw_line)

    return {
        "runtime_error": runtime_error,
        "exit_message": exit_message,
        "output": "\n".join(output_lines).rstrip(),
    }


def run_compiler(code: str, inputs: list[str]) -> dict:
    tokens = Lexer(code).tokenize()
    filtered_tokens = [
        t for t in tokens if t.type not in ("comment", "space", "newline", "tab")
    ]

    Parser(filtered_tokens).parse_program()

    ast = ASTParser(filtered_tokens).parse_program()
    _, error_handler = analyze_program(ast)
    if error_handler.has_errors():
        errors = "\n".join(str(err) for err in error_handler.get_errors())
        return {
            "success": False,
            "stage": "semantic",
            "error": errors,
            "output": "",
        }

    tac, _ = IRGenerator().generate(ast)
    optimized_tac = OptimizerManager(OptimizationLevel.STANDARD).optimize_tac(tac)
    exec_result = run_tac(optimized_tac, stdin_lines=inputs)

    if not exec_result.get("success"):
        return {
            "success": False,
            "stage": "runtime",
            "error": exec_result.get("error", "Unknown runtime error"),
            "output": exec_result.get("output", ""),
            "exit_message": exec_result.get("exit_message", ""),
        }

    return {
        "success": True,
        "stage": "done",
        "error": "",
        "output": exec_result.get("output", ""),
        "exit_message": exec_result.get("exit_message", ""),
    }


class TestCompiler(unittest.TestCase):
    def test_compiler_cases(self):
        self.maxDiff = None
        cases = load_cases(MACHINE_PROBLEMS_DIR)
        if not cases:
            self.skipTest(f"No case files found in {MACHINE_PROBLEMS_DIR}")

        for case in cases:
            with self.subTest(case=case["name"]):
                result = run_compiler(case["code"], case["inputs"])

                self.assertTrue(
                    result["success"],
                    msg=(
                        f"Case {case['name']} failed at stage '{result['stage']}'.\n"
                        f"Error: {result['error']}"
                    ),
                )
                self.assertEqual(result["output"].rstrip(), case["expected_output"].rstrip())

    def test_runtime_fix_cases(self):
        self.maxDiff = None
        cases = load_cases(RUNTIME_FIXES_DIR)
        if not cases:
            self.skipTest(f"No case files found in {RUNTIME_FIXES_DIR}")

        for case in cases:
            with self.subTest(case=case["name"]):
                result = run_compiler(case["code"], case["inputs"])
                expected = parse_runtime_expectations(case["expected_output"])

                expected_runtime_error = expected["runtime_error"]
                expected_exit_message = expected["exit_message"]
                expected_output = expected["output"]

                if expected_runtime_error:
                    self.assertFalse(
                        result["success"],
                        msg=f"Case {case['name']} expected runtime failure but succeeded."
                    )
                    self.assertEqual(result["stage"], "runtime")
                    self.assertEqual(result["error"], expected_runtime_error)
                    # Frontend owns the prefix; runtime should return raw message.
                    self.assertNotIn("Runtime Error:", result["error"])
                    continue

                self.assertTrue(
                    result["success"],
                    msg=(
                        f"Case {case['name']} failed at stage '{result['stage']}'.\n"
                        f"Error: {result['error']}"
                    ),
                )

                self.assertEqual(result["output"].rstrip(), expected_output.rstrip())

                if expected_exit_message is not None:
                    self.assertEqual(
                        result.get("exit_message", "").strip(),
                        expected_exit_message.strip(),
                        msg=f"Case {case['name']} exit message mismatch."
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
