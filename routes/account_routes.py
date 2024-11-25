from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from config.database import accounts_collection
from models.account import Account
from config.auth import verify_jwt_token
from bson import ObjectId
from datetime import datetime
import pytz

router = APIRouter()



# Get Account Details by Account Number
@router.get("/account/{account_number}")
async def account_details(account_number: str, token: dict = Depends(verify_jwt_token)):
    account = accounts_collection.find_one({"account_number": account_number, "user": token['sub']})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return jsonable_encoder(account, custom_encoder={ObjectId: str})

# Get All Accounts for Logged-In User
@router.get("/accounts")
async def all_accounts(token: dict = Depends(verify_jwt_token)):
    accounts = list(accounts_collection.find({"user": token['sub']}))
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found")
    return jsonable_encoder(accounts, custom_encoder={ObjectId: str})


# Filter accounts based on balance (<= max_balance)
@router.get("/accounts/filter")
async def filter_accounts(max_balance: float, token: dict = Depends(verify_jwt_token)):
    accounts = list(accounts_collection.find({"user": token["sub"], "balance": {"$lte": max_balance}}))
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found with the specified filter.")
    return jsonable_encoder(accounts, custom_encoder={ObjectId: str})

# Create Account
@router.post("/account")
async def create_new_account(account: Account, token: dict = Depends(verify_jwt_token)):
    account_data = account.model_dump()  
    account_data['user'] = token['sub']  
    local_time = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d  %H:%M:%S")
    account_data['created_at'] = local_time
    accounts_collection.insert_one(account_data)
    return {"message": "Account created successfully!"}

# Deposit Funds
@router.put("/account/{account_number}/deposit")
async def deposit(account_number: str, amount: float, token: dict = Depends(verify_jwt_token)):
    account = accounts_collection.find_one({"account_number": account_number, "user": token['sub']})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    new_balance = account['balance'] + amount
    accounts_collection.update_one({"account_number": account_number}, {"$set": {"balance": new_balance}})
    return {"message": "Deposit successful", "new_balance": new_balance}

# Withdraw Funds
@router.put("/account/{account_number}/withdraw")
async def withdraw(account_number: str, amount: float, token: dict = Depends(verify_jwt_token)):
    account = accounts_collection.find_one({"account_number": account_number, "user": token['sub']})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account['balance'] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    new_balance = account['balance'] - amount
    accounts_collection.update_one({"account_number": account_number}, {"$set": {"balance": new_balance}})
    return {"message": "Withdrawal successful", "new_balance": new_balance}

# Delete Account
@router.delete("/account/{account_number}")
async def delete_account(account_number: str, token: dict = Depends(verify_jwt_token)):
    account = accounts_collection.find_one({"account_number": account_number, "user": token['sub']})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    accounts_collection.delete_one({"account_number": account_number})
    return {"message": "Account deleted successfully"}










