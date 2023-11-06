from pydantic import BaseModel
from typing import List, Optional

class _LightningEvent(BaseModel):
    lat: float
    lon: float
    dist: float

class LightningResponse(BaseModel):
    count: int
    city: str
    state: str
    events: List[_LightningEvent]

class LightningQueryParams(BaseModel):
    lat: float
    lon: float
    dist: Optional[float] = 50.0
