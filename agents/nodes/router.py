"""
Router node — the intelligent 'switch' that decides where to fetch city info.

This is the conditional edge the assignment specifically requires: the agent
must NOT simply web-search everything. It queries the vector store first and
only falls back to web search when the city is not in our knowledge base.
"""

from agents.state import AgentState
from data.vector_store import initialize_vector_store, is_city_known


# Cache the collection reference so we don't re-initialize on every call
_collection = None


def get_collection():
    """Lazy-load the ChromaDB collection (only once per process)."""
    global _collection
    if _collection is None:
        _collection = initialize_vector_store()
    return _collection


def router_node(state: AgentState) -> AgentState:
    """Determine whether the city exists in the vector store.

    This node does not modify the messages — it only sets data_source
    so the conditional edge can route to the correct downstream node.
    """
    city = state.get("city_name", "")
    if not city:
        return {**state, "data_source": "web_search", "error": "No city name provided"}

    collection = get_collection()
    known, relevant_chunks = is_city_known(collection, city)

    if known:
        return {**state, "data_source": "vector_store"}
    else:
        return {**state, "data_source": "web_search"}


def route_decision(state: AgentState) -> str:
    """Conditional edge function: returns the name of the next node.

    Called by LangGraph's add_conditional_edges to decide which path
    to take after the router node runs.
    """
    # If this is a follow-up query (e.g., "what about next week?"),
    # skip straight to data fetching — we already have the city summary
    if state.get("is_follow_up", False):
        return "fetch_data"

    source = state.get("data_source", "web_search")
    if source == "vector_store":
        return "retrieve_from_store"
    return "search_web"
