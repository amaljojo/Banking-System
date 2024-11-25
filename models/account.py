from pydantic import BaseModel, Field,field_validator
from typing import Optional

class Account(BaseModel):
    account_number: str = Field(..., pattern=r"^\d{10}$", description="Account number must be exactly 10 digits")
    username: str = Field(..., min_length=3, max_length=30, description="Username must be between 3 and 30 characters")
    balance: float = Field(0.0, ge=0, description="Balance must be a positive value")
    account_type: str = Field("Savings", pattern=r"^(Savings|Checking|Business)$", description="Account type can be 'Savings', 'Checking', or 'Business'")

    # Example: add a validator to ensure that the account number has the expected format.
    @field_validator('account_number', mode='before')  
    def account_number_must_be_digits(cls, v):
        if not v.isdigit():
            raise ValueError("Account number must contain only digits")
        return v







