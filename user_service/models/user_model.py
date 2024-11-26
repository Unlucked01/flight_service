from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: int = Field(alias="_id")
    name: Optional[str] = None
    email: Optional[str] = None
    registered_objects: int = 0
