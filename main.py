from fastapi import FastAPI, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, get_db
from models import User, RoleEnum
from schemas import UserCreate, UserLogin, UserResponse
from auth import hash_password, verify_password, create_access_token, decode_token
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

Base.metadata.create_all(bind=engine)

def create_default_admin():
    db = SessionLocal()
    admin_exists = db.query(User).filter(User.role == RoleEnum.Admin).first()
    if not admin_exists:
        default_admin = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("Admin@123"),  # encrypt password
            department="Administration",
            role=RoleEnum.Admin
        )
        db.add(default_admin)
        db.commit()
        print("✅ Default Admin Created: username=admin, password=Admin@123")
    db.close()

create_default_admin()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ** check from current user **
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ** just Admin can add new user **
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password, department=user.department, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ** login with tocken jwt **
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ** just Admin can add get all users **
@app.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Only admins can view users")
    return db.query(User).all()

# ** just Admin can add find user by email **
@app.get("/user/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Only admins can search for users")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ** just Admin can find user by username **
@app.get("/user/username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Only admins can search for users")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ** just Admin can update info of user **
@app.put("/user/update/{user_id}", response_model=UserResponse)
def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.Admin:
        raise HTTPException(status_code=403, detail="Only admins can update users")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updated_user.password != updated_user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user.username = updated_user.username
    user.email = updated_user.email
    user.password = hash_password(updated_user.password)
    user.department = updated_user.department
    user.role = updated_user.role

    db.commit()
    db.refresh(user)
    return user

# ** just Admin can delete user **
@app.delete("/user/delete/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    """Only Admin can delete users"""
    if current_user.role != RoleEnum.Admin:  #  Ensure only Admins can delete
        raise HTTPException(status_code=403, detail="Only admins can delete users")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

