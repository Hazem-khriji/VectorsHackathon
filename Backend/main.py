import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from App.RAG_pipeline import Pipeline

app = FastAPI()

# create a pipeline class
pipeline_rag = Pipeline()

@app.get("/api/search")
def search_startup(q: str):
    return {"result": pipeline_rag.pipeline(query=q)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
