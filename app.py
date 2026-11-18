"""
Lab Report Lagbe? — AI-Powered Academic Programming Lab Report Workspace
Main FastAPI application.
"""

import io
import os
import re
import uuid
import base64
import tempfile
import subprocess
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from PIL import Image

from services.ai_service import AIService, LANG_EXTENSIONS
from services.code_runner import CodeRunner, LANGUAGE_MAP
from services.latex_generator import LaTeXGenerator
from services.visual_runner import is_visual_task, generate_auto_visualizations
from services.storage import ReportStorage, OUTPUT_DIR

load_dotenv()

app = FastAPI(title="Lab Report Lagbe?", version="4.5.0")

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


class MethodologyPoint(BaseModel):
    title: str
    description: str


class PreparedTask(BaseModel):
    title: str
    problem_overview: str = ""
    requirements: list[str] = []
    methodology: list[MethodologyPoint] = []
    filename: str = "main.py"
    code: str = ""
    output: str = ""
    images: list[ImageInput] = []
    is_visual: bool = False
    result_discussion: str = ""
    self_healed: bool = False
    exec_engine: str = "local"


class CompileRequest(BaseModel):
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
    tasks: list[PreparedTask] = []


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    stdin: str = ""
    groq_api_key: str = ""


# ─── Core Pipeline Helpers ───

async def _execute_with_self_healing(code: str, language: str, task_title: str, allow_heal: bool = True) -> dict:
    """
    Execute code locally/sandboxed; if compiler or runtime error occurs,
    automatically ask Groq AI to repair the code and re-run once.
    """
    exec_res = await code_runner.execute(code, language)
    if exec_res.get("success"):
        return {
            "code": code,
            "output": exec_res.get("output", ""),
            "images": exec_res.get("images", []),
            "engine": exec_res.get("engine", "local"),
            "self_healed": False,
        }

    engine = exec_res.get("engine", "")
    err_msg = exec_res.get("error", "")

    # Self-healing retry when an actual runtime/compiler returned an error
    if allow_heal and engine in ("local", "piston", "judge0") and err_msg:
        fixed_code = ai_service.fix_code(code, err_msg, language, task_title)
        if fixed_code and fixed_code.strip() != code.strip():
            retry_res = await code_runner.execute(fixed_code, language)
            if retry_res.get("success"):
                return {
                    "code": fixed_code,
                    "output": retry_res.get("output", ""),
                    "images": retry_res.get("images", []),
                    "engine": retry_res.get("engine", "local"),
                    "self_healed": True,
                }

    # Fallback to AI terminal prediction (e.g. GUI/OpenGL or unavailable runtime)
    predicted = ai_service.predict_output(code, language)
    return {
        "code": code,
        "output": predicted,
        "images": exec_res.get("images", []),
        "engine": "ai-simulated",
        "self_healed": False,
    }


async def _prepare_report_payload(req: GenerateRequest) -> dict:
    """Run AI generation, self-healing execution, plot capture, and auto-visualization."""
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

        has_custom = bool(task.custom_code and task.custom_code.strip())
        code = task.custom_code.strip() if has_custom else academic_data.get("code", "")
        filename = academic_data.get("filename") or f"task_{i+1}.{lang_ext}"
        problem_overview = academic_data.get("problem_overview") or task.description
        methodology = academic_data.get("methodology", [])
        result_discussion = academic_data.get("result_discussion", "")
        is_visual = bool(academic_data.get("is_visual", False))
        suggested_captions = academic_data.get("figure_captions", [])

        # Execute with self-healing (do not mutate user's explicit custom code)
        exec_info = await _execute_with_self_healing(
            code=code,
            language=req.language,
            task_title=task.title,
            allow_heal=not has_custom,
        )
        code = exec_info["code"]
        output = exec_info["output"]
        last_exec_engine = exec_info["engine"]
        captured_plots = exec_info.get("images", [])
        self_healed = exec_info.get("self_healed", False)

        # Process user-uploaded screenshots first
        images = []
        for idx, img in enumerate(task.images):
            caption = img.caption
            if not caption and idx < len(suggested_captions):
                caption = suggested_captions[idx]
            elif not caption:
                caption = f"Output state {idx + 1}"
            caption = re.sub(r"^figure\s*\d+\s*:\s*", "", caption, flags=re.IGNORECASE).strip()
            images.append({"data": img.data, "caption": caption})

        # Next: attach real headless Matplotlib plots captured during execution
        if not images and captured_plots:
            images = captured_plots
            is_visual = True

        # Next: targeted auto-visualization (3D OpenGL wireframe / 2D DDA & Circle)
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
            "self_healed": self_healed,
            "exec_engine": last_exec_engine,
        })

    return {
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
        "exec_engine": last_exec_engine,
    }


