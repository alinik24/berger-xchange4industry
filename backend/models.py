from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Tool(Base):
    __tablename__ = "tools"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner = Column(String, default="Werkzeugbau Berger")
    status = Column(String, default="Active")
    
    # Storing complex objects as JSON for simplicity in this prototype
    # In a strict schema, these would be separate tables
    assets = Column(JSON, default={}) 
    active_policy = Column(JSON, nullable=True)
    
    approvals = relationship("Approval", back_populates="tool")
    audit_logs = relationship("AuditLog", back_populates="tool")

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(String, ForeignKey("tools.id"))
    filename = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Received")
    
    tool = relationship("Tool", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(String, ForeignKey("tools.id"))
    action = Column(String)
    consumer = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Allowed")
    
    tool = relationship("Tool", back_populates="audit_logs")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, index=True) # e.g., "did:web:werkzeugbau-berger.com"
    name = Column(String, unique=True, index=True)
    type = Column(String) # Supplier, Manufacturer, Customer
    domain = Column(String)
    
    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String) # Admin, Operator, Viewer
    organization_id = Column(String, ForeignKey("organizations.id"))
    
    organization = relationship("Organization", back_populates="users")
