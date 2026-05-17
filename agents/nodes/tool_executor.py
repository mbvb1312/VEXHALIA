"""
Manual tool executor — Distinction Challenge #1.

Instead of relying on LangGraph's prebuilt ToolNode or LangChain's
create_tool_calling_agent, this module manually parses the LLM's raw
tool_calls response, executes the corresponding functions, and appends
ToolMessage objects back into the state.

This demonstrates understanding of the raw LLM API protocol: the model
returns a structured tool_calls array, and we are responsible for
executing each call and formatting the result as a ToolMessage with
the matching tool_call_id.
"""

import json
import asyncio
from langchain_core.messages import AIMessage, ToolMessage

from agents.state import AgentState
from tools.weather_tool import get_weather, generate_mock_weather
from tools.image_tool import get_images, generate_fallback_images
from tools.search_tool import search_web


# Registry mapping tool names to their implementation functions.
# When the LLM says "call get_weather_forecast", we look it up here.
TOOL_REGISTRY: dict[str, callable] = {
    "get_weather_forecast": get_weather,
    "get_city_images": get_images,
    "search_city_info": search_web,
}


def build_tool_definitions() -> list[dict]:
    """Return OpenAI-format tool definitions to bind to the LLM.

    These schemas tell the model what tools are available and what
    arguments each one expects. The model then returns structured
    tool_calls that we parse in execute_tool_calls().
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather_forecast",
                "description": (
                    "Fetch the 7-day weather forecast for a given city. "
                    "Returns daily high/low temperatures, precipitation "
                    "chance, humidity, and weather conditions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_name": {
                            "type": "string",
                            "description": "Name of the city to get weather for",
                        }
                    },
                    "required": ["city_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_city_images",
                "description": (
                    "Retrieve high-quality photographs of a city's landmarks "
                    "and attractions. Returns a list of image URLs with captions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_name": {
                            "type": "string",
                            "description": "Name of the city to get images for",
                        }
                    },
                    "required": ["city_name"],
                },
            },
        },
    ]


def tool_executor_node(state: AgentState) -> dict:
    """Parse and execute tool calls from the LLM's response.

    This is the 'manual transmission' approach:
    1. Look at the last AIMessage for tool_calls
    2. For each tool call, extract name, args, and id
    3. Look up the function in our registry
    4. Execute it (handling async functions in sync context)
    5. Wrap the result in a ToolMessage with the matching tool_call_id
    6. Append all ToolMessages back to state

    We deliberately avoid using LangGraph's ToolNode or any prebuilt
    abstraction — this is raw protocol-level tool execution.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    # Find the last AI message that contains tool calls
    last_ai_msg = None
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            last_ai_msg = msg
            break

    if last_ai_msg is None:
        return {}

    tool_messages = []
    weather_data = []
    image_data = []

    for tool_call in last_ai_msg.tool_calls:
        func_name = tool_call["name"]
        func_args = tool_call["args"]
        call_id = tool_call["id"]

        # Look up the function in our registry
        func = TOOL_REGISTRY.get(func_name)
        if func is None:
            tool_messages.append(
                ToolMessage(
                    content=f"Error: Unknown tool '{func_name}'",
                    tool_call_id=call_id,
                )
            )
            continue

        # Execute the tool — handle both async and sync functions
        try:
            if asyncio.iscoroutinefunction(func):
                loop = asyncio.new_event_loop()
                try:
                    result = loop.run_until_complete(func(**func_args))
                finally:
                    loop.close()
            else:
                result = func(**func_args)

            # Serialize the result for the ToolMessage content
            if isinstance(result, list):
                serialized = json.dumps(
                    [item.model_dump() if hasattr(item, 'model_dump') else item for item in result],
                    indent=2,
                )
                # Also store structured data for the state
                if func_name == "get_weather_forecast":
                    weather_data = [
                        item.model_dump() if hasattr(item, 'model_dump') else item
                        for item in result
                    ]
                elif func_name == "get_city_images":
                    image_data = [
                        item.model_dump() if hasattr(item, 'model_dump') else item
                        for item in result
                    ]
            else:
                serialized = json.dumps(result, indent=2) if not isinstance(result, str) else result

            tool_messages.append(
                ToolMessage(content=serialized, tool_call_id=call_id)
            )

        except Exception as e:
            tool_messages.append(
                ToolMessage(
                    content=f"Error executing {func_name}: {str(e)}",
                    tool_call_id=call_id,
                )
            )

    # Build the state update
    update = {"messages": tool_messages}
    if weather_data:
        update["weather_forecast"] = weather_data
    if image_data:
        update["images"] = image_data
        update["image_urls"] = [
            img["url"] if isinstance(img, dict) else img.url
            for img in image_data
        ]

    return update
