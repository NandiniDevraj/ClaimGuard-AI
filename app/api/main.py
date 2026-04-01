from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
from app.agents.orchestrator import AuthOrchestrator
from app.pipelines.document_parser import DocumentParser
from app.pipelines.vector_store import VectorStore
from app.database.db import db
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Healthcare Prior Authorization API",
    description="AI-powered prior authorization and coverage intelligence platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared components
vector_store = VectorStore()
parser = DocumentParser()
orchestrator = AuthOrchestrator(vector_store)

class AnalyzeRequest(BaseModel):
    procedure: str
    clinical_note: Optional[str] = None

class TextUploadRequest(BaseModel):
    text: str
    doc_type: str  # "policy" or "clinical"
    name: str

@app.get("/")
def root():
    return {
        "name": "Healthcare Prior Authorization API",
        "version": "1.0.0",
        "status": "running"
    }
@app.get("/")
def read_root():
    return {"status": "ClaimGuard AI Backend is Running"}
    
@app.get("/health")
def health():
    stats = vector_store.get_collection_stats()
    return {
        "status": "healthy",
        "vector_store": stats
    }

@app.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    doc_type: str = "policy"
):
    """Upload a PDF insurance policy or clinical note."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".pdf"
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Parse PDF
        parsed = parser.parse_pdf(tmp_path)
        parsed["file_name"] = file.filename

        # Store in vector store
        if doc_type == "policy":
            result = vector_store.add_policy_document(parsed)
        else:
            result = vector_store.add_clinical_note(parsed)

        # Cleanup temp file
        os.unlink(tmp_path)

        logger.info(
            f"Uploaded {doc_type} PDF: {file.filename}, "
            f"chunks: {result['stored']}"
        )

        return {
            "status": "success",
            "file_name": file.filename,
            "doc_type": doc_type,
            "chunks_stored": result["stored"],
            "pii_entities_found": len(
                parsed.get("pii_entities_found", [])
            )
        }

    except Exception as e:
        logger.error(f"PDF upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/text")
def upload_text(request: TextUploadRequest):
    """Upload text directly as policy or clinical note."""
    try:
        parsed = parser.parse_text(request.text, request.name)

        if request.doc_type == "policy":
            result = vector_store.add_policy_document(parsed)
        else:
            result = vector_store.add_clinical_note(parsed)

        return {
            "status": "success",
            "name": request.name,
            "doc_type": request.doc_type,
            "chunks_stored": result["stored"]
        }

    except Exception as e:
        logger.error(f"Text upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_authorization(request: AnalyzeRequest):
    """
    Run full multi-agent authorization analysis.
    This is the core endpoint.
    """
    try:
        # If clinical note provided, store it first
        if request.clinical_note:
            parsed = parser.parse_text(
                request.clinical_note,
                "submitted_clinical_note"
            )
            vector_store.add_clinical_note(parsed)

        # Run multi-agent analysis
        result = orchestrator.run(request.procedure)

        # Save to database
        if result["status"] == "success":
            record_id = db.save_authorization(result)
            result["record_id"] = record_id

        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history(limit: int = 10):
    """Get recent authorization analyses."""
    try:
        records = db.get_recent_records(limit)
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
def get_stats():
    """Get system statistics."""
    return {
        "vector_store": vector_store.get_collection_stats(),
        "api_version": "1.0.0"
    }