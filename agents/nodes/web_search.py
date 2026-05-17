"""
Web search node.

When the router determines the city is NOT in our vector store, this
node uses DuckDuckGo to find information online, enriches it with
Wikipedia content, and asks the LLM to synthesize a conversational
response tailored to the user's specific question.

This creates the ChatGPT/Gemini-style experience the user expects —
not just flat summaries but intelligent, contextual answers.
"""

import asyncio
from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AgentState
from tools.search_tool import search_web
from tools.wikipedia_tool import get_wikipedia_summary
from utils.helpers import get_llm


SYSTEM_PROMPT = """You are VEXHALIA, an expert AI travel assistant. You provide 
intelligent, conversational responses like ChatGPT or Gemini — not generic summaries.

Key behaviors:
- Answer the user's SPECIFIC question, not a generic city overview
- If they ask about weather/activities, reason about the data (e.g., check rain 
  probability before recommending outdoor activities)
- Give personalized recommendations with insider tips
- Be warm, enthusiastic, and helpful — like a knowledgeable local friend
- When you have weather data, USE it to make smart suggestions
- If asked about timing (next week, tomorrow), factor weather into your advice
- Structure your response clearly with highlights, but keep it conversational
- Write 200-300 words, well-organized but natural-sounding
- If information is limited, be honest but still helpful with general knowledge"""


def web_search_node(state: AgentState) -> dict:
    """Search the web for city information, enrich with Wikipedia, and
    generate a conversational response.
    """
    city = state.get("city_name", "")
    user_input = state.get("user_input", "")

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

    # Fetch Wikipedia summary for enrichment
    wiki_summary = get_wikipedia_summary(city)

    if not results and not wiki_summary:
        return {
            "city_summary": (
                f"Could not find detailed information about {city} online. "
                f"Please check the city name and try again."
            ),
            "data_source": "web_search",
        }

    # Format search results into a context block
    search_context = ""
    if results:
        search_context = "Web search results:\n" + "\n\n".join(
            f"Source: {r['title']}\n{r['body']}" for r in results
        )

    wiki_section = ""
    if wiki_summary:
        wiki_section = f"\n\nWikipedia reference:\n{wiki_summary}"

    synthesis_prompt = (
        f"User asked: \"{user_input}\"\n\n"
        f"City: {city}\n\n"
        f"{search_context}"
        f"{wiki_section}\n\n"
        f"Based on ALL the above information, give a thoughtful, conversational "
        f"response that directly addresses what the user is asking about. "
        f"Don't just summarize — be helpful, specific, and engaging."
    )

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=synthesis_prompt),
    ])

    return {
        "city_summary": response.content,
        "data_source": "web_search",
    }
