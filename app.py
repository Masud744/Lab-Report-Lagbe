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
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from PIL import Image

from services.ai_service import AIService, LANG_EXTENSIONS
from services.code_runner import CodeRunner, LANGUAGE_MAP
from services.latex_generator import LaTeXGenerator
from services.visual_runner import is_visual_task, generate_auto_visualizations
from services.storage import ReportStorage, OUTPUT_DIR
from services.auth_guard import (
    require_verified_user,
    get_optional_user,
    exec_rate_limiter,
    ai_rate_limiter,
)

load_dotenv()

app = FastAPI(title="Lab Report Lagbe?", version="4.5.0")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ai_service = AIService()
code_runner = CodeRunner()
latex_gen = LaTeXGenerator()
storage = ReportStorage()


def _resolve_ai_service(custom_key: str) -> AIService:
    """Return server AIService or request-scoped instance so user keys never mutate global state."""
    key = (custom_key or "").strip()
    server_key = os.getenv("GROQ_API_KEY", "")
    if key and key != server_key:
        if len(key) > 256:
            raise HTTPException(status_code=400, detail="Invalid API key format.")
        return AIService(api_key=key)
    if not server_key and not ai_service.api_key:
        raise HTTPException(
            status_code=400,
            detail="Groq API key is required. Configure it in Settings or server .env.",
        )
    return ai_service


def _assert_report_owner(report: dict | None, user: dict) -> dict:
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    owner = report.get("owner_uid")
    if owner and owner != user["uid"]:
        raise HTTPException(status_code=403, detail="Access denied: report belongs to another account.")
    return report


def _safe_output_path(filename: str) -> str:
    safe_dir = os.path.realpath(OUTPUT_DIR)
    target = os.path.realpath(os.path.join(safe_dir, os.path.basename(filename)))
    if not target.startswith(safe_dir + os.sep):
        raise HTTPException(status_code=400, detail="Invalid file reference.")
    return target


# ─── Request Models ───

class ImageInput(BaseModel):
    data: str = Field(..., max_length=15_000_000)
    caption: str = Field(default="", max_length=300)


class TaskInput(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(default="", max_length=4000)
    requirements: list[str] = Field(default=[], max_length=25)
    custom_code: str = Field(default="", max_length=100_000)
    images: list[ImageInput] = Field(default=[], max_length=4)


class GenerateRequest(BaseModel):
    student_name: str = Field(..., max_length=120)
    student_id: str = Field(..., max_length=60)
    session: str = Field(default="2022-2023", max_length=60)
    university: str = Field(default="University of Frontier Technology, Bangladesh", max_length=180)
    university_short: str = Field(default="UFTB", max_length=40)
    department: str = Field(default="Department of Internet of Things and Robotics Engineering (IRE)", max_length=180)
    department_short: str = Field(default="IRE", max_length=40)
    faculty: str = Field(default="Faculty of Cyber Physical System Engineering", max_length=180)
    course_code: str = Field(default="", max_length=60)
    course_title: str = Field(default="", max_length=200)
    instructor_name: str = Field(default="", max_length=120)
    instructor_title: str = Field(default="Lecturer", max_length=100)
    lab_number: int = Field(default=1, ge=1, le=999)
    lab_title: str = Field(default="", max_length=200)
    language: str = Field(default="python", max_length=40)
    github_link: str = Field(default="", max_length=500)
    custom_logo: str = Field(default="", max_length=5_000_000)
    tasks: list[TaskInput] = Field(default=[], max_length=15)
    groq_api_key: str = Field(default="", max_length=256)


class MethodologyPoint(BaseModel):
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=2000)


class PreparedTask(BaseModel):
    title: str = Field(..., max_length=200)
    problem_overview: str = Field(default="", max_length=5000)
    requirements: list[str] = Field(default=[], max_length=25)
    methodology: list[MethodologyPoint] = Field(default=[], max_length=20)
    filename: str = Field(default="main.py", max_length=100)
    code: str = Field(default="", max_length=100_000)
    output: str = Field(default="", max_length=100_000)
    images: list[ImageInput] = Field(default=[], max_length=4)
    is_visual: bool = False
    result_discussion: str = Field(default="", max_length=5000)
    self_healed: bool = False
    exec_engine: str = Field(default="local", max_length=40)


