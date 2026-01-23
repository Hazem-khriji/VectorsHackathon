from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
load_dotenv()
# model = ChatGoogleGenerativeAI(
#     model = "gemini-2.5-flash",
#     temperature= 0.7,
#     api_key= os.getenv("GEMINI_API_KEY")
# )

ollama_model = ChatOllama(
    model = "llama3.2:latest"
)

model = ChatGroq(
    model_name="openai/gpt-oss-20b",
    groq_api_key=os.getenv("GROQ_API_KEY")
)
