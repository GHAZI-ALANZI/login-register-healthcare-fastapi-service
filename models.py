from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum
from database import Base
import enum

class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Doctor = "Doctor"
    Employee = "Employee"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.Employee, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow)  # Track last login time
    is_online = Column(Boolean, default=False)  # Track online status
