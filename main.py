"""
ProU SkillNexus Backend
Stack: Python 3.9+, FastAPI, SQLite (Simulating Postgres), SQLAlchemy
"""
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import ast

# --- Database Setup ---
DATABASE_URL = "sqlite:///./prou.db" # This creates a REAL database file
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    skills = Column(String) 
    availability_status = Column(String, default="Available")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    required_skills = Column(String)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Pydantic Schemas ---
class ProjectCreate(BaseModel):
    title: str
    description: str
    required_skills: dict[str, int]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# --- CRITICAL: Enable React to talk to Python ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Your React App URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # Seed Data if Empty
    db = SessionLocal()
    if not db.query(Employee).first():
        seed_employees = [
            Employee(name="Sarah Chen", role="Senior Frontend Dev", skills='{"React": 9, "Design": 8, "SQL": 4, "Python": 3, "Data": 5}'),
            Employee(name="Marcus Johnson", role="Data Scientist", skills='{"Python": 9, "SQL": 8, "Data": 9, "React": 4, "Design": 2}'),
        ]
        db.add_all(seed_employees)
        db.commit()
    db.close()

# --- Endpoints ---

@app.post("/projects/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(
        title=project.title, 
        description=project.description,
        required_skills=str(project.required_skills)
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/projects/")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    # Convert string skills back to dict for JSON response
    results = []
    for p in projects:
        p_dict = p.__dict__
        if "required_skills" in p_dict and isinstance(p_dict["required_skills"], str):
             try:
                 p_dict["required_skills"] = ast.literal_eval(p_dict["required_skills"])
             except:
                 p_dict["required_skills"] = {}
        results.append(p)
    return results

@app.get("/projects/{project_id}/matches")
def get_project_matches(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project: raise HTTPException(status_code=404, detail="Project not found")
    
    req_skills = ast.literal_eval(project.required_skills)
    employees = db.query(Employee).all()
    
    matches = []
    for emp in employees:
        emp_skills = ast.literal_eval(emp.skills)
        # Algorithm
        total_weight = sum(req_skills.values())
        total_score = sum(min(emp_skills.get(k, 0), v) for k, v in req_skills.items())
        score = 0 if total_weight == 0 else round((total_score / total_weight) * 100, 1)
        
        matches.append({
            "employee_id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "match_score": score,
            "skills": emp_skills
        })
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)