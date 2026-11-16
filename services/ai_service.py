import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class AIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"

    def set_api_key(self, key: str):
        self.api_key = key
        self.client = Groq(api_key=key)

    def generate_code(self, task_title: str, task_description: str,
                      requirements: list[str], language: str,
                      student_name: str = "", student_id: str = "") -> str:
        req_text = "\n".join(f"- {r}" for r in requirements) if requirements else "No specific requirements given."

        prompt = f"""Write a complete, runnable {language} program for this task.

Task: {task_title}
Description: {task_description}

Requirements:
{req_text}

Rules:
- Write ONLY the code, no explanations, no markdown fences
- The code must be complete and runnable as-is
- Use clean, straightforward style (no over-engineering)
- Keep comments minimal and natural (not robotic like "// Step 1: ...")
- Include a main function or entry point that demonstrates the code working
- Use realistic sample data (you can use "{student_name}" with ID "{student_id}" as one of the test entries if relevant)
- Print clear, readable output to the console
- The code should be 40-80 lines ideally, not too short, not bloated
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are an expert {language} programmer. You write clean, correct, compilable code. Return ONLY code, nothing else."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        code = response.choices[0].message.content.strip()
        # strip markdown fences if the model added them
        if code.startswith("```"):
            lines = code.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)

        return code
