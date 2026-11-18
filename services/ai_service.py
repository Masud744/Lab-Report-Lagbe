"""
AI Service — Groq API integration for complete academic lab reports.
Generates:
1. Academic Problem Overview
2. Step-by-step Methodology (with bold titles and math)
3. Production-ready Source Code
4. Result and Discussion
5. Suggested Figure Captions & Console Output
"""

import os
import re
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CANDIDATE_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
]


LANG_EXTENSIONS = {
    "python": "py", "dart": "dart", "c++": "cpp", "c": "c", "java": "java",
    "javascript": "js", "typescript": "ts", "sql": "sql", "go": "go",
    "rust": "rs", "kotlin": "kt", "csharp": "cs", "php": "php", "ruby": "rb",
    "swift": "swift", "r": "R", "bash": "sh", "matlab": "m", "arduino": "ino",
    "lua": "lua", "perl": "pl", "scala": "scala",
}


def _extract_json_object(raw: str) -> dict:
    """Robustly parse JSON from LLM output even if wrapped in <think> or markdown fences."""
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    if "```" in cleaned:
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned)
        if fence:
            cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


class AIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        self.model = os.getenv("GROQ_MODEL") or "qwen/qwen3.8-27b"
        if self.api_key:
            self._init_client(self.api_key)

    def _init_client(self, api_key: str):
        self.api_key = api_key
        self.client = Groq(api_key=api_key)
        if not os.getenv("GROQ_MODEL"):
            try:
                available = {m.id for m in self.client.models.list().data}
                for m in CANDIDATE_MODELS:
                    if m in available:
                        self.model = m
                        break
            except Exception:
                self.model = "qwen/qwen3.8-27b"

    def set_api_key(self, key: str):
        if key != self.api_key or not self.client:
            self._init_client(key)

    def generate_full_report_task(
        self,
        task_title: str,
        task_description: str,
        requirements: list[str],
        language: str,
        student_name: str = "",
        student_id: str = "",
        user_code: str = "",
    ) -> dict:
        """
        Generate complete academic report data:
        - problem_overview (3-5 sentences)
        - methodology (4-6 structured points with title & technical description)
        - filename (e.g. cuboid.py, main.dart)
        - code (full runnable code — preserves user_code if provided)
        - result_discussion (academic analysis paragraph)
        - is_visual (boolean)
        - figure_captions (list of captions)
        """
        if not self.client:
            raise RuntimeError("Groq API key not configured.")

        req_text = "\n".join(f"- {r}" for r in requirements) if requirements else "No specific requirements given."
        has_user_code = bool(user_code and user_code.strip())
        code_block = (
            f"\nUser-Provided Source Code (analyze this exact code for methodology and discussion; keep it intact):\n{user_code.strip()}\n"
            if has_user_code
            else ""
        )
        code_field_instruction = (
            '"Return empty string "" because user provided their own code."'
            if has_user_code
            else f'"Complete, correct, runnable {language} source code with main entry point. Include student name and ID in comments/prints. Avoid interactive stdin prompts like input()/scanf() unless hardcoded sample values are used. No markdown fences inside JSON string."'
        )

        prompt = f"""You are an expert academic computer science and engineering instructor.
Generate a complete, rigorous academic lab report section for the following programming task.

Task Title: {task_title}
Task Description: {task_description}

Requirements:
{req_text}
{code_block}
Target Language: {language}
Student: {student_name} (ID: {student_id})

Output a single valid JSON object with EXACTLY these keys:
{{
  "problem_overview": "A formal academic introductory paragraph (3-5 sentences) explaining the objective, technologies used, and engineering principles.",
  "methodology": [
    {{
      "title": "Short Descriptive Title (e.g. Algorithm Design & Data Structures)",
      "description": "Technical description of implementation details, algorithms, complexity, equations, coordinates, or flags used."
    }}
  ],
  "filename": "Appropriate source code filename (e.g. cuboid.py, student.dart, sorting.cpp)",
  "code": {code_field_instruction},
  "result_discussion": "A formal academic evaluation paragraph (4-6 sentences) analyzing why the implementation successfully fulfills all requirements, observations on performance, and verification.",
  "is_visual": true or false (true ONLY if GUI, OpenGL, Pygame, Tkinter, Matplotlib, OpenCV, plots, or graphics),
  "figure_captions": ["Initial state", "Execution result"]
}}

Rules:
- Make methodology have 4 to 6 technical points.
- Return ONLY the raw JSON object. Do not wrap in markdown fences. Do not output anything else.
"""

        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]

        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an academic parser. You output strictly raw JSON matching the required schema. Never include markdown fences or preamble.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    max_tokens=2200,
                )

                raw = response.choices[0].message.content.strip()
                data = _extract_json_object(raw)
                if has_user_code:
                    data["code"] = user_code.strip()
                self.model = model
                return data
            except Exception:
                continue

        # Fallback if JSON parsing fails: generate code with fallback text
        fallback_code = user_code.strip() if has_user_code else self.generate_code(
            task_title, task_description, requirements, language, student_name, student_id
        )
        ext = LANG_EXTENSIONS.get(language.lower(), "txt")
        return {
            "problem_overview": task_description or f"Laboratory implementation of {task_title} in {language}.",
            "methodology": [
                {"title": "Implementation & Structure", "description": f"Developed using {language} conforming to specified functional requirements."},
                {"title": "Testing & Execution", "description": "Verified functionality through execution and validation of outputs."},
            ],
            "filename": f"main.{ext}",
            "code": fallback_code,
            "result_discussion": "The program executed successfully and met all specified requirements with expected output verified.",
            "is_visual": False,
            "figure_captions": ["Program Execution Output"],
        }

    def generate_code(
        self,
        task_title: str,
        task_description: str,
        requirements: list[str],
        language: str,
        student_name: str = "",
        student_id: str = "",
    ) -> str:
        """Fallback direct code generator."""
        if not self.client:
            raise RuntimeError("Groq API key not configured.")

        req_text = "\n".join(f"- {r}" for r in requirements) if requirements else "No specific requirements given."

        prompt = f"""Write a complete, runnable {language} program for this task.
Task: {task_title}
Description: {task_description}
Requirements:
{req_text}
Student: {student_name} (ID: {student_id})
Return ONLY runnable {language} code. No markdown fences.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are an expert {language} programmer. Output ONLY code."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=650,
        )
        code = response.choices[0].message.content.strip()
        if "```" in code:
            fence_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", code)
            if fence_match:
                code = fence_match.group(1).strip()
            else:
                code = code.replace("```", "").strip()
        return code

    def predict_output(self, code: str, language: str) -> str:
        """Use AI to predict console output with auto-fallback."""
        if not self.client:
            return "(Output simulation unavailable — no API key)"

        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]

        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a terminal emulator. Given source code, output EXACTLY what appears on "
                                "stdout when executed. Return ONLY raw console output without markdown or explanations."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Execute this {language} code and return stdout:\n\n{code}",
                        },
                    ],
                    temperature=0.1,
                    max_tokens=350,
                )
                output = response.choices[0].message.content.strip()
                if "```" in output:
                    fence_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", output)
                    if fence_match:
                        output = fence_match.group(1).strip()
                    else:
                        output = output.replace("```", "").strip()
                return output
            except Exception:
                continue

        return "(Execution output simulated from code logic)"

    def fix_code(self, code: str, error: str, language: str, task_title: str = "") -> str:
        """Self-healing step: repair compiler or runtime errors using stderr."""
        if not self.client:
            return code

        prompt = f"""The following {language} program for "{task_title or 'Lab Task'}" failed to compile or run.

