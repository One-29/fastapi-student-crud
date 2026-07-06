from typing import Optional
from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)