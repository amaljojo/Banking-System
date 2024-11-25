from fastapi import APIRouter, HTTPException, Depends
from config.auth import hash_password, create_access_token, verify_password
from models.user import User
from config.database import users_collection
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/create")
async def create_user(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken.")
    user.password = hash_password(user.password)
    users_collection.insert_one(user.model_dump())
    return {"message": "New user created successfully!"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    stored_user = users_collection.find_one({"username": form_data.username})
    if not stored_user or not verify_password(form_data.password, stored_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
