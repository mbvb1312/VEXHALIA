"""
Web search node.

When the router determines the city is NOT in our vector store, this
node uses DuckDuckGo to find information online, then asks the LLM
to synthesize the search results into a coherent city summary.
"""

from langchain_core.messages import HumanMessage

from agents.state import AgentState
from tools.search_tool import search_web
from utils.helpers import get_llm

import asyncio


def web_search_node(state: AgentState) -> dict:
    """Search the web for city information and synthesize results.

    The search query is constructed to target travel-relevant content.
    We run the async search function synchronously here because
    LangGraph node functions are synchronous by default.
    """
    city = state.get("city_name", "")
    if not city:
        return {
            "city_summary": "Unable to search — no city name was provided.",
            "data_source": "web_search",
        }

    # Build a targeted search query
    search_query = f"{city} travel guide tourist attractions things to do"

    # Run the async search in a sync context
    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(search_web(search_query))
    finally:
        loop.close()

    if not results:
        return {
            "city_summary": (
                f"Could not find detailed information about {city} online. "
                f"Please check the city name and try again."
            ),
            "data_source": "web_search",
        }

    # Format search results into a context block for the LLM
    search_context = "\n\n".join(
        f"Source: {r['title']}\n{r['body']}" for r in results
    )

    synthesis_prompt = (
        f"Based on the following web search results about {city}, write an "
        f"engaging and informative travel summary. Cover the key highlights, "
        f"attractions, local culture, and practical tips. Write around "
        f"200-250 words.\n\n"
        f"Search results:\n{search_context}"
    )

    llm = get_llm()
    response = llm.invoke([HumanMessage(content=synthesis_prompt)])

    return {
        "city_summary": response.content,
        "data_source": "web_search",
    }
