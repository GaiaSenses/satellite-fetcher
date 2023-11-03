from pydantic import BaseModel

class BrightnessResponse(BaseModel):
    city: str
    state: str
    temp: float

class BrightnessQueryParams(BaseModel):
    lat: float
    lon: float
