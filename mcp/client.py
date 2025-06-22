from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# create server parameters for stdio connection
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "mcp_server.py"],
    env=None,
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()
            # list available tools
            resources = await session.list_resources()
            logger.info("LISTING RESOURCES")
            for resource in resources:
                logger.info(f"Resource: {resource}")

            # list available tools 
            tools_obj = await session.list_tools()
            logger.info("LISTING TOOLS")
            for tool in tools_obj.tools:
                logger.info(f"Tool: {tool}")

            # Read a resource
            # logger.info("READING RESOURCE")
            # content, mime_type = await session.read_resource("greeting://hello")

            # Call a tool
            logger.info("Getting current weather")
            result = await session.call_tool("get_current_weather", arguments={"location": "New York"})
            logger.info(result.content)

            logger.info("Forecasting Weather")
            result = await session.call_tool("get_forecast", arguments={"location": "Lagos", "days": 1})
            logger.info(result.content)

if __name__ == "__main__":
    asyncio.run(run())