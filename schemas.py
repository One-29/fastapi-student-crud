from typing import Optional
from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    age: int

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int

    class Config:
        from_attributes = True