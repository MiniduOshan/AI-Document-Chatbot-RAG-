from rag import create_db, ask_question

print("Loading document...")

db = create_db("sample.pdf")

print("Ready! Ask your questions.\n")

while True:
    question = input("You: ")

    if question.lower() == "exit":
        break

    answer = ask_question(db, question)
    print("\nAI:", answer, "\n")