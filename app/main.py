
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.core.rag_pipeline import DocumentQA
import os
import shutil

app = FastAPI()
qa_system = DocumentQA()

# Permitir acceso desde frontend (Streamlit, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    qa_system.load_and_index_pdf(file_path)
    return {"message": "Document loaded and processed", "file": file.filename}

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    if not qa_system.qa_chain:
        index_loaded = qa_system.load_existing_index()
        if not index_loaded:
            return {"error": "No index loaded. Please upload a document first."}

    answer = qa_system.ask(question)
    return {"question": question, "answer": answer}
