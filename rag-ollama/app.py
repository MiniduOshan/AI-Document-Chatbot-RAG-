from pathlib import Path
from threading import Thread

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from rag import ask_question, get_index_status, set_pdf_source, warm_up_vector_store

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_index_in_background():
    try:
        warm_up_vector_store()
    except Exception:
        # Error details are available through get_index_status().
        pass


@app.route("/")
def home():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return send_from_directory(FRONTEND_DIR, "index.html")
    return "RAG API is running..."


@app.route("/<path:path>")
def serve_frontend_assets(path):
    requested = FRONTEND_DIR / path
    if requested.exists() and requested.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return jsonify({"error": "Not found"}), 404


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    query = (data.get("question") or "").strip()

    if not query:
        return jsonify({"error": "No question provided"}), 400

    try:
        answer = ask_question(query)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "question": query,
        "answer": answer
    })


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported"}), 400

    filename = secure_filename(file.filename)
    saved_path = UPLOAD_DIR / filename
    file.save(saved_path)

    try:
        set_pdf_source(saved_path)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    Thread(target=build_index_in_background, daemon=True).start()

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename,
        "indexing": True
    })


@app.route("/status", methods=["GET"])
def status():
    return jsonify(get_index_status())


if __name__ == "__main__":
    app.run(debug=True)