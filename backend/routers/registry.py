from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(
    prefix="/api/registry",
    tags=["registry"]
)

# Pydantic models
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    organization_id: str

class User(UserBase):
    id: int
    organization_id: str
    class Config:
        orm_mode = True

class OrganizationBase(BaseModel):
    id: str
    name: str
    type: str
    domain: str

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    users: List[User] = []
    class Config:
        orm_mode = True

# Endpoints

@router.post("/organization", response_model=Organization)
def create_organization(org: OrganizationCreate, db: Session = Depends(get_db)):
    db_org = db.query(models.Organization).filter(models.Organization.id == org.id).first()
    if db_org:
        raise HTTPException(status_code=400, detail="Organization already exists")
    new_org = models.Organization(**org.dict())
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

@router.get("/organizations", response_model=List[Organization])
def get_organizations(db: Session = Depends(get_db)):
    return db.query(models.Organization).all()

@router.post("/user", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# Initialize default data
def initialize_registry_data(db: Session):
    # Check if data exists
    if db.query(models.Organization).first():
        return {"message": "Data already initialized"}
        
    # Create Organizations
    orgs = [
        models.Organization(id="did:web:werkzeugbau-berger.com", name="Werkzeugbau Berger", type="Supplier", domain="werkzeugbau-berger.com"),
        models.Organization(id="did:web:stripmeier.com", name="Stripmeier", type="Customer", domain="stripmeier.com"),
        models.Organization(id="did:web:steel-supply.com", name="Steel Supply Co", type="Supplier", domain="steel-supply.com"),
        models.Organization(id="did:web:auto-parts.com", name="Auto Parts Inc", type="Manufacturer", domain="auto-parts.com")
    ]
    db.add_all(orgs)
    db.commit()
    
    # Create Users
    users = [
        models.User(username="hans.berger", role="Admin", organization_id="did:web:werkzeugbau-berger.com"),
        models.User(username="petra.mueller", role="Operator", organization_id="did:web:werkzeugbau-berger.com"),
        models.User(username="klaus.stripmeier", role="Admin", organization_id="did:web:stripmeier.com"),
        models.User(username="julia.schmidt", role="Viewer", organization_id="did:web:stripmeier.com"),
        models.User(username="tom.steel", role="Sales", organization_id="did:web:steel-supply.com")
    ]
    db.add_all(users)
    db.commit()
    
    return {"message": "Default registry data initialized"}

@router.post("/init_defaults")
def init_defaults(db: Session = Depends(get_db)):
    return initialize_registry_data(db)