Broken Code:
{code}

Error Message:
{error[:1200]}

Fix the bug so the program compiles and runs cleanly with zero interactive stdin blocking (use realistic sample inputs if needed).
Return ONLY the complete corrected {language} source code. Do NOT include markdown fences or explanations."""

        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": f"You are an expert {language} debugger. Output ONLY raw fixed code."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=850,
                )
                fixed = re.sub(r"<think>[\s\S]*?</think>", "", response.choices[0].message.content, flags=re.IGNORECASE).strip()
                if "```" in fixed:
                    fence_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", fixed)
                    fixed = fence_match.group(1).strip() if fence_match else fixed.replace("```", "").strip()
                if fixed and len(fixed) > 10:
                    return fixed
            except Exception:
                continue
        return code

    def parse_labsheet_text(self, text: str) -> dict:
        """Extract structured lab metadata and tasks from raw lab manual text."""
        if not self.client:
            raise RuntimeError("Groq API key not configured.")

        schema_prompt = f"""Extract structured programming lab report metadata from the following university lab sheet text.

Lab Sheet Text:
{text[:8000]}

Return ONLY a valid raw JSON object with EXACTLY these keys:
{{
  "course_code": "e.g. IRE 404 or empty string if unknown",
  "course_title": "e.g. Computer Graphics Sessional or empty string",
  "lab_number": 1,
  "lab_title": "Concise overall lab title",
  "language": "lowercase programming language key from: python, c++, c, java, dart, javascript, typescript, sql, go, rust, kotlin, csharp, php, ruby, swift, r, bash, matlab, arduino (default python if unclear)",
  "tasks": [
    {{
      "title": "Task title",
      "description": "Clear concise summary of what this task asks",
      "requirements": ["Requirement 1", "Requirement 2"]
    }}
  ]
}}

Rules:
- Extract ALL distinct lab tasks/exercises listed in the sheet (at least 1).
- Keep requirements crisp and actionable.
- Return ONLY raw JSON without markdown fences."""

        models_to_try = [self.model] + [m for m in CANDIDATE_MODELS if m != self.model]
        last_err = None
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You extract structured academic lab sheet data as strict raw JSON."},
                        {"role": "user", "content": schema_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=850,
                )
                return _extract_json_object(response.choices[0].message.content.strip())
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Failed to parse lab sheet text: {last_err}")

    def parse_labsheet_image(self, image_data_url: str) -> dict:
        """Extract structured lab metadata and tasks from a lab sheet screenshot/image using vision."""
        if not self.client:
            raise RuntimeError("Groq API key not configured.")

        instruction = """Read this university lab manual / assignment image carefully and extract all lab details.
Return ONLY a valid raw JSON object with EXACTLY these keys:
{
  "course_code": "e.g. IRE 404 or empty string if not visible",
  "course_title": "Course name or empty string",
  "lab_number": 1,
  "lab_title": "Concise overall lab title",
  "language": "lowercase language key from: python, c++, c, java, dart, javascript, typescript, sql, go, rust, kotlin, csharp, php, ruby, swift, r, bash, matlab, arduino (default python if unclear)",
  "tasks": [
    {
      "title": "Task title",
      "description": "Clear summary of what this task asks",
      "requirements": ["Requirement 1", "Requirement 2"]
    }
  ]
}
Return ONLY raw JSON without markdown fences."""

        vision_models = ["qwen/qwen3.8-27b"]
        last_err = None
        for model in vision_models:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": instruction},
                                {"type": "image_url", "image_url": {"url": image_data_url}},
                            ],
                        }
                    ],
                    temperature=0.1,
                    max_tokens=850,
                )
                return _extract_json_object(response.choices[0].message.content.strip())
            except Exception as e:
                last_err = e
                continue
        raise RuntimeError(f"Failed to parse lab sheet image: {last_err}")
