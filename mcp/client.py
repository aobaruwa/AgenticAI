from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SytemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential;
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import json
import logging
import os

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
                logger.info(f"Tool: {tool.inputShema["properties"]}")
                functions.append(convert_to_llm_tool(tool))

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

def convert_to_llm_tool(tool):
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description" : tool.description, 
            "type": "function",
            "parameters": {
                "type": "object", 
                "properties": tool.inputSchema["properties"]
            }
        }
    }
    return tool_schema

# llm 

def call_llm(prompt, functions):
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.inference.ai.azure.com"

    model_name = "gpt-4o"
    client = ChatCompletionsClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(token)
    )
    logger.info("CALLING LLM")
    response = client.complete(
        messages=[
            {
                "role":"system",
                "content": "You are a helfpul assistant"
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        model=model_name,
        tools=functions,
        # Optional parameters
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0
    )
    response_message = response.choices[0].message
    functions_to_call = []

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            logger.info(f"TOOL: ", tool_call)
            name = tool_call.function.name
            args = json.loads(tool_call, function.arguments)
            functions_to_call.append({ "name": name, "args", arg})
if __name__ == "__main__":
    asyncio.run(run())