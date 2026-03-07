import re
from typing import Literal
from pydantic import BaseModel, Field, field_validator

# ==================== Add Worker Schema ====================
class AddWorker(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    cnic: str = Field(..., min_length=13, max_length=13)
    job_type: Literal["reports", "courses"]
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')

    @field_validator('cnic')
    @classmethod
    def validate_cnic(cls, v):
        if len(v) != 13:
            raise ValueError('CNIC must be exactly 13 characters long')
        if not v.isdigit():
            raise ValueError('CNIC must contain only digits')
        return v

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Worker Name",
                "cnic": "1234567890123",
                "job_type": "courses",
                "username": "worker_user"
            }
        }
