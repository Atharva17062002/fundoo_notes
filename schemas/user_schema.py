from pydantic import BaseModel, Field, validator, ValidationError
from typing import Optional
import re

class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=100, pattern="^[a-zA-Z0-9_-]+$")
    email: str = Field(min_length=3, max_length=100, pattern="^[a-z0-9+-\.]+(\.)?@[a-z0-9]+\.[a-z]{2,}(\.[a-z]+)?$")
    password: str = Field(min_length=8, max_length=10)
    location: Optional[str] = None

    @validator('email')
    def email_must_be_valid(cls, email):
        assert '@' in email, 'Invalid email'
        return email

    @validator('password')
    def password_must_contain_special_characters(cls, password):
        # regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        if not re.match('^[A-Za-z0-9]{8,}$', password):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, one digit and one special character')
        return password





