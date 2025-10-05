import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Open-Meteo API kullanarak hava durumu verileri sağlar"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    @staticmethod
    async def get_weather_by_coordinates(lat: float, lon: float, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Koordinatlara göre mevcut hava durumu verilerini alır
        
        Args:
            lat: Enlem
            lon: Boylam
            units: Birim sistemi ('metric' veya 'imperial')
        
        Returns:
            Hava durumu verilerini içeren dict veya None
        """
        try:
            # Open-Meteo API parametreleri
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m", "apparent_temperature", "relative_humidity_2m", 
                    "precipitation", "pressure_msl", "surface_pressure",
                    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
                    "uv_index", "cloud_cover", "visibility"
                ],
                "daily": [
                    "temperature_2m_max", "temperature_2m_min", "weathercode",
                    "sunrise", "sunset", "uv_index_max", "precipitation_sum",
                    "wind_speed_10m_max", "wind_direction_10m_dominant"
                ],
                "timezone": "auto",
                "forecast_days": 7  # 7 günlük tahmin için
            }
            
            # Birim ayarları
            if units == "imperial":
                params["temperature_unit"] = "fahrenheit"
                params["wind_speed_unit"] = "mph"
                params["precipitation_unit"] = "inch"
            
            response = requests.get(WeatherService.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Veriyi düzenle
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            weather_data = {
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "current": {
                    "temperature": current.get("temperature_2m"),
                    "apparent_temperature": current.get("apparent_temperature"),
                    "humidity": current.get("relative_humidity_2m"),
                    "pressure": current.get("pressure_msl"),
                    "surface_pressure": current.get("surface_pressure"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "wind_direction": current.get("wind_direction_10m"),
                    "wind_gusts": current.get("wind_gusts_10m"),
                    "precipitation": current.get("precipitation"),
                    "uv_index": current.get("uv_index"),
                    "cloud_cover": current.get("cloud_cover"),
                    "visibility": current.get("visibility"),
                    "time": current.get("time")
                },
                "today": {
                    "max_temp": daily.get("temperature_2m_max", [None])[0] if daily.get("temperature_2m_max") else None,
                    "min_temp": daily.get("temperature_2m_min", [None])[0] if daily.get("temperature_2m_min") else None,
                    "weather_code": daily.get("weathercode", [None])[0] if daily.get("weathercode") else None,
                    "sunrise": daily.get("sunrise", [None])[0] if daily.get("sunrise") else None,
                    "sunset": daily.get("sunset", [None])[0] if daily.get("sunset") else None,
                    "uv_index_max": daily.get("uv_index_max", [None])[0] if daily.get("uv_index_max") else None,
                    "precipitation_sum": daily.get("precipitation_sum", [None])[0] if daily.get("precipitation_sum") else None
                },
                "forecast": {
                    "daily": []
                },
                "units": units,
                "updated_at": datetime.now().isoformat()
            }
            
            # 7 günlük tahmin ekle
            if daily.get("time"):
                for i in range(min(7, len(daily.get("time", [])))):
                    forecast_day = {
                        "date": daily.get("time", [])[i] if i < len(daily.get("time", [])) else None,
                        "max_temp": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                        "min_temp": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                        "weather_code": daily.get("weathercode", [])[i] if i < len(daily.get("weathercode", [])) else None,
                        "precipitation": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None,
                        "wind_speed": daily.get("wind_speed_10m_max", [])[i] if i < len(daily.get("wind_speed_10m_max", [])) else None,
                        "wind_direction": daily.get("wind_direction_10m_dominant", [])[i] if i < len(daily.get("wind_direction_10m_dominant", [])) else None
                    }
                    weather_data["forecast"]["daily"].append(forecast_day)
            
            return weather_data
            
        except requests.RequestException as e:
            logger.error(f"API isteği başarısız: {e}")
            return None
        except Exception as e:
            logger.error(f"Hava durumu verileri alınırken hata: {e}")
            return None
    
    @staticmethod
    def get_weather_description(weather_code: Optional[int]) -> str:
        """Hava durumu kodundan açıklama döndürür"""
        if not weather_code:
            return "Bilinmeyen"
            
        weather_codes = {
            0: "Açık hava",
            1: "Çoğunlukla açık",
            2: "Parçalı bulutlu",
            3: "Bulutlu",
            45: "Sisli",
            48: "Kırağılı sis",
            51: "Hafif çisenti",
            53: "Orta çisenti", 
            55: "Yoğun çisenti",
            61: "Hafif yağmur",
            63: "Orta yağmur",
            65: "Şiddetli yağmur",
            71: "Hafif kar",
            73: "Orta kar",
            75: "Şiddetli kar",
            80: "Hafif sağanak",
            81: "Orta sağanak",
            82: "Şiddetli sağanak",
            95: "Gök gürültülü fırtına",
            96: "Hafif dolu ile fırtına",
            99: "Şiddetli dolu ile fırtına"
        }
        
        return weather_codes.get(weather_code, f"Hava kodu: {weather_code}")
    
    @staticmethod
    async def get_weather_summary(lat: float, lon: float, units: str = "metric") -> Optional[str]:
        """
        Sohbet için hava durumu özeti döndürür
        
        Args:
            lat: Enlem
            lon: Boylam
            units: Birim sistemi
            
        Returns:
            Formatlanmış hava durumu metni
        """
        weather_data = await WeatherService.get_weather_by_coordinates(lat, lon, units)
        
        if not weather_data:
            return "Üzgünüm, şu anda hava durumu verilerini alamıyorum."
        
        current = weather_data["current"]
        today = weather_data["today"]
        
        temp_unit = "°F" if units == "imperial" else "°C"
        wind_unit = "mph" if units == "imperial" else "m/s"
        pressure_unit = "inHg" if units == "imperial" else "hPa"
        
        description = WeatherService.get_weather_description(today.get("weather_code"))
        
        summary = f"**Bugünün Hava Durumu**\n\n"
        summary += f"Konum: {lat:.3f}, {lon:.3f}\n"
        summary += f"Sıcaklık: {current.get('temperature', 'N/A')}{temp_unit}\n"
        
        if current.get("apparent_temperature"):
            summary += f"Hissedilen: {current['apparent_temperature']}{temp_unit}\n"
        
        if today.get("max_temp") and today.get("min_temp"):
            summary += f"Bugün: {today['max_temp']}{temp_unit} / {today['min_temp']}{temp_unit}\n"
        
        summary += f"Durum: {description}\n"
        
        if current.get("humidity"):
            summary += f"Nem: %{current['humidity']}\n"
            
        if current.get("pressure"):
            summary += f"Basınç: {current['pressure']} {pressure_unit}\n"
        
        summary += f"Rüzgar: {current.get('wind_speed', 'N/A')} {wind_unit}\n"
        
        if current.get("wind_gusts"):
            summary += f"Rüzgar Hızı (Max): {current['wind_gusts']} {wind_unit}\n"
        
        if current.get("uv_index") is not None:
            uv_level = "Düşük" if current['uv_index'] < 3 else "Orta" if current['uv_index'] < 6 else "Yüksek" if current['uv_index'] < 8 else "Çok Yüksek"
            summary += f"UV İndeksi: {current['uv_index']} ({uv_level})\n"
        
        if current.get("cloud_cover"):
            summary += f"Bulutluluk: %{current['cloud_cover']}\n"
        
        if current.get("visibility"):
            summary += f"Görüş: {current['visibility']} km\n"
        
        if current.get("precipitation"):
            prec_unit = "inch" if units == "imperial" else "mm"
            summary += f"Yağış: {current['precipitation']} {prec_unit}/h\n"
        
        # Güneş doğuş/batış
        if today.get("sunrise") and today.get("sunset"):
            try:
                sunrise = datetime.fromisoformat(today['sunrise'].replace('Z', '+00:00'))
                sunset = datetime.fromisoformat(today['sunset'].replace('Z', '+00:00'))
                summary += f"\nGüneş Doğuş: {sunrise.strftime('%H:%M')}\n"
                summary += f"Güneş Batış: {sunset.strftime('%H:%M')}\n"
            except:
                pass
        
        summary += f"\nGüncelleme: {datetime.now().strftime('%H:%M')}"
        
        return summary
    
    @staticmethod
    async def get_tomorrow_forecast(lat: float, lon: float, units: str = "metric") -> str:
        """
        Yarın için hava tahmini formatlanmış metin
        
        Args:
            lat: Enlem
            lon: Boylam
            units: Birim sistemi
            
        Returns:
            Formatlanmış yarın hava tahmini metni
        """
        weather_data = await WeatherService.get_weather_by_coordinates(lat, lon, units)
        
        if not weather_data or not weather_data.get("forecast", {}).get("daily"):
            return "Üzgünüm, şu anda yarın hava tahmini verilerini alamıyorum."
        
        forecast_data = weather_data["forecast"]["daily"]
        
        if len(forecast_data) < 2:
            return "Yarın için hava tahmini bulunamadı."
        
        tomorrow = forecast_data[1]  # İkinci gün (yarın)
        
        temp_unit = "°F" if units == "imperial" else "°C"
        
        description = WeatherService.get_weather_description(tomorrow.get("weather_code"))
        
        summary = f"**Yarın Hava Durumu**\n\n"
        summary += f"Tarih: {tomorrow.get('date', 'Bilinmiyor')}\n"
        summary += f"Sıcaklık: {tomorrow.get('max_temp', 'N/A')}{temp_unit} / {tomorrow.get('min_temp', 'N/A')}{temp_unit}\n"
        summary += f"Durum: {description}\n"
        
        if tomorrow.get("precipitation_probability"):
            summary += f"Yağış İhtimali: %{tomorrow['precipitation_probability']}\n"
        
        if tomorrow.get("precipitation_sum"):
            prec_unit = "inch" if units == "imperial" else "mm"
            summary += f"Toplam Yağış: {tomorrow['precipitation_sum']} {prec_unit}\n"
        
        if tomorrow.get("uv_index_max"):
            uv_level = "Düşük" if tomorrow['uv_index_max'] < 3 else "Orta" if tomorrow['uv_index_max'] < 6 else "Yüksek" if tomorrow['uv_index_max'] < 8 else "Çok Yüksek"
            summary += f"Max UV İndeksi: {tomorrow['uv_index_max']} ({uv_level})\n"
        
        if tomorrow.get("wind_speed_max"):
            wind_unit = "mph" if units == "imperial" else "m/s"
            summary += f"Max Rüzgar: {tomorrow['wind_speed_max']} {wind_unit}\n"
        
        if tomorrow.get("sunrise") and tomorrow.get("sunset"):
            try:
                sunrise = datetime.fromisoformat(tomorrow['sunrise'].replace('Z', '+00:00'))
                sunset = datetime.fromisoformat(tomorrow['sunset'].replace('Z', '+00:00'))
                summary += f"Güneş Doğuş: {sunrise.strftime('%H:%M')}\n"
                summary += f"Güneş Batış: {sunset.strftime('%H:%M')}\n"
            except:
                pass
        
        return summary
    
    @staticmethod
    async def get_weekly_forecast(lat: float, lon: float, units: str = "metric") -> Optional[str]:
        """
        7 günlük hava tahmini döndürür
        
        Args:
            lat: Enlem
            lon: Boylam
            units: Birim sistemi
            
        Returns:
            Formatlanmış haftalık tahmin metni
        """
        weather_data = await WeatherService.get_weather_by_coordinates(lat, lon, units)
        
        if not weather_data:
            return "7 günlük tahmin şu anda alınamıyor."
        
        forecast = weather_data.get("forecast", {}).get("daily", [])
        
        if not forecast:
            return "Haftalık tahmin verisi bulunamadı."
        
        temp_unit = "°F" if units == "imperial" else "°C"
        
        summary = f"**7 Günlük Hava Tahmini**\n\n"
        
        for i, day in enumerate(forecast[:7]):
            if not day.get("date"):
                continue
                
            try:
                date_obj = datetime.fromisoformat(day["date"])
                day_name = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][date_obj.weekday()]
                date_str = date_obj.strftime("%d.%m")
                
                if i == 0:
                    day_label = "Bugün"
                elif i == 1:
                    day_label = "Yarın"
                else:
                    day_label = f"{day_name} ({date_str})"
                
                description = WeatherService.get_weather_description(day.get("weather_code"))
                max_temp = day.get("max_temp", "N/A")
                min_temp = day.get("min_temp", "N/A")
                
                summary += f"{day_label}: {max_temp}°/{min_temp}° - {description}\n"
                
                if day.get("precipitation") and day["precipitation"] > 0:
                    prec_unit = "inch" if units == "imperial" else "mm"
                    summary += f"  Yağış: {day['precipitation']} {prec_unit}\n"
                    
            except Exception as e:
                continue
        
        return summary