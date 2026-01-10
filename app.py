from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from src.prompt import system_prompt

app = Flask(__name__)
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

llm = ChatOllama(
    model="gemma:2b",           
    temperature=0.4,
    base_url="http://localhost:11434"
)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medicalbot"
index = pc.Index(index_name)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{question}")
    ]
)

def retrieve_context(inputs: dict):
    docs = retriever.invoke(inputs["question"])
    return {
        "context": docs,
        "question": inputs["question"]
    }


def question_answer_chain(inputs: dict):
    docs_text = "\n\n".join(
        doc.page_content for doc in inputs["context"]
    )

    formatted_prompt = prompt.format(
        context=docs_text,
        question=inputs["question"]
    )

    response = llm.invoke(formatted_prompt)

    return {
        "answer": response.content
    }


rag_chain = (
    RunnableLambda(retrieve_context)
    | RunnableLambda(question_answer_chain)
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    print(f"User: {msg}")

    result = rag_chain.invoke({"question": msg})
    answer = result["answer"]

    print(f"Bot: {answer}")
    return str(answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
