from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime


class CalculationCreate(BaseModel):
    a: float
    b: float
    type: Literal["Add", "Sub", "Multiply", "Divide"]
    user_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_divide_by_zero(self):
        if self.type == "Divide" and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self


class CalculationUpdate(BaseModel):
    a: float
    b: float
    type: Literal["Add", "Sub", "Multiply", "Divide"]

    @model_validator(mode="after")
    def validate_divide_by_zero(self):
        if self.type == "Divide" and self.b == 0:
            raise ValueError("Cannot divide by zero.")
        return self


class CalculationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[int]
    created_at: datetime