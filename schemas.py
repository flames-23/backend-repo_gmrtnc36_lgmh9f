"""
Database Schemas for MetaApply

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Student(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    citizenship: Optional[str] = Field(None, description="Country of citizenship")
    preferred_country: Optional[str] = Field(None, description="Preferred study destination")
    level: Optional[str] = Field(None, description="Target level e.g., bachelor, master, phd")
    interests: List[str] = Field(default_factory=list, description="Academic interests/tags")
    gpa: Optional[float] = Field(None, ge=0, le=4.0, description="GPA on 4.0 scale")
    test_scores: Optional[dict] = Field(default_factory=dict, description="Standardized test scores e.g., IELTS, TOEFL, GRE")

class University(BaseModel):
    name: str
    country: str
    city: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    ranking: Optional[int] = Field(None, ge=1)

class Program(BaseModel):
    university_id: str = Field(..., description="Reference to university _id")
    title: str
    level: str = Field(..., description="bachelor, master, phd")
    field: str = Field(..., description="Discipline/major e.g., Computer Science")
    duration_months: Optional[int] = Field(None, ge=1)
    tuition_usd: Optional[float] = Field(None, ge=0)
    intake_months: List[str] = Field(default_factory=list)
    country: Optional[str] = None
    city: Optional[str] = None
    min_gpa: Optional[float] = Field(None, ge=0, le=4.0)
    tags: List[str] = Field(default_factory=list, description="keywords for recommendation")
    requirements: Optional[dict] = Field(default_factory=dict)

class Recruiter(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    regions: List[str] = Field(default_factory=list, description="Regions they recruit from")
    verified: bool = Field(default=False)

class Application(BaseModel):
    student_id: str
    program_id: str
    status: str = Field(default="draft", description="draft, submitted, under_review, accepted, rejected, withdrawn")
    recruiter_id: Optional[str] = None
    notes: Optional[str] = None
