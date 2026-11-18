"""
Lab Report Lagbe! — AI-Powered Academic Programming Lab Report Workspace
Main FastAPI application.
"""

import os
import re
import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from services.ai_service import AIService, LANG_EXTENSIONS
from services.code_runner import CodeRunner, LANGUAGE_MAP
from services.latex_generator import LaTeXGenerator
from services.visual_runner import is_visual_task, generate_auto_visualizations
from services.storage import ReportStorage, OUTPUT_DIR

load_dotenv()

app = FastAPI(title="Lab Report Lagbe!", version="4.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ai_service = AIService()
code_runner = CodeRunner()
latex_gen = LaTeXGenerator()
storage = ReportStorage()


# ─── Request Models ───

class ImageInput(BaseModel):
    data: str
    caption: str = ""


class TaskInput(BaseModel):
    title: str
    description: str = ""
    requirements: list[str] = []
    custom_code: str = ""
    images: list[ImageInput] = []


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
    language: str = "python"
    github_link: str = ""
    custom_logo: str = ""
    tasks: list[TaskInput] = []
    groq_api_key: str = ""


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: str = ""
    groq_api_key: str = ""


# ─── API Endpoints ───

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "4.0.0"}


@app.get("/api/config")
async def get_config():
    has_key = bool(os.getenv("GROQ_API_KEY") or ai_service.api_key)
    return {
        "has_groq_api_key": has_key,
        "model": ai_service.model,
    }


@app.get("/api/languages")
async def get_languages():
    langs = [{"value": k, "label": v["label"]} for k, v in LANGUAGE_MAP.items()]
    return {"languages": langs}


@app.get("/api/dashboard")
async def get_dashboard():
    stats = storage.get_stats()
    reports = storage.list_reports()
    activity = storage.list_activity(limit=15)
    has_key = bool(os.getenv("GROQ_API_KEY") or ai_service.api_key)
    return {
        "stats": stats,
        "recent_reports": reports[:6],
        "activity": activity,
        "engine": {
            "has_groq_api_key": has_key,
            "model": ai_service.model,
        },
        "languages": [{"value": k, "label": v["label"]} for k, v in LANGUAGE_MAP.items()],
    }


@app.get("/api/reports")
async def list_reports():
    return {"reports": storage.list_reports()}


@app.get("/api/reports/{report_id}/file")
async def get_report_file(report_id: str, inline: bool = Query(default=False)):
    report = storage.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    fpath = os.path.join(OUTPUT_DIR, report["filename"])
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Compiled PDF file not found on disk.")
    disposition = "inline" if inline else "attachment"
    return FileResponse(
        path=fpath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'{disposition}; filename="{report["filename"]}"'},
    )


@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    ok = storage.delete_report(report_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"deleted": True, "id": report_id}


@app.get("/api/activity")
async def get_activity():
    return {"activity": storage.list_activity(limit=40)}


@app.post("/api/execute")
async def execute_code(req: ExecuteRequest):
    """Execute code in the Code Workspace via local runtime, Piston, Judge0, or AI fallback."""
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    res = await code_runner.execute(req.code, req.language, stdin=req.stdin)
    engine = res.get("engine", "local")
    output = res.get("output", "")
    error = res.get("error", "")
    success = res.get("success", False)

    # If runtime unavailable or GUI, fall back to Groq AI terminal prediction
    if not success and engine in ("unavailable", "skipped-gui", "piston"):
        api_key = req.groq_api_key or os.getenv("GROQ_API_KEY")
        if api_key:
            ai_service.set_api_key(api_key)
            output = ai_service.predict_output(req.code, req.language)
            error = ""
            success = True
            engine = "ai-simulated"

    storage.log_execution(req.language, engine, success)
    return {
        "output": output,
        "error": error,
        "success": success,
        "engine": engine,
        "execution_ms": res.get("execution_ms", 0),
    }


