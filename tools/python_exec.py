"""Runs numeric Python (numpy/scipy) in a subprocess with a timeout.
NOT a security sandbox: run engbot inside Docker (provided) and don't expose it to untrusted users."""
import subprocess, sys, tempfile
from engbot.core.registry import register_tool


class PythonExecTool:
    name = "python"
    description = "Run Python 3 (numpy, scipy, sympy available) for numerics and simulation. Use print() for output."
    args_schema = {"code": "Python source"}

    def run(self, code: str, timeout: int = 30) -> str:
        with tempfile.TemporaryDirectory() as d:
            try:
                p = subprocess.run([sys.executable, "-I", "-c", code], cwd=d, capture_output=True,
                                   text=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                return f"Timed out after {timeout}s"
        return (p.stdout + p.stderr).strip() or "(no output)"


register_tool(PythonExecTool())
