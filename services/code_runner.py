import httpx

# Judge0 CE on RapidAPI (free tier: 50 requests/day)
JUDGE0_API = "https://judge0-ce.p.rapidapi.com"

# Language IDs for Judge0 CE
LANGUAGE_MAP = {
    "python": {"id": 71, "label": "Python 3"},
    "dart": {"id": 90, "label": "Dart"},
    "c++": {"id": 54, "label": "C++ (GCC)"},
    "c": {"id": 50, "label": "C (GCC)"},
    "java": {"id": 62, "label": "Java"},
    "javascript": {"id": 63, "label": "JavaScript (Node)"},
    "typescript": {"id": 74, "label": "TypeScript"},
    "go": {"id": 60, "label": "Go"},
    "rust": {"id": 73, "label": "Rust"},
    "ruby": {"id": 72, "label": "Ruby"},
    "php": {"id": 68, "label": "PHP"},
    "kotlin": {"id": 78, "label": "Kotlin"},
    "swift": {"id": 83, "label": "Swift"},
    "r": {"id": 80, "label": "R"},
    "bash": {"id": 46, "label": "Bash"},
}


class CodeRunner:
    def __init__(self, rapidapi_key: str = None):
        self.rapidapi_key = rapidapi_key
        self.client = httpx.AsyncClient(timeout=30.0)

    def _get_headers(self, api_key: str = None):
        key = api_key or self.rapidapi_key
        if key:
            return {
                "X-RapidAPI-Key": key,
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
                "Content-Type": "application/json",
            }
        return {"Content-Type": "application/json"}

    async def execute(self, code: str, language: str, rapidapi_key: str = None) -> dict:
        """Execute code using Judge0 CE API. Returns {output, error, success}."""
        lang_key = language.lower().strip()
        lang_info = LANGUAGE_MAP.get(lang_key)

        if not lang_info:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "success": False
            }

        key = rapidapi_key or self.rapidapi_key
        if not key:
            # fallback: simulate output with AI
            return {
                "output": "",
                "error": "no_api_key",
                "success": False
            }

        payload = {
            "language_id": lang_info["id"],
            "source_code": code,
            "stdin": "",
            "cpu_time_limit": 10,
            "wall_time_limit": 15,
        }

        try:
            # submit (wait=true for synchronous)
            resp = await self.client.post(
                f"{JUDGE0_API}/submissions?base64_encoded=false&wait=true",
                json=payload,
                headers=self._get_headers(key),
            )

            if resp.status_code == 429:
                return {"output": "", "error": "rate_limit", "success": False}

            if resp.status_code != 200 and resp.status_code != 201:
                return {"output": "", "error": f"Judge0 API error: {resp.status_code} - {resp.text[:200]}", "success": False}

            data = resp.json()

            stdout = data.get("stdout") or ""
            stderr = data.get("stderr") or ""
            compile_output = data.get("compile_output") or ""
            status_id = data.get("status", {}).get("id", 0)

            # status 3 = Accepted (success)
            if status_id == 3:
                return {"output": stdout.strip(), "error": "", "success": True}

            # status 6 = Compilation Error
            if status_id == 6:
                return {"output": "", "error": compile_output.strip(), "success": False}

            # status 5 = Time Limit Exceeded
            if status_id == 5:
                return {"output": stdout.strip(), "error": "Time Limit Exceeded", "success": False}

            # status 11 = Runtime Error
            if status_id in (11, 12):
                return {"output": stdout.strip(), "error": stderr.strip() or "Runtime Error", "success": False}

            # other errors
            error_msg = stderr.strip() or compile_output.strip() or data.get("status", {}).get("description", "Unknown error")
            return {"output": stdout.strip(), "error": error_msg, "success": False}

        except httpx.TimeoutException:
            return {"output": "", "error": "Code execution timed out", "success": False}
        except Exception as e:
            return {"output": "", "error": str(e), "success": False}
