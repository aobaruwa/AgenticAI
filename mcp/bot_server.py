#!/usr/bin/env python3
import asyncio
import logging
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create an instance of a FastMCP server
mcp = FastMCP(
    name="Weather MCP Server",
    version="1.0.0"
)

class WeatherTools:
    def __init__(self, api_key: str):
        """Initialize the WeatherTools with an API key."""
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1"
        logger.info(f"Initialized WeatherTools with API key: {api_key[:10]}...")

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make HTTP request to WeatherAPI."""
        params['key'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            with httpx.Client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

# Create a global instance
weather_tools = None

@mcp.tool()
def get_current_weather(location: str) -> dict:
    """Get the current weather for a given location.
    
    Args:
        location: City name, coordinates, or location query
    
    Returns:
        Current weather data including temperature, humidity, wind, etc.
    """
    try:
        logger.info(f"Fetching current weather for: {location}")
        
        data = weather_tools._make_request("current.json", {
            "q": location,
            "aqi": "yes"
        })
        
        current = data['current']
        location_info = data['location']
        
        result = {
            "location": f"{location_info['name']}, {location_info['region']}, {location_info['country']}",
            "temperature_c": current['temp_c'],
            "temperature_f": current['temp_f'],
            "feels_like_c": current['feelslike_c'],
            "feels_like_f": current['feelslike_f'],
            "condition": current['condition']['text'],
            "humidity": current['humidity'],
            "wind_kph": current['wind_kph'],
            "wind_mph": current['wind_mph'],
            "wind_dir": current['wind_dir'],
            "pressure_mb": current['pressure_mb'],
            "visibility_km": current['vis_km'],
            "visibility_miles": current['vis_miles'],
            "uv_index": current['uv'],
            "precipitation_mm": current['precip_mm'],
            "last_updated": current['last_updated']
        }
        
        # Add air quality if available
        if 'air_quality' in data:
            result['air_quality'] = data['air_quality']
        
        logger.debug(f"Current weather data: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching current weather: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def get_weather_forecast(location: str, days: int = 3) -> dict:
    """Get the weather forecast for a given location.
    
    Args:
        location: City name, coordinates, or location query
        days: Number of forecast days (1-10)
    
    Returns:
        Weather forecast data for the specified number of days
    """
    try:
        logger.info(f"Fetching {days}-day forecast for: {location}")
        
        # Ensure days is within valid range
        days = max(1, min(10, days))

        data = weather_tools._make_request("forecast.json", {
            "q": location,
            "days": days,
            "aqi": "no",
            "alerts": "no"
        })
        
        location_info = data['location']
        forecast_days = data['forecast']['forecastday']
        
        result = {
            "location": f"{location_info['name']}, {location_info['region']}, {location_info['country']}",
            "forecast_days": days,
            "forecast": []
        }
        
        for day_data in forecast_days:
            day_info = day_data['day']
            day_forecast = {
                "date": day_data['date'],
                "max_temp_c": day_info['maxtemp_c'],
                "max_temp_f": day_info['maxtemp_f'],
                "min_temp_c": day_info['mintemp_c'],
                "min_temp_f": day_info['mintemp_f'],
                "avg_temp_c": day_info['avgtemp_c'],
                "avg_temp_f": day_info['avgtemp_f'],
                "condition": day_info['condition']['text'],
                "chance_of_rain": day_info['daily_chance_of_rain'],
                "chance_of_snow": day_info['daily_chance_of_snow'],
                "avg_humidity": day_info['avghumidity'],
                "max_wind_kph": day_info['maxwind_kph'],
                "max_wind_mph": day_info['maxwind_mph'],
                "total_precip_mm": day_info['totalprecip_mm'],
                "avg_visibility_km": day_info['avgvis_km'],
                "avg_visibility_miles": day_info['avgvis_miles'],
                "uv_index": day_info['uv']
            }
            result["forecast"].append(day_forecast)
        
        logger.debug(f"Forecast data: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching forecast: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def get_astronomy_data(location: str, date: str = None) -> dict:
    """Get astronomy data (sunrise, sunset, moon phases) for a location.
    
    Args:
        location: City name, coordinates, or location query
        date: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        Astronomy data including sunrise, sunset, moon phases
    """
    try:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Fetching astronomy data for: {location} on {date}")
        
        data = weather_tools._make_request("astronomy.json", {
            "q": location,
            "dt": date
        })
        
        location_info = data['location']
        astro_data = data['astronomy']['astro']
        
        result = {
            "location": f"{location_info['name']}, {location_info['region']}, {location_info['country']}",
            "date": date,
            "sunrise": astro_data['sunrise'],
            "sunset": astro_data['sunset'],
            "moonrise": astro_data['moonrise'],
            "moonset": astro_data['moonset'],
            "moon_phase": astro_data['moon_phase'],
            "moon_illumination": astro_data['moon_illumination']
        }
        
        logger.debug(f"Astronomy data: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching astronomy data: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

@mcp.tool()
def get_weather_alerts(location: str) -> dict:
    """Get active weather alerts for a location.
    
    Args:
        location: City name, coordinates, or location query
    
    Returns:
        Active weather alerts and warnings
    """
    try:
        logger.info(f"Fetching weather alerts for: {location}")
        
        data = weather_tools._make_request("forecast.json", {
            "q": location,
            "days": 1,
            "aqi": "no",
            "alerts": "yes"
        })
        
        location_info = data['location']
        alerts = data.get('alerts', {}).get('alert', [])
        
        result = {
            "location": f"{location_info['name']}, {location_info['region']}, {location_info['country']}",
            "alerts_count": len(alerts),
            "alerts": []
        }
        
        for alert in alerts:
            alert_data = {
                "headline": alert['headline'],
                "msgtype": alert['msgtype'],
                "severity": alert['severity'],
                "urgency": alert['urgency'],
                "areas": alert['areas'],
                "category": alert['category'],
                "certainty": alert['certainty'],
                "event": alert['event'],
                "note": alert['note'],
                "effective": alert['effective'],
                "expires": alert['expires'],
                "desc": alert['desc'],
                "instruction": alert['instruction']
            }
            result["alerts"].append(alert_data)
        
        logger.debug(f"Weather alerts: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Error fetching weather alerts: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

def main():
    """Main function to run the MCP server."""
    global weather_tools
    
    logger.info("Starting Weather MCP Server...")
    
    # Initialize weather tools with API key
    api_key = '53f63b9961eb49819af231815251306'  # Your API key
    weather_tools = WeatherTools(api_key)
    
    logger.info("Successfully initialized the weather tools")
    logger.info("Starting MCP server with stdio transport")
    
    # Run the FastMCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
    