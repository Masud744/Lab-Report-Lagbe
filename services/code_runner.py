"""
Code execution service.
Supports:
1. Self-hosted or mirrored Piston API (via PISTON_URL)
2. Official Piston API with authorization token (via PISTON_KEY)
3. Judge0 CE on RapidAPI (via RAPIDAPI_KEY)
4. Safe local execution for supported runtimes (when ENABLE_LOCAL_RUNNER=true)
5. Graceful fallback signaling so callers can use AI output simulation.
"""

import os
import re
import time
import shutil
import asyncio
import tempfile
import subprocess
import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PISTON_URL = os.getenv("PISTON_URL", "https://emkc.org/api/v2/piston")
ENABLE_LOCAL_RUNNER = os.getenv("ENABLE_LOCAL_RUNNER", "true").lower() in ("1", "true", "yes")

# Language map for Piston & UI
PISTON_LANGUAGES = {
    "python": {"piston": "python", "version": "3.10.0", "label": "Python"},
    "c++": {"piston": "c++", "version": "10.2.0", "label": "C++"},
    "c": {"piston": "c", "version": "10.2.0", "label": "C"},
    "java": {"piston": "java", "version": "15.0.2", "label": "Java"},
    "dart": {"piston": "dart", "version": "2.19.6", "label": "Dart"},
    "javascript": {"piston": "javascript", "version": "18.15.0", "label": "JavaScript"},
    "typescript": {"piston": "typescript", "version": "5.0.3", "label": "TypeScript"},
    "sql": {"piston": "sqlite3", "version": "3.36.0", "label": "SQL"},
    "go": {"piston": "go", "version": "1.16.2", "label": "Go"},
    "rust": {"piston": "rust", "version": "1.68.2", "label": "Rust"},
    "kotlin": {"piston": "kotlin", "version": "1.8.20", "label": "Kotlin"},
    "csharp": {"piston": "csharp", "version": "6.12.0", "label": "C#"},
    "php": {"piston": "php", "version": "8.2.3", "label": "PHP"},
    "ruby": {"piston": "ruby", "version": "3.0.1", "label": "Ruby"},
    "swift": {"piston": "swift", "version": "5.3.3", "label": "Swift"},
    "r": {"piston": "r", "version": "4.1.1", "label": "R"},
    "bash": {"piston": "bash", "version": "5.2.0", "label": "Bash"},
    "matlab": {"piston": "octave", "version": "6.4.0", "label": "MATLAB / Octave"},
    "arduino": {"piston": "c++", "version": "10.2.0", "label": "Arduino (C++)"},
    "lua": {"piston": "lua", "version": "5.4.4", "label": "Lua"},
    "perl": {"piston": "perl", "version": "5.36.0", "label": "Perl"},
    "scala": {"piston": "scala", "version": "3.2.2", "label": "Scala"},
}

LANGUAGE_MAP = PISTON_LANGUAGES

JUDGE0_LANGUAGES = {
    "python": 71,
    "dart": 90,
    "c++": 54,
    "c": 50,
    "java": 62,
    "javascript": 63,
    "typescript": 74,
    "go": 60,
    "rust": 73,
    "ruby": 72,
    "php": 68,
    "kotlin": 78,
    "swift": 83,
    "r": 80,
    "bash": 46,
    "sql": 82,
}

# Patterns that indicate interactive/GUI programs not suitable for headless CLI execution
_NON_HEADLESS_PATTERNS = [
    r"\bpygame\b",
    r"\bOpenGL\b",
    r"\btkinter\b",
    r"\bturtle\b",
    r"\bPyQt\b",
    r"\bcv2\.imshow\b",
    r"\bplt\.show\b",
    r"\bglutMainLoop\b",
]


def _is_gui_or_interactive(code: str) -> bool:
    for pat in _NON_HEADLESS_PATTERNS:
        if re.search(pat, code):
            return True
    return False


