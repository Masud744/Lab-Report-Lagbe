import httpx

PISTON_API = "https://emkc.org/api/v2/piston"

LANGUAGE_MAP = {
    "dart": {"language": "dart", "version": "2.19.6"},
    "python": {"language": "python", "version": "3.10.0"},
    "c++": {"language": "c++", "version": "10.2.0"},
    "c": {"language": "c", "version": "10.2.0"},
    "java": {"language": "java", "version": "15.0.2"},
    "javascript": {"language": "javascript", "version": "18.15.0"},
    "typescript": {"language": "typescript", "version": "5.0.3"},
    "go": {"language": "go", "version": "1.16.2"},
    "rust": {"language": "rust", "version": "1.68.2"},
    "ruby": {"language": "ruby", "version": "3.0.1"},
    "php": {"language": "php", "version": "8.2.3"},
    "kotlin": {"language": "kotlin", "version": "1.8.20"},
    "swift": {"language": "swift", "version": "5.3.3"},
    "r": {"language": "r", "version": "4.1.1"},
    "bash": {"language": "bash", "version": "5.2.0"},
}


class CodeRunner:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_runtimes(self) -> list[str]:
        """Get available language runtimes from Piston."""
        try:
            resp = await self.client.get(f"{PISTON_API}/runtimes")
            if resp.status_code == 200:
                runtimes = resp.json()
                return [r["language"] for r in runtimes]
        except Exception:
            pass
        return list(LANGUAGE_MAP.keys())

    async def execute(self, code: str, language: str) -> dict:
        """Execute code using Piston API. Returns {output, error, success}."""
        lang_key = language.lower().strip()
        lang_info = LANGUAGE_MAP.get(lang_key)

        if not lang_info:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "success": False
            }

        payload = {
            "language": lang_info["language"],
            "version": lang_info["version"],
            "files": [{"name": f"main.{self._get_extension(lang_key)}", "content": code}],
            "stdin": "",
            "compile_timeout": 15000,
            "run_timeout": 10000,
        }

        try:
            resp = await self.client.post(f"{PISTON_API}/execute", json=payload)
            if resp.status_code != 200:
                return {"output": "", "error": f"Piston API error: {resp.status_code}", "success": False}

            data = resp.json()
            run_data = data.get("run", {})
            compile_data = data.get("compile", {})

            # check compile errors first
            if compile_data and compile_data.get("stderr"):
                return {
                    "output": compile_data.get("output", ""),
                    "error": compile_data["stderr"],
                    "success": False
                }

            output = run_data.get("output", "").strip()
            stderr = run_data.get("stderr", "").strip()

            if run_data.get("code", 0) != 0 and stderr:
                return {"output": output, "error": stderr, "success": False}

            return {"output": output, "error": "", "success": True}

        except httpx.TimeoutException:
            return {"output": "", "error": "Code execution timed out (10s limit)", "success": False}
        except Exception as e:
            return {"output": "", "error": str(e), "success": False}

    def _get_extension(self, language: str) -> str:
        ext_map = {
            "dart": "dart", "python": "py", "c++": "cpp", "c": "c",
            "java": "java", "javascript": "js", "typescript": "ts",
            "go": "go", "rust": "rs", "ruby": "rb", "php": "php",
            "kotlin": "kt", "swift": "swift", "r": "r", "bash": "sh",
        }
        return ext_map.get(language, "txt")
