from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional


class UserRegister(BaseModel):
    user_id: Optional[str] = ""
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    phonenumber: int
    password: constr(min_length=8)
    first_name: Optional[constr(max_length=10)] = None
    last_name: Optional[constr(max_length=10)] = None
    created_on: Optional[str] = 0
    updated_on: Optional[str] = 0
    failed_attempts: Optional[int] = Field(default=0)

    @validator("username")
    def username_alphanumeric(cls, v):
        assert v.isalnum(), "must be alphanumeric"
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "strongpassword",
                "password_confirm": "strongpassword",
                "first_name": "John",
                "last_name": "Doe",
            }
        }


class LoginRequest(BaseModel):
    username: str
    password: str
    max_age: int = 30


class ResetPasswordRequest(BaseModel):
    user_name: str
    new_password: Optional[str] = None
    confirm_password: Optional[str] = None
    old_password: Optional[str] = None
    user_id: Optional[str] = None
