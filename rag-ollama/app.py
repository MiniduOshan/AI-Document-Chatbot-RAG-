from flask import Flask, request, jsonify
from rag import ask_question

app = Flask(__name__)


@app.route("/")
def home():
    return "RAG API is running..."


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("question")

    if not query:
        return jsonify({"error": "No question provided"}), 400

    answer = ask_question(query)

    return jsonify({
        "question": query,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True)