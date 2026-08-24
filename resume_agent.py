import os
import json
import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# ------------------------------------------------------------------
# Configuration (all secrets come from environment, never the frontend)
# ------------------------------------------------------------------

API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")
HISTORY_FILE = os.path.join(BASE_DIR, "histroy.json")


# ------------------------------------------------------------------
# JSON helpers
# ------------------------------------------------------------------

def _read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data if data is not None else default
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------
# LLM call
# ------------------------------------------------------------------

def _call_llm(system_prompt, user_prompt):
    if not API_KEY or OpenAI is None:
        return None
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception:
        return None


def _extract_json(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Tolerate ```json fences returned by some models.
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


# ------------------------------------------------------------------
# Prompt
# ------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a professional multi-agent resume analysis system. "
    "You will receive a candidate's resume text and a job description. "
    "Analyze the resume against the job description and return ONLY a single "
    "valid JSON object (no markdown, no commentary) that exactly matches the "
    "schema below. All scores must be integers between 0 and 100. "
    "Use the candidate's real details; do not invent experience. "
    "If information is missing, use an empty array or empty string.\n\n"
    "SCHEMA:\n"
    "{\n"
    '  "extracted": {\n'
    '    "personal_details": {"name": "", "email": "", "phone": "", "location": ""},\n'
    '    "education": [{"degree": "", "institution": "", "year": ""}],\n'
    '    "skills": ["skill1", "skill2"],\n'
    '    "projects": [{"title": "", "description": ""}],\n'
    '    "certifications": ["cert1"],\n'
    '    "experience": [{"role": "", "company": "", "duration": ""}],\n'
    '    "summary": "concise candidate summary"\n'
    "  },\n"
    '  "ats": {\n'
    '    "ats_score": 0,\n'
    '    "keyword_match": 0,\n'
    '    "format_score": 0,\n'
    '    "experience_score": 0,\n'
    '    "ats_problems": ["problem1"]\n'
    "  },\n"
    '  "skills": {\n'
    '    "skills_match": 0,\n'
    '    "matched_skills": ["skill"],\n'
    '    "missing_skills": ["skill"],\n'
    '    "recommended_skills": ["skill"]\n'
    "  },\n"
    '  "strengths": {\n'
    '    "strengths": ["strength1"],\n'
    '    "weaknesses": ["weakness1"]\n'
    "  },\n"
    '  "critic": {\n'
    '    "critical_issues": ["issue1"],\n'
    '    "high_priority": ["item1"],\n'
    '    "quick_fixes": ["fix1"]\n'
    "  },\n"
    '  "final": {\n'
    '    "overall_score": 0,\n'
    '    "summary": "overall summary",\n'
    '    "final_verdict": "verdict text",\n'
    '    "top_3_actions": ["action1", "action2", "action3"]\n'
    "  }\n"
    "}"
)


def _build_user_prompt(resume_text, job_description, student_info):
    student_block = "\n".join(f"{k}: {v}" for k, v in student_info.items() if v)
    return (
        "CANDIDATE-SUPPLIED INFORMATION:\n"
        f"{student_block}\n\n"
        "JOB DESCRIPTION:\n"
        f"{job_description or 'Not provided'}\n\n"
        "RESUME TEXT:\n"
        f"{resume_text[:12000]}"
    )


# ------------------------------------------------------------------
# Safe assembly of the result
# ------------------------------------------------------------------

def _num(value, default=0):
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def _as_str(value):
    return str(value).strip() if value is not None else ""


def analyze_resume(resume_text, job_description, student_info):
    raw = _call_llm(SYSTEM_PROMPT, _build_user_prompt(resume_text, job_description, student_info))
    data = _extract_json(raw)

    extracted = data.get("extracted", {}) or {}
    ats = data.get("ats", {}) or {}
    skills = data.get("skills", {}) or {}
    strengths = data.get("strengths", {}) or {}
    critic = data.get("critic", {}) or {}
    final = data.get("final", {}) or {}

    if not API_KEY:
        final["summary"] = (
            "AI analysis could not run because no API key is configured. "
            "Set OPENROUTER_API_KEY (or OPENAI_API_KEY) in the environment. "
            "Scores below are placeholders."
        )

    result = {
        "student": student_info,
        "extracted": {
            "personal_details": extracted.get("personal_details", {}) or {},
            "education": _as_list_of_objects(extracted.get("education", [])),
            "skills": _as_list(extracted.get("skills", [])),
            "projects": _as_list_of_objects(extracted.get("projects", [])),
            "certifications": _as_list(extracted.get("certifications", [])),
            "experience": _as_list_of_objects(extracted.get("experience", [])),
            "summary": _as_str(extracted.get("summary", "")),
        },
        "ats": {
            "ats_score": _num(ats.get("ats_score")),
            "keyword_match": _num(ats.get("keyword_match")),
            "format_score": _num(ats.get("format_score")),
            "experience_score": _num(ats.get("experience_score")),
            "ats_problems": _as_list(ats.get("ats_problems", [])),
        },
        "skills": {
            "skills_match": _num(skills.get("skills_match")),
            "matched_skills": _as_list(skills.get("matched_skills", [])),
            "missing_skills": _as_list(skills.get("missing_skills", [])),
            "recommended_skills": _as_list(skills.get("recommended_skills", [])),
        },
        "strengths": {
            "strengths": _as_list(strengths.get("strengths", [])),
            "weaknesses": _as_list(strengths.get("weaknesses", [])),
        },
        "critic": {
            "critical_issues": _as_list(critic.get("critical_issues", [])),
            "high_priority": _as_list(critic.get("high_priority", [])),
            "quick_fixes": _as_list(critic.get("quick_fixes", [])),
        },
        "final": {
            "overall_score": _num(final.get("overall_score")),
            "summary": _as_str(final.get("summary", "")),
            "final_verdict": _as_str(final.get("final_verdict", "")),
            "top_3_actions": _as_list(final.get("top_3_actions", []))[:3],
        },
    }

    _persist(student_info, result)
    return result


def _as_list_of_objects(value):
    if not isinstance(value, list):
        return []
    cleaned = []
    for item in value:
        if isinstance(item, dict):
            cleaned.append(item)
        elif item is not None:
            cleaned.append({"title": _as_str(item)})
    return cleaned


# ------------------------------------------------------------------
# Persistence (used by /student and /history)
# ------------------------------------------------------------------

def _persist(student_info, result):
    email = (student_info.get("email") or "").strip().lower()
    if not email:
        return

    students = _read_json(STUDENTS_FILE, [])
    students = [s for s in students if str(s.get("email", "")).strip().lower() != email]
    record = dict(student_info)
    record["updated_at"] = _now()
    students.append(record)
    _write_json(STUDENTS_FILE, students)

    history = _read_json(HISTORY_FILE, [])
    history.append({
        "email": email,
        "name": student_info.get("name", ""),
        "overall_score": result["final"]["overall_score"],
        "ats_score": result["ats"]["ats_score"],
        "timestamp": _now(),
    })
    _write_json(HISTORY_FILE, history)


def get_student(email):
    if not email:
        return None
    email = email.strip().lower()
    students = _read_json(STUDENTS_FILE, [])
    for student in students:
        if str(student.get("email", "")).strip().lower() == email:
            return student
    return None


def get_history():
    return _read_json(HISTORY_FILE, [])
