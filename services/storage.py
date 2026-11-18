"""
Lightweight JSON-backed persistence for reports, execution metrics, and activity history.
Auto-discovers real PDFs already present in output/ on first boot.
"""

import os
import json
import uuid
import threading
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORE_PATH = os.path.join(DATA_DIR, "store.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

_LOCK = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_store() -> dict:
    return {
        "reports": [],
        "activity": [],
        "code_executions": 0,
    }


def _load_store() -> dict:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STORE_PATH):
        store = _default_store()
        _seed_existing_pdfs(store)
        _save_store(store)
        return store
    try:
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _default_store()
        data.setdefault("reports", [])
        data.setdefault("activity", [])
        data.setdefault("code_executions", 0)
        return data
    except Exception:
        return _default_store()


def _save_store(data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_path = STORE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, STORE_PATH)


def _seed_existing_pdfs(store: dict) -> None:
    """Import non-test PDFs from output/ so existing reports appear on Dashboard."""
    if not os.path.isdir(OUTPUT_DIR):
        return
    candidates = []
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith(".pdf"):
            continue
        lower = fname.lower()
        if lower.startswith(("test_", "stress_", "verified_", "uftb_logo_", "final_tested")):
            continue
        full = os.path.join(OUTPUT_DIR, fname)
        mtime = os.path.getmtime(full)
        candidates.append((mtime, fname, full))

    candidates.sort(key=lambda x: x[0], reverse=True)
    for mtime, fname, full in candidates:
        dt = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
        is_lab4 = "lab4" in fname.lower()
        report_id = str(uuid.uuid4())[:8]
        store["reports"].append({
            "id": report_id,
            "title": "3D Wireframe Cuboid & Rotation" if is_lab4 else fname.replace(".pdf", "").replace("_", " "),
            "course_code": "IRE 404" if is_lab4 else "IRE 460",
            "course_title": "Computer Graphics and Animation Sessional" if is_lab4 else "Programming Sessional",
            "lab_number": 4 if is_lab4 else 1,
            "language": "python",
            "status": "completed",
            "filename": fname,
            "file_size": os.path.getsize(full),
            "student_name": "Shahriar Alom Masud",
            "student_id": "2201032",
            "task_count": 1,
            "created_at": dt,
            "updated_at": dt,
        })
    if store["reports"]:
        store["code_executions"] = len(store["reports"]) * 2
        store["activity"].append({
            "id": str(uuid.uuid4())[:8],
            "type": "system",
            "title": "Workspace initialized",
            "detail": f"Indexed {len(store['reports'])} existing lab report(s) from output/.",
            "timestamp": _now_iso(),
        })


class ReportStorage:
    def list_reports(self) -> list[dict]:
        with _LOCK:
            store = _load_store()
            valid = []
            changed = False
            for r in store["reports"]:
                fpath = os.path.join(OUTPUT_DIR, r.get("filename", ""))
                if r.get("filename") and os.path.exists(fpath):
                    r["file_size"] = os.path.getsize(fpath)
                    valid.append(r)
                else:
                    changed = True
            if changed:
                store["reports"] = valid
                _save_store(store)
            return sorted(valid, key=lambda x: x.get("updated_at", ""), reverse=True)

    def get_report(self, report_id: str) -> dict | None:
        with _LOCK:
            store = _load_store()
            for r in store["reports"]:
                if r.get("id") == report_id:
                    return r
            return None

    def add_report(
        self,
        title: str,
        course_code: str,
        course_title: str,
        lab_number: int,
        language: str,
        filename: str,
        student_name: str,
        student_id: str,
        task_count: int = 1,
        engine: str = "groq",
    ) -> dict:
        with _LOCK:
            store = _load_store()
            fpath = os.path.join(OUTPUT_DIR, filename)
            size = os.path.getsize(fpath) if os.path.exists(fpath) else 0
            now = _now_iso()
            report = {
                "id": str(uuid.uuid4())[:8],
                "title": title or f"Lab Report {lab_number:02d}",
                "course_code": course_code or "",
                "course_title": course_title or "Programming Sessional",
                "lab_number": lab_number,
                "language": language.lower(),
                "status": "completed",
                "filename": filename,
                "file_size": size,
                "student_name": student_name,
                "student_id": student_id,
                "task_count": task_count,
                "engine": engine,
                "created_at": now,
                "updated_at": now,
            }
            store["reports"].insert(0, report)
            store["code_executions"] = store.get("code_executions", 0) + max(1, task_count)
            store["activity"].insert(0, {
                "id": str(uuid.uuid4())[:8],
                "type": "report",
                "title": f"Generated {report['title']}",
                "detail": f"{language.upper()} • Lab {lab_number:02d} • {task_count} task(s)",
                "timestamp": now,
            })
            store["activity"] = store["activity"][:50]
            _save_store(store)
            return report

    def delete_report(self, report_id: str) -> bool:
        with _LOCK:
            store = _load_store()
            target = None
            remaining = []
            for r in store["reports"]:
                if r.get("id") == report_id:
                    target = r
                else:
                    remaining.append(r)
            if not target:
                return False
            store["reports"] = remaining
            fpath = os.path.join(OUTPUT_DIR, target.get("filename", ""))
            # Only remove file if no other report entry points to it
            still_referenced = any(r.get("filename") == target.get("filename") for r in remaining)
            if not still_referenced and os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass
            store["activity"].insert(0, {
                "id": str(uuid.uuid4())[:8],
                "type": "delete",
                "title": f"Deleted {target.get('title', 'report')}",
                "detail": target.get("filename", ""),
                "timestamp": _now_iso(),
            })
            store["activity"] = store["activity"][:50]
            _save_store(store)
            return True

    def log_execution(self, language: str, engine: str, success: bool) -> None:
        with _LOCK:
            store = _load_store()
            store["code_executions"] = store.get("code_executions", 0) + 1
            store["activity"].insert(0, {
                "id": str(uuid.uuid4())[:8],
                "type": "execute",
                "title": f"Ran {language.upper()} code in Workspace",
                "detail": f"Engine: {engine} • {'Succeeded' if success else 'Completed with errors'}",
                "timestamp": _now_iso(),
            })
            store["activity"] = store["activity"][:50]
            _save_store(store)

    def list_activity(self, limit: int = 30) -> list[dict]:
        with _LOCK:
            store = _load_store()
            return store.get("activity", [])[:limit]

    def get_stats(self) -> dict:
        reports = self.list_reports()
        with _LOCK:
            store = _load_store()
            executions = store.get("code_executions", 0)
        now = datetime.now(timezone.utc)
        month_prefix = now.strftime("%Y-%m")
        this_month = sum(1 for r in reports if r.get("created_at", "").startswith(month_prefix))
        report_dates = sorted({r.get("created_at", "")[:10] for r in reports if r.get("created_at")})
        return {
            "total_reports": len(reports),
            "completed_reports": sum(1 for r in reports if r.get("status") == "completed"),
            "code_executions": executions,
            "this_month_reports": this_month,
            "monthly_goal": 50,
            "report_dates": report_dates,
        }

