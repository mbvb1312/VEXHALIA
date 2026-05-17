"""
Vector store retrieval node.

When the router determines that a city is in our knowledge base, this
node fetches the relevant chunks from ChromaDB and uses the LLM to
synthesize them into a coherent, engaging city summary. This is the
'internal database' path of the agent's decision tree.
"""

from langchain_core.messages import HumanMessage, AIMessage

from agents.state import AgentState
from agents.nodes.router import get_collection
from data.vector_store import query_vector_store
from utils.helpers import get_llm


def retriever_node(state: AgentState) -> dict:
    """Pull relevant chunks from the vector store and synthesize a summary.

    We query with both the city name and the user's original message
    to capture any specific aspects they asked about (e.g., 'food in Paris'
    vs just 'Paris').
    """
    city = state.get("city_name", "")
    collection = get_collection()

    # Retrieve top chunks — using the city name as the primary query
    documents, metadatas, distances = query_vector_store(
        collection, city, top_k=6
    )

    if not documents:
        return {
            "city_summary": f"No detailed information found for {city} in the knowledge base.",
            "data_source": "vector_store",
        }

    # Build context from retrieved chunks for the LLM
    context_block = "\n\n".join(documents)

    synthesis_prompt = (
        f"Using the following reference material about {city}, write an engaging "
        f"and informative travel summary. Cover the key highlights, landmarks, "
        f"food scene, and practical travel tips. Keep it concise but rich — "
        f"around 200-250 words.\n\n"
        f"Reference material:\n{context_block}"
    )

    llm = get_llm()
    response = llm.invoke([HumanMessage(content=synthesis_prompt)])

    return {
        "city_summary": response.content,
        "data_source": "vector_store",
    }
