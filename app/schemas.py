from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class RegisterUserRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=20)
    last_name: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class RegisterEmployeeRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    department: str
    salary: int

class Response(RegisterEmployeeRequest):
    id: int
    # ConfigDict(from_attributes=True) allows Pydantic to convert SQLAlchemy ORM instances to JSON.
    model_config = ConfigDict(from_attributes=True)