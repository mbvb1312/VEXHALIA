---
title: VEXHALIA
emoji: 🌍
colorFrom: purple
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---

# VEXHALIA — Multi-Modal Agentic Travel Intelligence System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-7c3aed?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-10b981?style=for-the-badge)](https://www.trychroma.com/)

**A production-ready travel assistant powered by LangGraph that aggregates data from multiple sources and renders it into a rich, interactive Streamlit UI.**

*The system doesn't just respond to prompts — it **decides** how to fulfill them.*

</div>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🧠 **Agentic Routing** | Intelligent routing between local vector store and live web search based on query similarity |
| 🌤️ **16-Day Forecast** | Real-time weather data from Open-Meteo API with interactive Plotly charts |
| 📸 **Live Image Search** | Real destination photos fetched from DuckDuckGo image search |
| 📚 **Wikipedia Integration** | Rich factual context from Wikipedia API enriches every response |
| 💬 **Conversational AI** | ChatGPT-style responses — the agent reasons about weather data to give actionable advice |
| 🔄 **Auto-Fallback LLM** | Gemini primary → Groq automatic failover for 24/7 availability |
| 🧩 **Follow-Up Memory** | Context-aware follow-ups ("What about next week?") without re-explaining the city |
| ⚡ **Parallel Execution** | Weather + Image fetching runs concurrently via LangGraph fan-out |

---

## 🏗️ Architecture

The agent is built as a **LangGraph StateGraph** with conditional routing, parallel execution, and conversation memory:

### System Architecture

![System Architecture](architecture.png)

### LangGraph Topology

![LangGraph Topology](graph.png)

### How It Works

1. **User Input** → The user types a city name or travel query into the Streamlit chat interface
2. **Router Node** → Queries the ChromaDB vector store to check if the city exists in the local knowledge base
3. **Conditional Edge** → Routes to either:
   - **Vector Retriever** (for known cities: Paris, Tokyo, New York) + **Wikipedia enrichment**
   - **Web Search** (for any other city worldwide via DuckDuckGo) + **Wikipedia enrichment**
4. **Parallel Fan-Out** → Weather forecast and image retrieval run **concurrently** (not sequentially)
5. **Synthesizer** → Combines all data and uses the LLM to generate a conversational, contextual response
6. **Streamlit Renderer** → Parses the structured output to display summary, Plotly chart, and image gallery

### Key Design Decisions

<details>
<summary><strong>Why conditional routing instead of always searching the web?</strong></summary>
<br>
For cities we have detailed knowledge about, the vector store provides richer, more reliable information than a quick web search. The router checks ChromaDB similarity scores and only falls back to web search when the city is genuinely unknown. This mirrors how a real travel system would work — curated content for popular destinations, dynamic search for everything else.
</details>

<details>
<summary><strong>Why parallel fan-out for weather and images?</strong></summary>
<br>
Weather data and image retrieval are completely independent operations. Running them sequentially would double the latency for no reason. The graph defines both as separate branches from the same parent node, and LangGraph executes them concurrently.
</details>

<details>
<summary><strong>Why manual tool execution instead of ToolNode?</strong></summary>
<br>
To demonstrate understanding of the raw LLM tool-calling protocol. The <code>tool_executor</code> node manually parses the <code>tool_calls</code> payload from the AI message, looks up functions in a registry dictionary, executes them, and constructs <code>ToolMessage</code> objects with matching <code>tool_call_id</code> values. No framework abstractions are used.
</details>

---

## 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Orchestration | LangGraph | State management, conditional edges, and parallel execution |
| Frontend | Streamlit | Interactive GUI with charts, images, and chat interface |
| Primary LLM | Gemini (2.0 Flash) | Free tier via Google API; intelligent reasoning for follow-ups |
| Fallback LLM | Groq (Llama 3.3 70B) | Automatic fallback using `.with_fallbacks()` for rate-limit resilience |
| Vector Store | ChromaDB | Persistent embeddings with cosine similarity search and category metadata |
| Embeddings | all-MiniLM-L6-v2 | Lightweight sentence transformer, runs on CPU, no API key needed |
| Weather | Open-Meteo API | Free, no API key, global coverage, 16-day forecast |
| Web Search | DuckDuckGo | Free, no API key, worldwide results |
| Knowledge | Wikipedia API | Enriched factual summaries alongside search/vector results |
| Charts | Plotly | Interactive line charts with hover details and dual-axis support |

---

## 📁 Project Structure