class CompileRequest(BaseModel):
    student_name: str = Field(..., max_length=120)
    student_id: str = Field(..., max_length=60)
    session: str = Field(default="2022-2023", max_length=60)
    university: str = Field(default="University of Frontier Technology, Bangladesh", max_length=180)
    university_short: str = Field(default="UFTB", max_length=40)
    department: str = Field(default="Department of Internet of Things and Robotics Engineering (IRE)", max_length=180)
    department_short: str = Field(default="IRE", max_length=40)
    faculty: str = Field(default="Faculty of Cyber Physical System Engineering", max_length=180)
    course_code: str = Field(default="", max_length=60)
    course_title: str = Field(default="", max_length=200)
    instructor_name: str = Field(default="", max_length=120)
    instructor_title: str = Field(default="Lecturer", max_length=100)
    lab_number: int = Field(default=1, ge=1, le=999)
    lab_title: str = Field(default="", max_length=200)
    language: str = Field(default="python", max_length=40)
    github_link: str = Field(default="", max_length=500)
    custom_logo: str = Field(default="", max_length=5_000_000)
    tasks: list[PreparedTask] = Field(default=[], max_length=15)


class ExecuteRequest(BaseModel):
    code: str = Field(..., max_length=100_000)
    language: str = Field(default="python", max_length=40)
    stdin: str = Field(default="", max_length=20_000)
    groq_api_key: str = Field(default="", max_length=256)


# ─── Core Pipeline Helpers ───

async def _execute_with_self_healing(
    code: str,
    language: str,
    task_title: str,
    ai: AIService,
    allow_heal: bool = True,
) -> dict:
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
        fixed_code = ai.fix_code(code, err_msg, language, task_title)
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
    predicted = ai.predict_output(code, language)
    return {
        "code": code,
        "output": predicted,
        "images": exec_res.get("images", []),
        "engine": "ai-simulated",
        "self_healed": False,
    }


async def _prepare_report_payload(req: GenerateRequest) -> dict:
    """Run AI generation, self-healing execution, plot capture, and auto-visualization."""
    ai = _resolve_ai_service(req.groq_api_key)

    if not req.student_name or not req.student_id:
        raise HTTPException(status_code=400, detail="Student name and ID are required.")
    if not req.tasks:
        raise HTTPException(status_code=400, detail="At least one task is required.")

    processed_tasks = []
    lang_ext = LANG_EXTENSIONS.get(req.language.lower(), "txt")
    last_exec_engine = "ai-simulated"

    for i, task in enumerate(req.tasks):
        try:
            academic_data = ai.generate_full_report_task(
                task_title=task.title,
                task_description=task.description,
                requirements=task.requirements,
                language=req.language,
                student_name=req.student_name,
                student_id=req.student_id,
                user_code=task.custom_code,
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail=f"Academic report generation failed for Task {i+1}. Please retry.",
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
            ai=ai,
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


def _compile_and_persist(report_data: dict, owner_uid: str = "") -> FileResponse:
    """Compile prepared report dictionary to PDF + Overleaf zip and store metadata."""
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "", report_data.get("student_id", "")) or "student"
    lab_num = int(report_data.get("lab_number", 1) or 1)
    short_uid = str(uuid.uuid4())[:6]
    pdf_filename = f"{safe_id}_Lab{lab_num}_{short_uid}_Report.pdf"

    try:
        pdf_path = latex_gen.compile_pdf(report_data, pdf_filename)
    except Exception:
        raise HTTPException(status_code=500, detail="PDF compilation failed due to invalid formatting.")

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
        owner_uid=owner_uid,
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


@app.get("/api/firebase-config")
async def get_firebase_config():
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "lab-report-lagbe"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", ""),
    }


@app.get("/api/languages")
async def get_languages():
    langs = [{"value": k, "label": v["label"]} for k, v in LANGUAGE_MAP.items()]
    return {"languages": langs}


@app.get("/api/dashboard")
async def get_dashboard(user: dict | None = Depends(get_optional_user)):
    uid = user["uid"] if user else None
    stats = storage.get_stats(owner_uid=uid)
    reports = storage.list_reports(owner_uid=uid)
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
async def list_reports(user: dict | None = Depends(get_optional_user)):
    uid = user["uid"] if user else None
    return {"reports": storage.list_reports(owner_uid=uid)}


@app.get("/api/reports/{report_id}/file")
async def get_report_file(
    report_id: str,
    inline: bool = Query(default=False),
    user: dict = Depends(require_verified_user),
):
    report = _assert_report_owner(storage.get_report(report_id), user)
    fpath = _safe_output_path(report["filename"])
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="Compiled PDF file not found on disk.")
    disposition = "inline" if inline else "attachment"
    safe_dl = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(report["filename"]))
    return FileResponse(
        path=fpath,
        media_type="application/pdf",
        headers={"Content-Disposition": f'{disposition}; filename="{safe_dl}"'},
    )


