from fastapi import APIRouter, HTTPException
from ..rag.retriever import retrieve_documents
from ..pdf_processing.parser import parse_pdf
from ..pdf_processing.extractor import extract_text

router = APIRouter()

@router.post("/upload-pdf/")
async def upload_pdf(file: bytes):
    try:
        text = parse_pdf(file)
        return {"message": "PDF processed successfully", "text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/")
async def search(query: str):
    try:
        results = retrieve_documents(query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))