from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
import models, database
import json
import os

router = APIRouter(
    prefix="/api/tool",
    tags=["Asset Management"]
)

# --- Pydantic Models ---
class ToolCreate(BaseModel):
    id: str
    name: str
    description: str
    owner: str = "Werkzeugbau Berger"

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class AssetMetadata(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    status: str
    assets: Dict
    approvals: List[Dict]
    audit_log: List[Dict]

    class Config:
        orm_mode = True

# --- Endpoints ---

@router.get("s", response_model=List[Dict]) # /api/tools (plural) - Note: Router prefix is /api/tool, so this needs adjustment or a separate router
def get_all_tools(db: Session = Depends(database.get_db)):
    tools = db.query(models.Tool).all()
    return [{"id": t.id, "name": t.name} for t in tools]

@router.post("", response_model=AssetMetadata) # /api/tool
def create_tool(tool: ToolCreate, db: Session = Depends(database.get_db)):
    db_tool = db.query(models.Tool).filter(models.Tool.id == tool.id).first()
    if db_tool:
        raise HTTPException(status_code=400, detail="Tool ID already exists")
    
    new_tool = models.Tool(
        id=tool.id,
        name=tool.name,
        description=tool.description,
        owner=tool.owner,
        assets={"bom": None, "timeline": None, "steel_cert": None, "documents": []}
    )
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    # Return empty lists for relationships to match response model
    return {
        "id": new_tool.id,
        "name": new_tool.name,
        "description": new_tool.description,
        "owner": new_tool.owner,
        "status": new_tool.status,
        "assets": new_tool.assets,
        "approvals": [],
        "audit_log": []
    }

@router.get("/{tool_id}", response_model=AssetMetadata)
def get_tool_metadata(tool_id: str, db: Session = Depends(database.get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Convert SQLAlchemy objects to dicts for the response
    approvals = [{"filename": a.filename, "timestamp": a.timestamp.isoformat(), "status": a.status} for a in tool.approvals]
    audit_logs = [{"action": a.action, "consumer": a.consumer, "timestamp": a.timestamp.isoformat(), "status": a.status} for a in tool.audit_logs]
    
    return {
        "id": tool.id,
        "name": tool.name,
        "description": tool.description,
        "owner": tool.owner,
        "status": tool.status,
        "assets": tool.assets,
        "approvals": approvals,
        "audit_log": audit_logs,
        "active_policy": tool.active_policy
    }

@router.put("/{tool_id}")
def update_tool(tool_id: str, tool_update: ToolUpdate, db: Session = Depends(database.get_db)):
    tool = db.query(models.Tool).filter(models.Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    if tool_update.name:
        tool.name = tool_update.name
    if tool_update.description:
        tool.description = tool_update.description
    if tool_update.status:
        tool.status = tool_update.status
    
    db.commit()
    db.refresh(tool)
    return tool