class CodeRunner:
    def __init__(self, piston_url: str = None, piston_key: str = None):
        self.piston_url = (piston_url or DEFAULT_PISTON_URL).rstrip("/")
        self.piston_key = piston_key or os.getenv("PISTON_KEY")
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.client = httpx.AsyncClient(timeout=20.0)

    async def execute(self, code: str, language: str, stdin: str = "") -> dict:
        """
        Execute code via local runtime (if enabled), Piston, or Judge0.
        Returns: {"output": str, "error": str, "success": bool, "engine": str, "execution_ms": int}
        """
        lang_key = language.lower().strip()
        start = time.perf_counter()

        # Skip live execution for GUI/OpenGL apps (avoid blocking/opening desktop windows)
        if _is_gui_or_interactive(code):
            return {
                "output": "",
                "error": "GUI/OpenGL program detected; routing to visual/simulated output.",
                "success": False,
                "engine": "skipped-gui",
                "execution_ms": int((time.perf_counter() - start) * 1000),
            }

        # 1. Try local runtime first when enabled (fast, accurate, zero network lag)
        if ENABLE_LOCAL_RUNNER and lang_key in ("python", "c", "c++", "java", "javascript", "dart", "bash"):
            local_res = await asyncio.to_thread(self._execute_local, code, lang_key, stdin)
            if local_res is not None:
                local_res["execution_ms"] = int((time.perf_counter() - start) * 1000)
                return local_res

        # 2. Try Piston (only if self-hosted or key configured)
        if self.piston_key or "emkc.org" not in self.piston_url:
            piston_result = await self._execute_piston(code, lang_key)
            piston_result["execution_ms"] = int((time.perf_counter() - start) * 1000)
            if piston_result.get("success"):
                return piston_result

        # 3. Try RapidAPI Judge0 if configured
        if self.rapidapi_key and lang_key in JUDGE0_LANGUAGES:
            judge_result = await self._execute_judge0(code, lang_key)
            judge_result["execution_ms"] = int((time.perf_counter() - start) * 1000)
            if judge_result.get("success"):
                return judge_result

        return {
            "output": "",
            "error": "No live runtime available for this language; fallback to AI simulation.",
            "success": False,
            "engine": "unavailable",
            "execution_ms": int((time.perf_counter() - start) * 1000),
        }

    def _execute_local(self, code: str, lang_key: str, stdin: str = "") -> dict | None:
        """Safely compile/run code locally inside an isolated temporary directory with strict timeout."""
        timeout_sec = 5
        try:
            with tempfile.TemporaryDirectory(prefix="lrg_run_") as tmpdir:
                cmd = None
                compile_cmd = None

                if lang_key == "python":
                    exe = shutil.which("python3")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.py")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    cmd = [exe, "-I", src]

                elif lang_key == "c":
                    exe = shutil.which("gcc")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.c")
                    out_bin = os.path.join(tmpdir, "main")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    compile_cmd = [exe, src, "-o", out_bin, "-lm"]
                    cmd = [out_bin]

                elif lang_key == "c++":
                    exe = shutil.which("g++")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.cpp")
                    out_bin = os.path.join(tmpdir, "main")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    compile_cmd = [exe, "-std=c++17", src, "-o", out_bin]
                    cmd = [out_bin]

                elif lang_key == "java":
                    javac = shutil.which("javac")
                    java = shutil.which("java")
                    if not javac or not java:
                        return None
                    class_match = re.search(r"public\s+class\s+([A-Za-z_]\w*)", code)
                    class_name = class_match.group(1) if class_match else "Main"
                    src = os.path.join(tmpdir, f"{class_name}.java")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    compile_cmd = [javac, src]
                    cmd = [java, "-cp", tmpdir, class_name]

                elif lang_key == "javascript":
                    exe = shutil.which("node")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.js")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    cmd = [exe, src]

                elif lang_key == "dart":
                    exe = shutil.which("dart")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.dart")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    cmd = [exe, "run", src]

                elif lang_key == "bash":
                    exe = shutil.which("bash")
                    if not exe:
                        return None
                    src = os.path.join(tmpdir, "main.sh")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(code)
                    cmd = [exe, src]

                if not cmd:
                    return None

                if compile_cmd:
                    cproc = subprocess.run(
                        compile_cmd,
                        cwd=tmpdir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=10,
                    )
                    if cproc.returncode != 0:
                        err = cproc.stderr.decode("utf-8", errors="replace").strip()
                        return {
                            "output": "",
                            "error": f"Compilation Error:\n{err[:1000]}",
                            "success": False,
                            "engine": "local",
                        }

                rproc = subprocess.run(
                    cmd,
                    cwd=tmpdir,
                    input=stdin.encode("utf-8") if stdin else b"",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout_sec,
                )
                stdout = rproc.stdout.decode("utf-8", errors="replace").strip()
                stderr = rproc.stderr.decode("utf-8", errors="replace").strip()

                if rproc.returncode != 0:
                    return {
                        "output": stdout,
                        "error": stderr or f"Exited with code {rproc.returncode}",
                        "success": False,
                        "engine": "local",
                    }
                return {
                    "output": stdout or stderr or "(Program finished with no console output)",
                    "error": "",
                    "success": True,
                    "engine": "local",
                }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": f"Execution timed out after {timeout_sec}s (possible infinite loop or waiting for input).",
                "success": False,
                "engine": "local",
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "success": False,
                "engine": "local",
            }

    async def _execute_piston(self, code: str, lang_key: str) -> dict:
        lang_info = PISTON_LANGUAGES.get(lang_key)
        if not lang_info:
            return {"output": "", "error": f"Language not configured for Piston: {lang_key}", "success": False, "engine": "piston"}

        headers = {"Content-Type": "application/json"}
        if self.piston_key:
            headers["Authorization"] = self.piston_key

        payload = {
            "language": lang_info["piston"],
            "version": lang_info["version"],
            "files": [{"content": code}],
        }

        try:
            resp = await self.client.post(f"{self.piston_url}/execute", json=payload, headers=headers)
            if resp.status_code != 200:
                return {"output": "", "error": f"Piston HTTP {resp.status_code}", "success": False, "engine": "piston"}

            data = resp.json()
            run_data = data.get("run", {})
            compile_data = data.get("compile", {})
            stdout = run_data.get("stdout", "") or ""
            stderr = run_data.get("stderr", "") or ""
            compile_stderr = compile_data.get("stderr", "") or ""

            if compile_stderr.strip():
                return {"output": "", "error": compile_stderr.strip(), "success": False, "engine": "piston"}
            if run_data.get("code", 0) != 0:
                return {"output": stdout.strip() or stderr.strip(), "error": stderr.strip() or "Runtime error", "success": False, "engine": "piston"}
            return {"output": stdout.strip() or stderr.strip(), "error": "", "success": True, "engine": "piston"}
        except Exception as e:
            return {"output": "", "error": f"Piston unreachable: {str(e)}", "success": False, "engine": "piston"}

    async def _execute_judge0(self, code: str, lang_key: str) -> dict:
        lang_id = JUDGE0_LANGUAGES.get(lang_key)
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        payload = {"language_id": lang_id, "source_code": code, "stdin": "", "cpu_time_limit": 10}
        try:
            resp = await self.client.post(
                "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true",
                json=payload,
                headers=headers,
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                stdout = data.get("stdout") or ""
                stderr = data.get("stderr") or ""
                if data.get("status", {}).get("id", 0) == 3:
                    return {"output": stdout.strip(), "error": "", "success": True, "engine": "judge0"}
                return {"output": stdout.strip(), "error": stderr.strip() or "Non-zero exit", "success": False, "engine": "judge0"}
            return {"output": "", "error": f"Judge0 status {resp.status_code}", "success": False, "engine": "judge0"}
        except Exception as e:
            return {"output": "", "error": str(e), "success": False, "engine": "judge0"}
