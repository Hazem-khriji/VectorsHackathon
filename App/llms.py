from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
load_dotenv()
# model = ChatGoogleGenerativeAI(
#     model = "gemini-2.0-flash",
#     temperature= 0.7,
#     api_key= os.getenv("GEMINI_API_KEY")
# )
# Main Text Model (Groq)
model = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

# Vision Model (Groq) - Required for Image Search
vision_model = ChatGroq(
    model_name="llama-3.2-11b-vision",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

# Ollama (Local fallback)
ollama_model = ChatOllama(
    model = "llama3.2:latest"
)
