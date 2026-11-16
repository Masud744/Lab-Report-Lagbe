import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from services.ai_service import AIService
from services.code_runner import CodeRunner
from services.latex_generator import LaTeXGenerator

load_dotenv()

app = FastAPI(title="Lab Report Lagbe!", version="1.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ai_service = AIService()
code_runner = CodeRunner()
latex_gen = LaTeXGenerator()


class TaskInput(BaseModel):
    title: str
    description: str
    requirements: list[str] = []

class GenerateRequest(BaseModel):
    student_name: str
    student_id: str
    session: str = "2022-2023"
    university: str = "University of Frontier Technology, Bangladesh"
    university_short: str = "UFTB"
    department: str = "Department of Internet of Things and Robotics Engineering (IRE)"
    department_short: str = "IRE"
    faculty: str = "Faculty of Cyber Physical System Engineering"
    course_code: str = ""
    course_title: str = ""
    instructor_name: str = ""
    instructor_title: str = "Lecturer"
    lab_number: int = 1
    lab_title: str = ""
    lab_subtitle: str = ""
    language: str = "python"
    github_link: str = ""
    tasks: list[TaskInput] = []
    groq_api_key: str = ""
    rapidapi_key: str = ""


@app.get("/api/languages")
async def get_languages():
    from services.code_runner import LANGUAGE_MAP
    langs = [{"value": k, "label": v["label"]} for k, v in LANGUAGE_MAP.items()]
    return {"languages": langs}


def generate_expected_output(groq_client: AIService, code: str, language: str) -> str:
    """Use AI to predict what the code output would be."""
    try:
        response = groq_client.client.chat.completions.create(
            model=groq_client.model,
            messages=[
                {"role": "system", "content": "You are a code executor. Given source code, predict EXACTLY what the terminal/console output would be when this code runs. Return ONLY the raw output text, nothing else. No explanations, no markdown."},
                {"role": "user", "content": f"What would be the exact console output of this {language} code?\n\n{code}"}
            ],
            temperature=0.1,
            max_tokens=1000,
        )
        output = response.choices[0].message.content.strip()
        if output.startswith("```"):
            lines = output.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            output = "\n".join(lines)
        return output
    except Exception:
        return "(Output not available)"


@app.post("/api/generate")
async def generate_report(req: GenerateRequest):
    api_key = req.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required. Enter it in the form or set GROQ_API_KEY env variable.")

    ai_service.set_api_key(api_key)

    if not req.tasks:
        raise HTTPException(status_code=400, detail="At least one task is required.")
    if not req.student_name or not req.student_id:
        raise HTTPException(status_code=400, detail="Student name and ID are required.")

    rapidapi_key = req.rapidapi_key or os.getenv("RAPIDAPI_KEY", "")
    processed_tasks = []

    for i, task in enumerate(req.tasks):
        # generate code via AI
        try:
            code = ai_service.generate_code(
                task_title=task.title,
                task_description=task.description,
                requirements=task.requirements,
                language=req.language,
                student_name=req.student_name,
                student_id=req.student_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI code generation failed for Task {i+1}: {str(e)}")

        # try running code via Judge0
        output = ""
        if rapidapi_key:
            try:
                result = await code_runner.execute(code, req.language, rapidapi_key)
                if result["success"]:
                    output = result["output"]
                elif result["error"] == "rate_limit":
                    output = generate_expected_output(ai_service, code, req.language)
                elif result["error"] == "no_api_key":
                    output = generate_expected_output(ai_service, code, req.language)
                else:
                    output = f"{result['output']}\n[Error]: {result['error']}"
            except Exception:
                output = generate_expected_output(ai_service, code, req.language)
        else:
            # no RapidAPI key — use AI to predict output
            output = generate_expected_output(ai_service, code, req.language)

        processed_tasks.append({
            "title": task.title,
            "description": task.description,
            "requirements": task.requirements,
            "code": code,
            "output": output.strip() if output else "(No output)",
            "summary": "",
        })

    # build LaTeX data
    data = {
        "student_name": req.student_name,
        "student_id": req.student_id,
        "session": req.session,
        "university": req.university,
        "university_short": req.university_short,
        "department": req.department,
        "department_short": req.department_short,
        "faculty": req.faculty,
        "course_code": req.course_code,
        "course_title": req.course_title,
        "instructor_name": req.instructor_name,
        "instructor_title": req.instructor_title,
        "lab_number": req.lab_number,
        "lab_title": req.lab_title,
        "lab_subtitle": req.lab_subtitle,
        "language": req.language,
        "github_link": req.github_link,
        "tasks": processed_tasks,
    }

    try:
        tex_content = latex_gen.generate(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LaTeX generation failed: {str(e)}")

    filename = f"{req.student_id}_Report_{req.lab_number}.pdf"
    try:
        pdf_path = latex_gen.compile_pdf(tex_content, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")

    return FileResponse(
        path=pdf_path,
        filename=filename,
        media_type="application/pdf",
    )


# Serve static frontend (must be LAST)
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
