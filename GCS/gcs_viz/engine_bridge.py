import subprocess
import os
import json
from typing import Optional


class EngineBridge:
    def __init__(self, exe_path: str = None):
        if exe_path is None:
            candidates = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "x64", "Debug", "GCS.exe"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "x64", "Debug", "GCS.exe"),
            ]
            exe_path = None
            for c in candidates:
                c = os.path.normpath(c)
                if os.path.isfile(c):
                    exe_path = c
                    break
            if exe_path is None:
                exe_path = os.path.normpath(candidates[0])
        self.exe_path = exe_path

    def is_available(self) -> bool:
        return os.path.isfile(self.exe_path)

    def run_pipeline(self, input_path: str) -> dict:
        if not self.is_available():
            return {"error": f"GCS.exe not found at {self.exe_path}"}
        abs_input_path = os.path.abspath(input_path)
        if not os.path.isfile(abs_input_path):
            return {"error": f"Input file not found: {abs_input_path}"}
        try:
            result = subprocess.run(
                [self.exe_path, abs_input_path],
                capture_output=True, text=True, timeout=30,
                cwd=os.path.dirname(self.exe_path)
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"error": "GCS.exe timed out after 30s"}
        except Exception as e:
            return {"error": str(e)}

    def solve(self, input_path: str) -> dict:
        result = self.run_pipeline(input_path)
        if "error" in result:
            return result
        if result.get("returncode") != 0:
            return {"error": f"GCS.exe returned code {result.get('returncode')}", "stderr": result.get("stderr", "")}
        return {"status": "completed", "output": result.get("stdout", "")}