def _compile_and_persist(report_data: dict) -> FileResponse:
    """Compile prepared report dictionary to PDF + Overleaf zip and store metadata."""
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "", report_data.get("student_id", "")) or "student"
    lab_num = int(report_data.get("lab_number", 1) or 1)
    short_uid = str(uuid.uuid4())[:6]
    pdf_filename = f"{safe_id}_Lab{lab_num}_{short_uid}_Report.pdf"

    try:
        pdf_path = latex_gen.compile_pdf(report_data, pdf_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF compilation failed: {str(e)}")

    tasks = report_data.get("tasks", [])
    exec_engine = report_data.get("exec_engine") or (tasks[0].get("exec_engine", "local") if tasks else "local")
    saved_meta = storage.add_report(
        title=report_data.get("lab_title") or (tasks[0].get("title") if tasks else f"Lab Report {lab_num:02d}"),
        course_code=report_data.get("course_code", ""),
        course_title=report_data.get("course_title", ""),
        lab_number=lab_num,
        language=report_data.get("language", "python"),
        filename=pdf_filename,
        student_name=report_data.get("student_name", ""),
        student_id=report_data.get("student_id", ""),
        task_count=len(tasks),
        engine=exec_engine,
    )

    stem = os.path.splitext(pdf_filename)[0]
    has_zip = os.path.exists(os.path.join(OUTPUT_DIR, f"{stem}_latex.zip"))
    download_name = f"{safe_id}_Lab{lab_num}_Report.pdf"
    return FileResponse(
        path=pdf_path,
        filename=download_name,
        media_type="application/pdf",
        headers={
            "X-Report-Id": saved_meta["id"],
            "X-Execution-Engine": exec_engine,
            "X-Has-Latex-Zip": "true" if has_zip else "false",
            "Access-Control-Expose-Headers": "X-Report-Id, X-Execution-Engine, X-Has-Latex-Zip",
        },
    )


# ─── API Endpoints ───

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "4.5.0"}


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


@app.get("/api/reports/{report_id}/latex")
async def get_report_latex_zip(report_id: str):
    """Download Overleaf-ready LaTeX .zip bundle (main.tex + logo + figures)."""
    report = storage.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    stem = os.path.splitext(report["filename"])[0]
    zip_name = f"{stem}_latex.zip"
    zpath = os.path.join(OUTPUT_DIR, zip_name)
    if not os.path.exists(zpath):
        raise HTTPException(status_code=404, detail="LaTeX source bundle not available for this report.")
    return FileResponse(
        path=zpath,
        media_type="application/zip",
        filename=zip_name,
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


@app.post("/api/parse-labsheet")
async def parse_labsheet(
    file: UploadFile = File(...),
    groq_api_key: str = Form(default=""),
):
    """Parse an uploaded Lab Manual PDF, screenshot image, or text file to auto-fill the form."""
    api_key = groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required to parse lab sheets.")
    ai_service.set_api_key(api_key)

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 15 MB limit.")

    fname = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()

    try:
        if fname.endswith(".pdf") or "pdf" in ctype:
            with tempfile.TemporaryDirectory(prefix="lrg_parse_") as tmpdir:
                pdf_file = os.path.join(tmpdir, "sheet.pdf")
                with open(pdf_file, "wb") as f:
                    f.write(raw_bytes)

                proc = subprocess.run(
                    ["pdftotext", pdf_file, "-"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=15,
                )
                extracted_text = proc.stdout.decode("utf-8", errors="replace").strip()

                if len(extracted_text) >= 30:
                    parsed = ai_service.parse_labsheet_text(extracted_text)
                else:
                    # Scanned PDF fallback: render page 1 as PNG and parse via vision
                    img_prefix = os.path.join(tmpdir, "page")
                    subprocess.run(
                        ["pdftoppm", "-png", "-r", "140", "-f", "1", "-l", "1", pdf_file, img_prefix],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=20,
                        check=True,
                    )
                    rendered = [f for f in os.listdir(tmpdir) if f.startswith("page") and f.endswith(".png")]
                    if not rendered:
                        raise RuntimeError("Could not extract text or image from PDF.")
                    with Image.open(os.path.join(tmpdir, rendered[0])) as im:
                        im.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                        buf = io.BytesIO()
                        im.convert("RGB").save(buf, format="JPEG", quality=85)
                        data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
                    parsed = ai_service.parse_labsheet_image(data_url)

        elif ctype.startswith("image/") or fname.endswith((".png", ".jpg", ".jpeg", ".webp")):
            with Image.open(io.BytesIO(raw_bytes)) as im:
                im.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.convert("RGB").save(buf, format="JPEG", quality=88)
                data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
            parsed = ai_service.parse_labsheet_image(data_url)

        else:
            text = raw_bytes.decode("utf-8", errors="replace").strip()
            if not text:
                raise RuntimeError("No readable text found in file.")
            parsed = ai_service.parse_labsheet_text(text)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lab sheet parsing failed: {str(e)}")

    # Normalize language key cleanly
    lang = str(parsed.get("language", "python")).lower().strip()
    if lang not in LANGUAGE_MAP:
        lang = "c++" if lang in ("cpp", "cxx") else "javascript" if lang == "js" else "python"
    parsed["language"] = lang
    return parsed


@app.post("/api/execute")
async def execute_code(req: ExecuteRequest):
    """Execute code in Code Workspace (with headless Matplotlib plot capture)."""
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    res = await code_runner.execute(req.code, req.language, stdin=req.stdin)
    engine = res.get("engine", "local")
    output = res.get("output", "")
    error = res.get("error", "")
    success = res.get("success", False)
    images = res.get("images", [])

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
        "images": images,
    }


@app.post("/api/prepare")
async def prepare_report(req: GenerateRequest):
    """Stage 1 of Review & Edit workflow: generate sections, self-heal/run code, and capture figures."""
    return await _prepare_report_payload(req)


@app.post("/api/compile")
async def compile_prepared_report(req: CompileRequest):
    """Stage 2 of Review & Edit workflow: compile user-edited sections into PDF + Overleaf zip."""
    data = req.model_dump()
    return _compile_and_persist(data)


@app.post("/api/generate")
async def generate_report(req: GenerateRequest):
    """1-click end-to-end endpoint: prepare + self-heal + plot capture + compile PDF & LaTeX zip."""
    report_data = await _prepare_report_payload(req)
    return _compile_and_persist(report_data)


# ─── Serve static frontend (must be LAST) ───
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
