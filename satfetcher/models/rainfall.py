from pydantic import BaseModel, Field
from typing import List, Optional

class _RainData(BaseModel):
    one_hour: float = Field(alias='1h')
    three_hours: float = Field(alias='3h')

class _WindData(BaseModel):
    speed: float
    deg: float
    gust: float

class _WeatherData(BaseModel):
    main: str
    description: str
    icon: str

class _MainData(BaseModel):
    temp: float
    feels_like: float
    pressure: float
    humidity: float
    grnd_level: float

class RainfallResponse(BaseModel):
    lat: float
    lon: float
    rain: Optional[_RainData]
    wind: Optional[_WindData]
    weather: List[_WeatherData]
    main: _MainData
    clouds: float
    visibility: float
    city: str
    state: str

class RainfallQueryParams(BaseModel):
    lat: float
    lon: float
