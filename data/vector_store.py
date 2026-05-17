"""
ChromaDB vector store setup and querying.

On first run, this module creates a persistent ChromaDB collection and
populates it with the city knowledge chunks. On subsequent runs it
detects the existing collection and skips re-indexing, so startup is
fast after the initial embedding pass.

Each document is stored with category metadata (e.g., "food", "weather",
"attractions") enabling both semantic search and filtered retrieval.
"""

import chromadb
from chromadb.utils import embedding_functions

from config.settings import settings
from data.city_knowledge import get_all_chunks, get_city_names


def _get_embedding_function():
    """Build the sentence-transformer embedding function for ChromaDB.

    Using all-MiniLM-L6-v2 because it is lightweight (~80 MB), runs on
    CPU without issues, and produces 384-dimensional embeddings that
    are plenty accurate for our small knowledge base.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.EMBEDDING_MODEL
    )


def initialize_vector_store() -> chromadb.Collection:
    """Create or load the ChromaDB collection.

    If the collection already contains documents, we skip the embedding
    step entirely to avoid redundant computation on every restart.
    """
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    embed_fn = _get_embedding_function()

    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Only populate if the collection is empty (first run)
    if collection.count() == 0:
        chunks = get_all_chunks()  # list of (city_name, text, category)
        documents = [text for _, text, _ in chunks]
        metadatas = [
            {"city": city, "category": category}
            for city, _, category in chunks
        ]
        ids = [
            f"{city.lower().replace(' ', '_')}_{category}_{i}"
            for i, (city, _, category) in enumerate(chunks)
        ]

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    return collection


def query_vector_store(
    collection: chromadb.Collection,
    query: str,
    top_k: int = 4,
    category_filter: str | None = None,
) -> tuple[list[str], list[dict], list[float]]:
    """Search the vector store for chunks relevant to the query.

    Parameters:
        collection: The ChromaDB collection to search.
        query: The search query text.
        top_k: Number of results to return.
        category_filter: Optional — only return chunks matching this
            category (e.g., "food", "weather", "attractions").

    Returns:
        documents: The matching text chunks.
        metadatas: Metadata dicts (each has 'city' and 'category' keys).
        distances: Cosine distances — lower is more similar.
    """
    query_params = {
        "query_texts": [query],
        "n_results": top_k,
    }

    if category_filter:
        query_params["where"] = {"category": category_filter}

    results = collection.query(**query_params)
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []
    return documents, metadatas, distances


def is_city_known(
    collection: chromadb.Collection,
    city_name: str,
) -> tuple[bool, list[str]]:
    """Check whether the vector store has meaningful knowledge about a city.

    We query with just the city name and look at the top result's distance.
    If it is below SIMILARITY_THRESHOLD, we consider the city 'known' and
    return the relevant chunks. Otherwise the agent should fall back to
    web search.

    Returns:
        (is_known, relevant_chunks)
    """
    documents, metadatas, distances = query_vector_store(
        collection, city_name, top_k=6
    )

    if not distances:
        return False, []

    # Filter results that are actually about this city
    # (the query might return chunks from other cities too)
    relevant = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        # Cosine distance: 0 = identical, 2 = opposite
        if dist < settings.SIMILARITY_THRESHOLD:
            relevant.append(doc)

    is_known = len(relevant) >= 2  # need at least 2 relevant chunks
    return is_known, relevant