@app.post("/api/generate")
async def generate_report(req: GenerateRequest):
    """Generate a publication-grade academic programming lab report PDF."""
    api_key = req.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key is required. Configure it in Settings or server .env.",
        )

    ai_service.set_api_key(api_key)

    if not req.student_name or not req.student_id:
        raise HTTPException(status_code=400, detail="Student name and ID are required.")
    if not req.tasks:
        raise HTTPException(status_code=400, detail="At least one task is required.")

    processed_tasks = []
    lang_ext = LANG_EXTENSIONS.get(req.language.lower(), "txt")
    last_exec_engine = "ai-simulated"

    for i, task in enumerate(req.tasks):
        try:
            academic_data = ai_service.generate_full_report_task(
                task_title=task.title,
                task_description=task.description,
                requirements=task.requirements,
                language=req.language,
                student_name=req.student_name,
                student_id=req.student_id,
                user_code=task.custom_code,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Academic report generation failed for Task {i+1}: {str(e)}",
            )

        code = (task.custom_code.strip() if task.custom_code and task.custom_code.strip() else academic_data.get("code", ""))
        filename = academic_data.get("filename") or f"task_{i+1}.{lang_ext}"
        problem_overview = academic_data.get("problem_overview") or task.description
        methodology = academic_data.get("methodology", [])
        result_discussion = academic_data.get("result_discussion", "")
        is_visual = bool(academic_data.get("is_visual", False))
        suggested_captions = academic_data.get("figure_captions", [])

        # Execute code (local runtime -> Piston -> Judge0 -> AI prediction)
        output = ""
        try:
            exec_res = await code_runner.execute(code, req.language)
            if exec_res.get("success"):
                output = exec_res["output"]
                last_exec_engine = exec_res.get("engine", "local")
            else:
                output = ai_service.predict_output(code, req.language)
                last_exec_engine = "ai-simulated"
        except Exception:
            output = ai_service.predict_output(code, req.language)
            last_exec_engine = "ai-simulated"

        # Process user-uploaded screenshots / images
        images = []
        for idx, img in enumerate(task.images):
            caption = img.caption
            if not caption and idx < len(suggested_captions):
                caption = suggested_captions[idx]
            elif not caption:
                caption = f"Output state {idx + 1}"
            caption = re.sub(r"^figure\s*\d+\s*:\s*", "", caption, flags=re.IGNORECASE).strip()
            images.append({"data": img.data, "caption": caption})

        # Auto-visualization ONLY when task genuinely matches supported visual renderers
        if not images and is_visual_task(task.title, task.description, code):
            auto_imgs = generate_auto_visualizations(task.title, task.description, code)
            if auto_imgs:
                images = auto_imgs
                is_visual = True

        processed_tasks.append({
            "title": task.title,
            "problem_overview": problem_overview,
            "requirements": [r for r in task.requirements if r and r.strip()],
            "methodology": methodology,
            "filename": filename,
            "code": code,
            "output": output.strip() if output else "(No console output)",
            "images": images,
            "is_visual": is_visual and bool(images),
            "result_discussion": result_discussion,
        })

    report_data = {
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
        "language": req.language,
        "github_link": req.github_link,
        "custom_logo": req.custom_logo,
        "tasks": processed_tasks,
    }

    safe_id = re.sub(r"[^A-Za-z0-9_-]", "", req.student_id) or "student"
    short_uid = str(uuid.uuid4())[:6]
    pdf_filename = f"{safe_id}_Lab{req.lab_number}_{short_uid}_Report.pdf"

    try:
        pdf_path = latex_gen.compile_pdf(report_data, pdf_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")

    saved_meta = storage.add_report(
        title=req.lab_title or (req.tasks[0].title if req.tasks else f"Lab Report {req.lab_number:02d}"),
        course_code=req.course_code,
        course_title=req.course_title,
        lab_number=req.lab_number,
        language=req.language,
        filename=pdf_filename,
        student_name=req.student_name,
        student_id=req.student_id,
        task_count=len(processed_tasks),
        engine=last_exec_engine,
    )

    download_name = f"{safe_id}_Lab{req.lab_number}_Report.pdf"
    return FileResponse(
        path=pdf_path,
        filename=download_name,
        media_type="application/pdf",
        headers={
            "X-Report-Id": saved_meta["id"],
            "X-Execution-Engine": last_exec_engine,
            "Access-Control-Expose-Headers": "X-Report-Id, X-Execution-Engine",
        },
    )


# ─── Serve static frontend (must be LAST) ───
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