@app.get("/api/reports/{report_id}/latex")
async def get_report_latex_zip(
    report_id: str,
    user: dict = Depends(require_verified_user),
):
    """Download Overleaf-ready LaTeX .zip bundle (main.tex + logo + figures)."""
    report = _assert_report_owner(storage.get_report(report_id), user)
    stem = os.path.splitext(os.path.basename(report["filename"]))[0]
    zip_name = f"{stem}_latex.zip"
    zpath = _safe_output_path(zip_name)
    if not os.path.exists(zpath):
        raise HTTPException(status_code=404, detail="LaTeX source bundle not available for this report.")
    safe_zip_name = re.sub(r"[^A-Za-z0-9._-]", "_", zip_name)
    return FileResponse(
        path=zpath,
        media_type="application/zip",
        filename=safe_zip_name,
    )


@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: str,
    user: dict = Depends(require_verified_user),
):
    _assert_report_owner(storage.get_report(report_id), user)
    ok = storage.delete_report(report_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"deleted": True, "id": report_id}


@app.get("/api/activity")
async def get_activity():
    return {"activity": storage.list_activity(limit=40)}


@app.post("/api/parse-labsheet")
async def parse_labsheet(
    request: Request,
    file: UploadFile = File(...),
    groq_api_key: str = Form(default=""),
):
    """Parse an uploaded Lab Manual PDF, screenshot image, or text file to auto-fill the form."""
    ai_rate_limiter.check(request)
    ai = _resolve_ai_service(groq_api_key)

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(raw_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 15 MB limit.")

    fname = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()

    if "svg" in ctype or fname.endswith(".svg"):
        raise HTTPException(status_code=400, detail="SVG files are not supported for security reasons.")

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
                    parsed = ai.parse_labsheet_text(extracted_text)
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
                    parsed = ai.parse_labsheet_image(data_url)

        elif ctype.startswith("image/") or fname.endswith((".png", ".jpg", ".jpeg", ".webp")):
            with Image.open(io.BytesIO(raw_bytes)) as im:
                if im.format not in ("PNG", "JPEG", "WEBP", "GIF"):
                    raise HTTPException(status_code=400, detail="Unsupported image format.")
                im.thumbnail((1400, 1400), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                im.convert("RGB").save(buf, format="JPEG", quality=88)
                data_url = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
            parsed = ai.parse_labsheet_image(data_url)

        else:
            text = raw_bytes.decode("utf-8", errors="replace").strip()
            if not text:
                raise RuntimeError("No readable text found in file.")
            parsed = ai.parse_labsheet_text(text)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Lab sheet parsing failed. Ensure file is valid PDF, image, or text.")

    # Normalize language key cleanly
    lang = str(parsed.get("language", "python")).lower().strip()
    if lang not in LANGUAGE_MAP:
        lang = "c++" if lang in ("cpp", "cxx") else "javascript" if lang == "js" else "python"
    parsed["language"] = lang
    return parsed


@app.post("/api/execute")
async def execute_code(request: Request, req: ExecuteRequest):
    """Execute code in Code Workspace (with headless Matplotlib plot capture)."""
    exec_rate_limiter.check(request)
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")

    res = await code_runner.execute(req.code, req.language, stdin=req.stdin)
    engine = res.get("engine", "local")
    output = res.get("output", "")
    error = res.get("error", "")
    success = res.get("success", False)
    images = res.get("images", [])

    if not success and engine in ("unavailable", "skipped-gui", "piston"):
        if req.groq_api_key or os.getenv("GROQ_API_KEY"):
            ai = _resolve_ai_service(req.groq_api_key)
            output = ai.predict_output(req.code, req.language)
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
async def prepare_report(request: Request, req: GenerateRequest):
    """Stage 1 of Review & Edit workflow: generate sections, self-heal/run code, and capture figures."""
    ai_rate_limiter.check(request)
    return await _prepare_report_payload(req)


@app.post("/api/compile")
async def compile_prepared_report(
    request: Request,
    req: CompileRequest,
    user: dict = Depends(require_verified_user),
):
    """Stage 2 of Review & Edit workflow: compile user-edited sections into PDF + Overleaf zip."""
    ai_rate_limiter.check(request)
    data = req.model_dump()
    return _compile_and_persist(data, owner_uid=user["uid"])


@app.post("/api/generate")
async def generate_report(
    request: Request,
    req: GenerateRequest,
    user: dict = Depends(require_verified_user),
):
    """1-click end-to-end endpoint: prepare + self-heal + plot capture + compile PDF & LaTeX zip."""
    ai_rate_limiter.check(request)
    report_data = await _prepare_report_payload(req)
    return _compile_and_persist(report_data, owner_uid=user["uid"])


# ─── Serve static frontend (must be LAST) ───
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
