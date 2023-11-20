from pydantic import BaseModel, Field
from typing import List, Optional

class _PrecipitationData(BaseModel):
    one_hour: Optional[float] = Field(alias='1h', default=None)
    three_hours: Optional[float] = Field(alias='3h', default=None)

class _WindData(BaseModel):
    speed: Optional[float] = None
    deg: Optional[float] = None
    gust: Optional[float] = None

class _WeatherData(BaseModel):
    main: str
    description: str
    icon: str

class _MainData(BaseModel):
    temp: float
    feels_like: float
    pressure: float
    humidity: float
    grnd_level: Optional[float] = None

class RainfallResponse(BaseModel):
    lat: float
    lon: float
    rain: Optional[_PrecipitationData]
    wind: Optional[_WindData]
    weather: List[_WeatherData]
    main: _MainData
    clouds: float
    visibility: float
    snow: Optional[_PrecipitationData]
    city: str
    state: str

class RainfallQueryParams(BaseModel):
    lat: float
    lon: float
