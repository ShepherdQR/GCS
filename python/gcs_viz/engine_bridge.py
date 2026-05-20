import subprocess
import os


class EngineBridge:
    def __init__(self, exe_path: str = None):
        if exe_path is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            python_dir = os.path.normpath(os.path.join(package_dir, ".."))
            repo_dir = os.path.normpath(os.path.join(python_dir, ".."))
            env_exe = os.environ.get("GCS_EXE")
            candidates = [
                env_exe,
                os.path.join(repo_dir, "out", "build", "clang-ninja", "GCS.exe"),
            ]
            exe_path = None
            for c in candidates:
                if not c:
                    continue
                c = os.path.normpath(c)
                if os.path.isfile(c):
                    exe_path = c
                    break
            if exe_path is None:
                exe_path = os.path.normpath(candidates[1])
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
                cwd=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
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
