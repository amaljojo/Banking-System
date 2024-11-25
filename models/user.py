from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Username must be between 3 and 30 characters")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    full_name: str = Field(..., max_length=50, description="Full name should be no more than 50 characters")
    email: Optional[EmailStr] = None  # Automatically validates for proper email format
  

    # Add a validator for the password field to check for strength requirements if needed
    @field_validator('password',mode='before')  
    def password_strength(cls, v):
        
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v
   






  
