"""
Vector store retrieval node.

When the router determines that a city is in our knowledge base, this
node fetches the relevant chunks from ChromaDB, enriches them with
Wikipedia content, and uses the LLM to synthesize a conversational
response that directly addresses the user's question.

Unlike a simple summarizer, this node creates ChatGPT/Gemini-style
responses that reason about the data — e.g., if the user asks about
boating next week, the LLM considers weather forecasts and rain
probability to give practical advice.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from agents.state import AgentState
from agents.nodes.router import get_collection
from data.vector_store import query_vector_store
from utils.helpers import get_llm
from tools.wikipedia_tool import get_wikipedia_summary


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
- Write 200-300 words, well-organized but natural-sounding"""


def retriever_node(state: AgentState) -> dict:
    """Pull relevant chunks from the vector store, enrich with Wikipedia,
    and generate a conversational response to the user's question.
    """
    city = state.get("city_name", "")
    user_input = state.get("user_input", "")
    collection = get_collection()

    # Retrieve top chunks — using the user's full query for better matching
    query_text = user_input if user_input else city
    documents, metadatas, distances = query_vector_store(
        collection, query_text, top_k=6
    )

    if not documents:
        return {
            "city_summary": f"No detailed information found for {city} in the knowledge base.",
            "data_source": "vector_store",
        }

    # Build context from retrieved chunks
    context_block = "\n\n".join(
        f"[{meta.get('category', 'general').upper()}] {doc}"
        for doc, meta in zip(documents, metadatas)
    )

    # Enrich with Wikipedia data
    wiki_summary = get_wikipedia_summary(city)
    wiki_section = ""
    if wiki_summary:
        wiki_section = f"\n\nWikipedia reference:\n{wiki_summary}"

    synthesis_prompt = (
        f"User asked: \"{user_input}\"\n\n"
        f"City: {city}\n\n"
        f"Knowledge base data:\n{context_block}"
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
        "data_source": "vector_store",
    }
