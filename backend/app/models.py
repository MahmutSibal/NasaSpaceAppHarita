from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class WeatherRequest(BaseModel):
    """Hava durumu talebi modeli"""
    latitude: float = Field(..., ge=-90, le=90, description="Enlem (-90 ile 90 arası)")
    longitude: float = Field(..., ge=-180, le=180, description="Boylam (-180 ile 180 arası)")
    units: str = Field(default="metric", description="Birim sistemi (metric veya imperial)")

class LocationInfo(BaseModel):
    """Konum bilgileri"""
    latitude: float
    longitude: float

class CurrentWeather(BaseModel):
    """Mevcut hava durumu"""
    temperature: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[float]
    precipitation: Optional[float]
    time: Optional[str]

class DailyWeather(BaseModel):
    """Günlük hava durumu"""
    max_temp: Optional[float]
    min_temp: Optional[float]
    weather_code: Optional[int]

class WeatherResponse(BaseModel):
    """Hava durumu yanıt modeli"""
    location: LocationInfo
    current: CurrentWeather
    today: DailyWeather
    units: str
    updated_at: str

class ChatRequest(BaseModel):
    """Sohbet talebi modeli"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    units: str = Field(default="metric")
    message: str = Field(..., min_length=1, description="Kullanıcı mesajı")

class ChatResponse(BaseModel):
    """Sohbet yanıt modeli"""
    response: str
    weather_data: Optional[WeatherResponse] = None
    timestamp: str