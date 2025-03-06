import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from models import RoleEnum
import re
from fastapi import HTTPException
from datetime import datetime

def validate_password(password: str):
    """ check if password match secure requirements"""
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not re.search(r'[a-z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
    if not re.search(r'[A-Z]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    if not re.search(r'\d', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not re.search(r'[@$!%*?&]', password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character (@$!%*?&).")
    return password

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str
    department: str
    role: RoleEnum
   

    def __init__(self, **data):
        super().__init__(**data)
        self.password = validate_password(self.password)

    class Config:
        use_enum_values = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    department: str
    role: RoleEnum
    last_login: Optional[datetime]
    is_online: Optional[bool]

    # ✅ Allow Partial Updates
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    department: Optional[str] = None
    role: Optional[RoleEnum] = None
    last_login: Optional[datetime] = None  
    is_online: Optional[bool] = None 

    class Config:
        from_attributes = True
