import pytest
from unittest.mock import patch, MagicMock
from mcp_server import WeatherMCP, MCPServer

@pytest.fixture
def weather_tools():
    return WeatherTools(api_key="test_api_key")

@pytest.fixture
def mcp_server():
    return MCPServer()

def test_weather_tools_initialization():
    """Test WeatherTools initializes correctly"""
    tools = WeatherTools(api_key="test_api_key")
    assert tools.api_key is not None
    assert isinstance(tools.api_key, str)

@pytest.mark.asyncio
async def test_get_weather_data_success(weather_tools):
    """Test successful weather data retrieval"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "weather": [{"description": "clear sky"}],
            "main": {
                "temp": 20,
                "humidity": 65
            }
        }
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        weather_mcp = WeatherMCP()
        result = await weather_mcp.get_weather_data("London")
        
        assert result["status"] == "success"
        assert "temperature" in result["data"]
        assert "humidity" in result["data"]
        assert "description" in result["data"]

@pytest.mark.asyncio
async def test_get_weather_data_city_not_found():
    """Test weather data retrieval with invalid city"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = MagicMock()
        mock_response.status = 404
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        weather_mcp = WeatherMCP()
        result = await weather_mcp.get_weather_data("NonExistentCity")
        
        assert result["status"] == "error"
        assert "City not found" in result["message"]

@pytest.mark.asyncio
async def test_mcp_server_handle_request():
    """Test MCP server request handling"""
    server = MCPServer()
    
    mock_request = {
        "mcp": "weather",
        "action": "get_weather",
        "parameters": {"city": "London"}
    }
    
    with patch.object(WeatherMCP, 'get_weather_data') as mock_get_weather:
        mock_get_weather.return_value = {
            "status": "success",
            "data": {
                "temperature": 20,
                "humidity": 65,
                "description": "clear sky"
            }
        }
        
        response = await server.handle_request(mock_request)
        
        assert response["status"] == "success"
        assert "data" in response
        mock_get_weather.assert_called_once_with("London")

@pytest.mark.asyncio
async def test_mcp_server_invalid_request():
    """Test MCP server handling of invalid request"""
    server = MCPServer()
    
    invalid_request = {
        "mcp": "invalid_mcp",
        "action": "get_weather",
        "parameters": {"city": "London"}
    }
    
    response = await server.handle_request(invalid_request)
    assert response["status"] == "error"
    assert "Invalid MCP type" in response["message"]