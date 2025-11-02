from flask import Flask, render_template, request
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
import google.generativeai as genai
import os


from src.helper import download_hugging_face_embeddings
from src.prompt import system_prompt


app = Flask(__name__)


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY


genai.configure(api_key=GEMINI_API_KEY)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.4,
    max_output_tokens=500
)


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medibot"
index = pc.Index(index_name)

vectorstore = PineconeVectorStore(index=index, embedding=embeddings)



retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{question}")
])


def retrieve_context(inputs):
    docs = retriever.get_relevant_documents(inputs["question"])
    return {"context": docs, "question": inputs["question"]}


def question_answer_chain(inputs):
    docs_text = "\n\n".join([doc.page_content for doc in inputs["context"]])
    formatted_prompt = prompt.format(context=docs_text, question=inputs["question"])
    response = llm.invoke(formatted_prompt)
    return {"answer": response.content}


rag_chain = RunnableLambda(retrieve_context) | RunnableLambda(question_answer_chain)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    print(f"User: {msg}")
    response = rag_chain.invoke({"question": msg})
    print("Response:", response["answer"])
    return str(response["answer"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
