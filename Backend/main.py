import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from App.RAG_pipeline import Pipeline
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create a pipeline class
pipeline_rag = Pipeline()


@app.post("/api/search")
async def search_products(
        query: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None)
):
    """
    Endpoint to handle text query and/or image upload
    """
    try:
        image_path = None
        if image:
            image_path = UPLOAD_DIR/image.filename
            with image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        if not query and not image:
            raise HTTPException(status_code=400, detail="Please provide a query or image")

        search_query = query if query else ""

        result = pipeline_rag.pipeline(
            query=search_query,
            image_path=str(image_path) if image_path else None
        )

        if image_path and image_path.exists():
            image_path.unlink()

        return JSONResponse(content={
            "success": True,
            "data": result
        })
    except Exception as e:
        if image_path and image_path.exists():
            image_path.unlink()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    return {"message": "Product Search API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
