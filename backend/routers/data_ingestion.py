from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import models, database
from .pdf_parsing import extract_timeline_from_pdf
import os
import shutil
import datetime

router = APIRouter(
    tags=["Data Ingestion"]
)

DATA_DIR = os.getenv("DATA_DIR", "../data")
EXAMPLE_DATA_DIR = os.getenv("EXAMPLE_DATA_DIR", "../example_data")

class AttachFileRequest(BaseModel):
    filename: str
    category: str

@router.get("/api/repository/files")
def list_repository_files():
    """
    Lists all PDF files available in the example_data directory.
    """
    if not os.path.exists(EXAMPLE_DATA_DIR):
        return []
    
    files = [f for f in os.listdir(EXAMPLE_DATA_DIR) if f.lower().endswith('.pdf')]
    return files

@router.post("/api/tool/{tool_id}/attach_file")
def attach_file_to_tool(tool_id: str, request: AttachFileRequest, db: Session = Depends(database.get_db)):
    """
    Copies a file from the repository to the tool's asset list.
    """
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    source_path = os.path.join(EXAMPLE_DATA_DIR, request.filename)
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="File not found in repository")
    
    # Copy file to DATA_DIR to 'publish' it
    dest_filename = f"{tool_id}_{request.filename}"
    dest_path = os.path.join(DATA_DIR, dest_filename)
    shutil.copy2(source_path, dest_path)
    
    # Update JSON assets
    assets = dict(tool.assets) # Copy to mutate
    if "documents" not in assets or assets["documents"] is None:
        assets["documents"] = []
        
    # Check if already attached
    already_attached = False
    for doc in assets["documents"]:
        if doc["filename"] == dest_filename:
            already_attached = True
            break
    
    document_record = None
    if not already_attached:
        document_record = {
            "name": request.filename,
            "filename": dest_filename,
            "category": request.category,
            "attached_at": datetime.datetime.now().isoformat()
        }
        assets["documents"].append(document_record)
    else:
        document_record = next(d for d in assets["documents"] if d["filename"] == dest_filename)

    # --- AUTOMATOR: Parse Timeline if applicable ---
    timeline_updated = False
    if request.category == "Timeline" or "Ablaufplan" in request.filename:
        force_mock = (request.category == "Timeline")
        parsed_timeline = extract_timeline_from_pdf(dest_path, force_mock=force_mock)
        if parsed_timeline:
            assets["timeline"] = parsed_timeline
            timeline_updated = True

    tool.assets = assets # Re-assign to trigger update
    db.commit()

    response = {"message": "File attached successfully", "document": document_record}
    if timeline_updated:
        response["message"] = "File attached & Timeline updated automatically!"
        response["timeline_updated"] = True
        
    return response

@router.get("/api/files/{filename}")
def download_file(filename: str):
    """
    Serves a file from the DATA_DIR.
    """
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)

@router.post("/api/tool/{tool_id}/approve")
async def approve_tool(tool_id: str, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """
    Accepts a file upload (e.g., signed approval doc) and logs the approval.
    """
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Create approvals directory if it doesn't exist
    approvals_dir = os.path.join(DATA_DIR, "approvals")
    os.makedirs(approvals_dir, exist_ok=True)

    # Simulate saving the file
    # file_location = os.path.join(approvals_dir, f"approval_{tool_id}_{file.filename}")
    # with open(file_location, "wb+") as file_object:
    #     file_object.write(file.file.read())
    
    approval_record = models.Approval(
        tool_id=tool_id,
        filename=file.filename,
        timestamp=datetime.datetime.utcnow(),
        status="Received"
    )
    db.add(approval_record)
    db.commit()
    
    return {
        "message": "Approval document received and processed successfully.",
        "approval_record": {"filename": file.filename, "status": "Received"}
    }
