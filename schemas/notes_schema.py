from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional

class NotesSchema(BaseModel):
    title: Optional[str] = None
    description: str 
    color: Optional[str] =None
    reminder: Optional[str] = None
    user_id: int