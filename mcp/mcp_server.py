import asyncio
import httpx
import logging
import weatherapi
from datetime import datetime
from mcp.server.fastmcp import FastMCP 
# from mcp.server.stdio import stdio_server

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Weather application
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
weather_tools = WeatherTools(api_key='53f63b9961eb49819af231815251306')

# Create an instance of a FastMCP server
mcp = FastMCP(
    name="Weather MCP Server",
    version="1.0.0"
)

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
def get_forecast(location: str, days: int = 3) -> dict:
    """Get the weather forecast for a given location."""  
    try:
        response = weather_tools._make_request("forecast.json", {
            "q": location,
            "days": days
        })
        logger.debug(f"Raw forecast API output for {location}: {response}")
        return response 
        # weather_data = [{
        #     "location": location,
        #     "temperature": response.temperature,
        #     "humidity": response.humidity,
        #     "wind_speed": response.wind_speed,
        #     "description": response.description
        # } for _ in range(days)]
        # return weather_data
    except Exception as e:
        logger.error(f"Error fetching forecast: {e}")
        return {"error": str(e)}
    

def main():
    """Main function to run the MCP server."""
    
    logger.info("Starting Weather MCP Server...")

    # Start the MCP server with stdio transport
    logger.info("Successfully initialized the weather tools")
    logger.info("Starting MCP server with stdio transport")
    # Run the FastMCP server
    mcp.run(transport="stdio")
   
if __name__ == "__main__":
    main()


"""
{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
"""