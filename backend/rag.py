from langchain.llms import OpenAI

def ask_question(db, query):
    docs = db.similarity_search(query)

    context = "\n".join([doc.page_content for doc in docs])

    llm = OpenAI()
    answer = llm(f"Answer based on context:\n{context}\n\nQuestion: {query}")

    return answer