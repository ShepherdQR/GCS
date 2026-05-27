import json
import os
import subprocess
import tempfile


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
        self._repo_root = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        )

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

    def solve_with_evidence(self, input_path: str) -> dict:
        """Run GCS.exe and also capture replay evidence as structured JSON.

        Returns a dict with:
            status: "completed" or "error"
            output: stdout text from the solver
            evidence: parsed replay evidence dict (or None)
            evidence_path: path to the saved JSON file (or None)
        """
        result = self.run_pipeline(input_path)
        if "error" in result:
            return result
        if result.get("returncode") != 0:
            return {
                "status": "error",
                "error": f"GCS.exe returned code {result.get('returncode')}",
                "stderr": result.get("stderr", ""),
                "output": result.get("stdout", ""),
            }

        # Also run with --save-replay-evidence to capture structured evidence
        replay_path = None
        evidence = None
        try:
            abs_input = os.path.abspath(input_path)
            fd, replay_path = tempfile.mkstemp(
                suffix=".json", prefix="gcs_replay_"
            )
            os.close(fd)
            replay_result = subprocess.run(
                [self.exe_path, abs_input,
                 "--save-replay-evidence", replay_path],
                capture_output=True, text=True, timeout=30,
                cwd=self._repo_root,
            )
            if replay_result.returncode == 0 and os.path.isfile(replay_path):
                try:
                    with open(replay_path, "r", encoding="utf-8") as fh:
                        evidence = json.load(fh)
                except (json.JSONDecodeError, OSError):
                    evidence = None
        except (subprocess.TimeoutExpired, OSError):
            pass

        return {
            "status": "completed",
            "output": result.get("stdout", ""),
            "evidence": evidence,
            "evidence_path": replay_path,
        }
