from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import models, database
import datetime

router = APIRouter(
    prefix="/api/tool",
    tags=["Policy Engine"]
)

class Policy(BaseModel):
    type: str
    expiry_date: Optional[str] = None
    max_downloads: Optional[int] = None
    allowed_purpose: Optional[str] = None
    created_at: str

class LogAccessRequest(BaseModel):
    action: str
    consumer: str

@router.post("/{tool_id}/policy")
def set_tool_policy(tool_id: str, policy: Policy, db: Session = Depends(database.get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Update the JSON field
    tool.active_policy = policy.dict()
    db.commit()
    
    return {"message": "Policy updated successfully", "policy": policy}

@router.post("/{tool_id}/log_access")
def log_access(tool_id: str, request: LogAccessRequest, db: Session = Depends(database.get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    log_entry = models.AuditLog(
        tool_id=tool_id,
        action=request.action,
        consumer=request.consumer,
        timestamp=datetime.datetime.utcnow(),
        status="Allowed"
    )
    db.add(log_entry)
    db.commit()
    
    return {"message": "Access logged"}
