import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Student, University, Program, Recruiter, Application

app = FastAPI(title="MetaApply API", description="Student-University-Recruiter management with AI-ready structures")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MetaApply backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Helpers
class IdModel(BaseModel):
    id: str

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# CRUD Endpoints (minimal for demo)
# Students
@app.post("/students")
def create_student(payload: Student):
    inserted_id = create_document("student", payload)
    return {"id": inserted_id}

@app.get("/students")
def list_students(level: Optional[str] = None, country: Optional[str] = None):
    filt = {}
    if level:
        filt["level"] = level
    if country:
        filt["preferred_country"] = country
    items = get_documents("student", filt, limit=100)
    for i in items:
        i["_id"] = str(i["_id"])  # stringify
    return items

# Universities
@app.post("/universities")
def create_university(payload: University):
    inserted_id = create_document("university", payload)
    return {"id": inserted_id}

@app.get("/universities")
def list_universities(country: Optional[str] = None):
    filt = {"country": country} if country else {}
    items = get_documents("university", filt, limit=100)
    for i in items:
        i["_id"] = str(i["_id"])  # stringify
    return items

# Programs
@app.post("/programs")
def create_program(payload: Program):
    inserted_id = create_document("program", payload)
    return {"id": inserted_id}

@app.get("/programs")
def list_programs(level: Optional[str] = None, field: Optional[str] = None, country: Optional[str] = None):
    filt = {}
    if level:
        filt["level"] = level
    if field:
        filt["field"] = field
    if country:
        filt["country"] = country
    items = get_documents("program", filt, limit=100)
    for i in items:
        i["_id"] = str(i["_id"])  # stringify
    return items

# Recruiters
@app.post("/recruiters")
def create_recruiter(payload: Recruiter):
    inserted_id = create_document("recruiter", payload)
    return {"id": inserted_id}

@app.get("/recruiters")
def list_recruiters(verified: Optional[bool] = None):
    filt = {"verified": verified} if verified is not None else {}
    items = get_documents("recruiter", filt, limit=100)
    for i in items:
        i["_id"] = str(i["_id"])  # stringify
    return items

# Applications
@app.post("/applications")
def create_application(payload: Application):
    inserted_id = create_document("application", payload)
    return {"id": inserted_id}

@app.get("/applications")
def list_applications(status: Optional[str] = None, student_id: Optional[str] = None, program_id: Optional[str] = None):
    filt = {}
    if status:
        filt["status"] = status
    if student_id:
        filt["student_id"] = student_id
    if program_id:
        filt["program_id"] = program_id
    items = get_documents("application", filt, limit=100)
    for i in items:
        i["_id"] = str(i["_id"])  # stringify
    return items

# Simple recommendation stub (rule-based placeholder for AI)
@app.get("/recommendations/{student_id}")
def recommend_programs(student_id: str, limit: int = 10):
    # Fetch student
    students = get_documents("student", {"_id": to_object_id(student_id)}, limit=1)
    if not students:
        raise HTTPException(status_code=404, detail="Student not found")
    student = students[0]

    filt = {}
    if student.get("level"):
        filt["level"] = student["level"]
    if student.get("preferred_country"):
        filt["country"] = student["preferred_country"]

    # Simple tag overlap scoring
    programs = get_documents("program", filt, limit=200)
    s_tags = set(student.get("interests", []))
    for p in programs:
        p["_id"] = str(p["_id"])  # stringify
        p_tags = set(p.get("tags", []))
        p["score"] = len(s_tags & p_tags)
        if student.get("gpa") is not None and p.get("min_gpa") is not None:
            p["score"] += 1 if student["gpa"] >= p["min_gpa"] else -1
    programs.sort(key=lambda x: x.get("score", 0), reverse=True)
    return programs[:limit]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
