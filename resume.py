import os
from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from werkzeug.utils import secure_filename

from pypdf import PdfReader
from docx import Document

from resume_agent import (
    analyze_resume,
    get_student,
    get_history
)


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# FILE VALIDATION
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/history")
def history():
    return jsonify(get_history())


@app.get("/student/<email>")
def student(email):
    record = get_student(email)
    if record is None:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(record)


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf(path):

    text = ""

    reader = PdfReader(path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ============================================================
# DOCX EXTRACTION
# ============================================================

def extract_docx(path):
    document = Document(path)
    return "\n".join(
        paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
    )


def extract_text(path, extension):
    if extension == "pdf":
        return extract_pdf(path)
    if extension == "docx":
        return extract_docx(path)
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


@app.post("/analyze")
def analyze():
    uploaded = request.files.get("resume")
    if uploaded is None or not uploaded.filename:
        return jsonify({"success": False, "error": "Please upload a resume file."}), 400
    if not allowed_file(uploaded.filename):
        return jsonify({"success": False, "error": "Only PDF, DOCX and TXT files are allowed."}), 400

    filename = secure_filename(uploaded.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    uploaded.save(path)
    extension = filename.rsplit(".", 1)[1].lower()

    try:
        resume_text = extract_text(path, extension)
        if not resume_text.strip():
            return jsonify({"success": False, "error": "The uploaded resume contains no readable text."}), 400

        student_info = {
            key: request.form.get(key, "").strip()
            for key in ("name", "email", "phone", "college", "branch", "year")
        }
        result = analyze_resume(
            resume_text,
            request.form.get("job_description", "").strip(),
            student_info,
        )
        return jsonify({"success": True, "result": result})
    except Exception as error:
        app.logger.exception("Resume analysis failed")
        return jsonify({"success": False, "error": str(error)}), 500
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))