import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from app.config.settings import get_settings
from app.models.entities import Verdict


@dataclass
class CaseExecution:
    input: str
    expected_output: str
    actual_output: str
    stderr: str
    status: Verdict
    execution_time: float
    memory: int


@dataclass
class JudgeExecution:
    status: Verdict
    execution_time: float
    memory: int
    cases: list[CaseExecution]


class Executor:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run_cases(
        self,
        language: str,
        source_code: str,
        cases: list[tuple[str, str]],
        time_limit: float,
        memory_limit: int,
    ) -> JudgeExecution:
        if language.lower() != "python":
            return JudgeExecution(Verdict.compilation_error, 0, 0, [])

        results: list[CaseExecution] = []
        worst_status = Verdict.accepted
        total_time = 0.0

        for input_text, expected_output in cases:
            result = self._run_python(source_code, input_text, expected_output, time_limit, memory_limit)
            results.append(result)
            total_time += result.execution_time
            if result.status != Verdict.accepted and worst_status == Verdict.accepted:
                worst_status = result.status

        max_memory = max((case.memory for case in results), default=0)
        return JudgeExecution(worst_status, total_time, max_memory, results)

    def _run_python(
        self,
        source_code: str,
        input_text: str,
        expected_output: str,
        time_limit: float,
        memory_limit: int,
    ) -> CaseExecution:
        if self.settings.executor_use_docker:
            return self._run_python_docker(source_code, input_text, expected_output, time_limit, memory_limit)
        return self._run_python_local(source_code, input_text, expected_output, time_limit)

    def _run_python_local(
        self,
        source_code: str,
        input_text: str,
        expected_output: str,
        time_limit: float,
    ) -> CaseExecution:
        started_at = time.perf_counter()
        try:
            completed = subprocess.run(
                [sys.executable, "-c", source_code],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=time_limit,
                check=False,
            )
            elapsed = time.perf_counter() - started_at
        except subprocess.TimeoutExpired:
            return CaseExecution(input_text, expected_output, "", "", Verdict.time_limit_exceeded, time_limit, 0)

        return self._classify(input_text, expected_output, completed.stdout, completed.stderr, completed.returncode, elapsed, 0)

    def _run_python_docker(
        self,
        source_code: str,
        input_text: str,
        expected_output: str,
        time_limit: float,
        memory_limit: int,
    ) -> CaseExecution:
        Path(self.settings.executor_workspace_root).mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=self.settings.executor_workspace_root) as tmpdir:
            source_path = Path(tmpdir) / "main.py"
            source_path.write_text(source_code, encoding="utf-8")
            command = [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--cpus",
                "1",
                "--memory",
                f"{memory_limit}m",
                "--pids-limit",
                "64",
                "--read-only",
                "-v",
                f"{tmpdir}:/workspace:ro",
                "-w",
                "/workspace",
                "python:3.12-slim",
                "python",
                "main.py",
            ]
            started_at = time.perf_counter()
            try:
                completed = subprocess.run(
                    command,
                    input=input_text,
                    capture_output=True,
                    text=True,
                    timeout=time_limit + 1,
                    check=False,
                )
                elapsed = time.perf_counter() - started_at
            except subprocess.TimeoutExpired:
                return CaseExecution(input_text, expected_output, "", "", Verdict.time_limit_exceeded, time_limit, 0)

        return self._classify(input_text, expected_output, completed.stdout, completed.stderr, completed.returncode, elapsed, 0)

    @staticmethod
    def _classify(
        input_text: str,
        expected_output: str,
        actual_output: str,
        stderr: str,
        return_code: int,
        elapsed: float,
        memory: int,
    ) -> CaseExecution:
        if return_code != 0:
            status = Verdict.runtime_error
        elif actual_output.rstrip() == expected_output.rstrip():
            status = Verdict.accepted
        elif actual_output.strip() == expected_output.strip():
            status = Verdict.presentation_error
        else:
            status = Verdict.wrong_answer
        return CaseExecution(input_text, expected_output, actual_output, stderr, status, elapsed, memory)
