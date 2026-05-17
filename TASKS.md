# VEXHALIA — Development Roadmap

This document tracks the planned work for building the multi-modal agentic travel assistant. Each phase builds on the previous one.

## Phase 1: Foundation & Infrastructure ✅
- [x] Initialize git repository with proper `.gitignore`
- [x] Create `.env.example` with Groq/OpenAI configuration
- [x] Define `requirements.txt` with all dependencies
- [x] Build `config/settings.py` for centralized configuration
- [x] Install and verify all Python packages

## Phase 2: Data Layer ✅
- [x] Define Pydantic schemas (`TravelResponse`, `WeatherDataPoint`, `CityImage`)
- [x] Write rich knowledge base for 4 cities (Chennai, Mumbai, New Jersey, New York)
- [x] Set up ChromaDB vector store with sentence-transformer embeddings
- [x] Implement similarity search and city-known detection

## Phase 3: Tools Layer ✅
- [x] Build Open-Meteo weather tool (geocoding + 7-day forecast + WMO code parsing)
- [x] Build image retrieval tool (curated Wikimedia URLs + picsum placeholders)
- [x] Build DuckDuckGo web search tool with mock fallback
- [x] Add mock mode toggles for all tools

## Phase 4: Agent Nodes (LangGraph Core) ✅
- [x] Define `AgentState` TypedDict with annotated message reducer
- [x] Build router node with conditional edge (vector store vs web search)
- [x] Build vector store retriever node with LLM synthesis
- [x] Build web search node with DuckDuckGo + LLM synthesis
- [x] Build manual tool executor (Distinction 1 — no ToolNode abstraction)
- [x] Build weather fetcher node (parallel-ready)
- [x] Build image fetcher node (parallel-ready)
- [x] Build synthesizer node (structured Pydantic output)
- [x] Assemble complete LangGraph with all edges, parallel fan-out, and MemorySaver

## Phase 5: Streamlit Frontend ✅
- [x] Create `app.py` with professional CSS styling
- [x] Implement city input with follow-up detection
- [x] Add Plotly weather chart (dual-axis: temperature + precipitation)
- [x] Add image gallery with captions
- [x] Add conversation history and session state
- [x] Add sidebar with configuration info and memory controls

## Phase 6: Visualization & Documentation ✅
- [x] Generate `graph.png` from LangGraph topology
- [x] Write `README.md` with architecture explanation
- [x] Create `TASKS.md` (this file — development roadmap)
- [x] Create `PROGRESS.md` (change log)

## Phase 7: Testing & Polish
- [ ] Test known city flow (Chennai, Mumbai)
- [ ] Test unknown city flow (Kyoto, Barcelona)
- [ ] Test follow-up query with memory
- [ ] Verify graph.png renders correctly
- [ ] Push all commits to GitHub
- [ ] Final review of README for clarity
