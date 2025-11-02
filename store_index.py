from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings  
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY 


extracted_data = load_pdf_file(data="C:/Users/nisar/OneDrive/Documents/End-to-End-Medical-Chatbot/Data/")
text_chunks = text_split(extracted_data)


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medibot"


if index_name not in [index.name for index in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )


vectorstore = PineconeVectorStore.from_documents(
    documents=text_chunks,
    embedding=embeddings,
    index_name=index_name
)

print("Pinecone index created and documents stored successfully!")
