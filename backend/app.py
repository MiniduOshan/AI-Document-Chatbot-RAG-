from flask import Flask, request, jsonify
from rag import load_and_index, ask_question

app = Flask(__name__)

db = None

@app.route("/upload", methods=["POST"])
def upload():
    global db
    file = request.files["file"]
    path = f"data/{file.filename}"
    file.save(path)

    db = load_and_index(path)
    return jsonify({"message": "File processed!"})

@app.route("/ask", methods=["POST"])
def ask():
    global db
    query = request.json["question"]

    answer = ask_question(db, query)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)