```
VEXHALIA/
├── app.py                          # Streamlit entry point — chat UI
├── .streamlit/
│   └── config.toml                 # Streamlit server configuration
├── config/
│   └── settings.py                 # Centralized configuration (env vars, defaults)
├── agents/
│   ├── state.py                    # TypedDict for graph state
│   ├── graph.py                    # LangGraph definition (nodes + edges + memory)
│   └── nodes/
│       ├── router.py               # Conditional routing (vector store vs web)
│       ├── retriever.py            # Vector store retrieval + Wikipedia + LLM synthesis
│       ├── web_search.py           # DuckDuckGo + Wikipedia + LLM synthesis
│       ├── tool_executor.py        # Manual tool call parsing (no ToolNode)
│       ├── weather_fetcher.py      # Parallel weather data fetching
│       ├── image_fetcher.py        # Parallel image retrieval
│       └── synthesizer.py          # Final structured output with weather reasoning
├── tools/
│   ├── weather_tool.py             # Open-Meteo API integration + mock fallback
│   ├── image_tool.py               # DuckDuckGo image search + fallback
│   ├── search_tool.py              # DuckDuckGo text search + mock fallback
│   └── wikipedia_tool.py           # Wikipedia API for knowledge enrichment
├── data/
│   ├── city_knowledge.py           # Rich knowledge base for Paris, Tokyo, New York
│   └── vector_store.py             # ChromaDB initialization with category metadata
├── models/
│   └── schemas.py                  # Pydantic models (TravelResponse, WeatherDataPoint)
├── utils/
│   └── helpers.py                  # LLM factory with fallback, city extraction, follow-up detection
├── graph.png                       # LangGraph topology (auto-generated from code)
├── requirements.txt                # Pinned dependencies
└── .env.example                    # Environment variable template
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10 or higher
- A free Google Gemini API key ([aistudio.google.com](https://aistudio.google.com))
- A free Groq API key for fallback ([console.groq.com](https://console.groq.com))

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/mbvb1312/VEXHALIA.git
   cd VEXHALIA
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys:
   ```env
   LLM_PROVIDER=gemini
   GOOGLE_API_KEY=your_gemini_key_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`

---

## 🔄 High-Availability LLM Routing (Auto-Fallback)

```
User Query → Gemini (primary, high quality)
                ↓ if rate-limited or error
             Groq (automatic fallback, free tier)
```

The system uses **Google Gemini** as the primary intelligence engine. Because free-tier API keys have hourly rate limits, the `get_llm()` helper implements a robust fallback strategy using LangChain's `.with_fallbacks([fallback])`.

If Gemini throws a rate limit or service error, the system **automatically and seamlessly fails over to Groq (Llama 3.3 70B)** without crashing or exposing errors to the user. This ensures 24/7 availability for the travel assistant.

The project is also fully compatible with **OpenAI GPT-4o** and **Anthropic Claude 3.5 Sonnet** — simply change `LLM_PROVIDER` in `.env`.

---

## 💬 Usage

### Basic Query
Type a city name like `Paris` or `Tell me about Tokyo` and press Enter. The agent will:
- Check if the city is in the knowledge base (or fall back to Web + Wikipedia)
- Fetch a **16-day weather forecast** from Open-Meteo
- Retrieve relevant destination images
- Display everything in a structured layout with conversational AI synthesis

### Follow-Up Queries (Memory)
After asking about a city, try a follow-up like `What about next week?` or `Is it good for boating?`. The agent preserves context — it knows you're still asking about the same city and uses **weather data reasoning** to give actionable advice (e.g., checking rain probability before recommending outdoor activities).

### Unknown Cities
Ask about any city not in the knowledge base (e.g., `Kyoto`, `Barcelona`, `Snohomish`). The router automatically switches to DuckDuckGo web search + Wikipedia and the LLM synthesizes the results.

---

## 🏆 Distinction Challenges Implemented

### 1. Manual Tool Execution ("Manual Transmission")
Located in [`agents/nodes/tool_executor.py`](agents/nodes/tool_executor.py). The node:
- Parses the raw `tool_calls` array from the LLM's `AIMessage`
- Looks up each function name in a `TOOL_REGISTRY` dictionary
- Executes the function with the provided arguments
- Wraps results in `ToolMessage` objects with matching `tool_call_id`
- **No `ToolNode`, `create_tool_calling_agent`, or any prebuilt abstraction is used**

### 2. Parallel Fan-Out
Defined in [`agents/graph.py`](agents/graph.py). After the city summary is obtained, the graph branches into two independent nodes:
- `fetch_weather` — calls the Open-Meteo API (16-day forecast)
- `fetch_images` — retrieves destination photos via DuckDuckGo

Both edges originate from the same parent node and converge at the `synthesizer`. LangGraph executes them concurrently, reducing total latency.

### 3. Human-in-the-Loop & Memory (Time Travel)
Implemented via `MemorySaver` checkpointer in [`agents/graph.py`](agents/graph.py). Each conversation is assigned a `thread_id`, and the checkpointer preserves the full state between invocations. Follow-up detection logic in [`utils/helpers.py`](utils/helpers.py) identifies when a user references time changes without naming a new city.

---

## ☁️ Deployment (Hugging Face Spaces)

### Step-by-Step Deployment

1. **Create a Hugging Face account** at [huggingface.co](https://huggingface.co)

2. **Create a new Space**
   - Go to [huggingface.co/new-space](https://huggingface.co/new-space)
   - Name: `VEXHALIA`
   - SDK: **Streamlit**
   - Visibility: **Public**

3. **Add secrets** (in Space Settings → Repository secrets):
   ```
   GOOGLE_API_KEY = your_gemini_key
   GROQ_API_KEY = your_groq_key
   LLM_PROVIDER = gemini
   ```

4. **Push your code to the Space**
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/VEXHALIA
   git push hf main
   ```

5. **Wait for build** — Hugging Face will install dependencies from `requirements.txt` and launch the Streamlit app automatically.

6. **Access your live app** at:
   ```
   https://YOUR_USERNAME-vexhalia.hf.space
   ```

> **Note:** The free tier on Hugging Face Spaces provides a persistent URL that stays online 24/7. The app may cold-start after periods of inactivity (~30 seconds).

---

## 🧪 Mock Mode

If API keys are unavailable or you want to test offline, enable mock mode in `.env`:

```env
USE_MOCK_WEATHER=true
USE_MOCK_IMAGES=true
USE_MOCK_SEARCH=true
```

Mock functions return realistic, structured data so the full agent pipeline executes end-to-end.

---

## 📄 License

This project was built as a technical assessment submission. All code is original.
