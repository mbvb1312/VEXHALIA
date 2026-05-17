# VEXHALIA — Progress Log

Chronological record of development work, decisions made, and changes applied.

---

## Session 1 — 2026-05-18

### Work Completed

**Phase 1: Foundation**
- Initialized the project with `.gitignore`, `.env.example`, `requirements.txt`
- Built `config/settings.py` with provider switching (Groq free tier as default, OpenAI/Anthropic as premium options)
- Chose Groq's Llama 3.3 70B as the default LLM because it is free (30 req/min, 14,400 req/day) and uses the same OpenAI-compatible API format, making provider switching trivial

**Phase 2: Data Layer**
- Created Pydantic schemas: `TravelResponse`, `WeatherDataPoint`, `CityImage`
- Wrote detailed knowledge base for 4 cities: Chennai, Mumbai, New Jersey, New York
  - Each city has 6 text chunks covering history, landmarks, food, transport, weather, and culture
  - Chunks are kept under 200 words for optimal embedding quality
- Set up ChromaDB with `all-MiniLM-L6-v2` embeddings and cosine similarity
  - Lazy initialization: only embeds on first run, skips on subsequent runs
  - City-known detection uses a similarity threshold (0.35) and requires at least 2 relevant chunks

**Phase 3: Tools Layer**
- Weather: Open-Meteo API (free, no API key, global, 16-day forecast)
  - Geocoding endpoint converts city names to lat/lon
  - WMO weather codes mapped to human-readable conditions
  - Mock fallback generates city-specific data using name hash
- Images: Curated Wikimedia Commons URLs for known cities, picsum.photos placeholders for unknown
- Search: DuckDuckGo via `duckduckgo-search` package, mock fallback with realistic structured results

**Phase 4: Agent Graph**
- Built all 7 nodes: router, retriever, web_search, tool_executor, weather_fetcher, image_fetcher, synthesizer
- Implemented all 3 distinction challenges:
  1. Manual tool execution — parses raw `tool_calls`, no `ToolNode`
  2. Parallel fan-out — weather and images run concurrently
  3. MemorySaver checkpointer — preserves context for follow-up queries
- Graph compiles successfully with 8 nodes (including __start__ and __end__)

**Phase 5: Streamlit Frontend**
- Built `app.py` with custom CSS, Plotly weather chart, image gallery, conversation history
- Dual-axis chart: temperature lines (°C) + precipitation bars (%)
- Data source badge shows whether info came from vector store or web search
- Follow-up detection for memory-based queries

**Phase 6: Documentation**
- Generated `graph.png` from LangGraph topology
- Wrote comprehensive `README.md` with architecture, setup, and distinction challenge details
- Created `TASKS.md` (roadmap) and `PROGRESS.md` (this file)

### Decisions Made

| Decision | Rationale |
|----------|-----------|
| Groq over OpenAI as default | Free tier sufficient for development and demos; same API format makes switching trivial |
| Open-Meteo over OpenWeatherMap | No API key needed, free forever, better forecast range (16 days) |
| ChromaDB over FAISS | Better metadata filtering, built-in persistence, cleaner LangGraph integration |
| Wikimedia Commons over Unsplash | No API key needed, real high-quality photographs, reliable URLs |
| 4 cities (2 India + 2 USA) | Demonstrates global coverage without geographic bias |

### Git Commits
1. `init: project scaffold with config and dependencies`
2. `feat: define pydantic schemas and data models`
3. `feat: build city knowledge base and ChromaDB vector store`
4. `feat: implement weather, image, and search tools with mock fallbacks`
5. `feat: complete langgraph agent with routing, parallel fan-out, manual tool execution, and memory`
6. `feat: streamlit frontend with interactive weather chart and image gallery`
