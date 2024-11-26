from typing import Optional

from pydantic import BaseModel, Field
from bson import ObjectId


class FlightTicket(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    flight_number: str
    passenger_name: str
    destination: str
    price: float
    user_id: Optional[int] = None
    timestamp: Optional[str] = None

