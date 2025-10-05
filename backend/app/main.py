import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime

from weather_service import WeatherService
from models import WeatherRequest, WeatherResponse, ChatRequest, ChatResponse

load_dotenv()

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]

app = FastAPI(title="Weather API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Weather API is running"}

@app.get("/")
async def root():
    return {"message": "Hava Durumu API - Weather data is provided via external APIs (Open-Meteo)"}

@app.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """Koordinatlara göre hava durumu verilerini döndürür"""
    try:
        weather_data = await WeatherService.get_weather_by_coordinates(
            request.latitude, 
            request.longitude, 
            request.units
        )
        
        if not weather_data:
            raise HTTPException(
                status_code=503, 
                detail="Hava durumu verileri şu anda alınamıyor"
            )
        
        return WeatherResponse(**weather_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hava durumu verileri alınırken hata oluştu: {str(e)}"
        )

@app.post("/chat/weather", response_model=ChatResponse)
async def chat_weather(request: ChatRequest):
    """Sohbet için hava durumu bilgisi döndürür"""
    try:
        # Kullanıcının mesajını analiz et
        message = request.message.lower()
        
        # Hava durumu ile ilgili anahtar kelimeler
        weather_keywords = [
            "hava", "sıcaklık", "yağmur", "kar", "rüzgar", "bugün", "weather", 
            "derece", "soğuk", "sıcak", "nasıl", "durum"
        ]
        
        is_weather_request = any(keyword in message for keyword in weather_keywords)
        
        if is_weather_request:
            # Hava durumu verilerini al
            weather_summary = await WeatherService.get_weather_summary(
                request.latitude,
                request.longitude,
                request.units
            )
            
            # Ayrıntılı veri de al
            weather_data = await WeatherService.get_weather_by_coordinates(
                request.latitude,
                request.longitude,
                request.units
            )
            
            response_text = weather_summary or "Hava durumu verileri şu anda mevcut değil."
            weather_response = WeatherResponse(**weather_data) if weather_data else None
            
        else:
            # Hava durumu ile ilgili değilse genel yanıt ver
            response_text = "Merhaba! Ben bir hava durumu asistanıyım. 🌤️ Bugünün hava durumu hakkında bilgi almak için 'bugün hava nasıl?' gibi sorular sorabilirsiniz."
            weather_response = None
        
        return ChatResponse(
            response=response_text,
            weather_data=weather_response,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sohbet işlemi sırasında hata oluştu: {str(e)}"
        )

@app.post("/forecast/weekly")
async def get_weekly_forecast(request: WeatherRequest):
    """7 günlük hava tahmini döndürür"""
    try:
        forecast_text = await WeatherService.get_weekly_forecast(
            request.latitude, 
            request.longitude, 
            request.units
        )
        
        if not forecast_text:
            raise HTTPException(
                status_code=503, 
                detail="Haftalık tahmin verileri şu anda alınamıyor"
            )
        
        return {
            "forecast": forecast_text,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "units": request.units,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Haftalık tahmin alınırken hata oluştu: {str(e)}"
        )

@app.post("/forecast/tomorrow")
async def get_tomorrow_forecast(request: WeatherRequest):
    """Yarın için hava durumu tahmini"""
    try:
        tomorrow_forecast = await WeatherService.get_tomorrow_forecast(
            request.latitude,
            request.longitude,
            request.units
        )
        
        if not tomorrow_forecast:
            raise HTTPException(
                status_code=404,
                detail="Yarın hava tahmini alınamadı"
            )
        
        return {
            "forecast": tomorrow_forecast,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "units": request.units,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Yarın tahmini alınırken hata oluştu: {str(e)}"
        )
