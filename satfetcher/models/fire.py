from pydantic import BaseModel
from typing import List, Optional

class _FireEvent(BaseModel):
    lat: float
    lon: float
    dist: float

class FireResponse(BaseModel):
    count: int
    city: str
    state: str
    events: List[_FireEvent]

class FireQueryParams(BaseModel):
    lat: float
    lon: float
    dist: Optional[float] = 50.0
