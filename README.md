# VEXHALIA — Multi-Modal Agentic Travel Intelligence System

A production-ready travel assistant powered by **LangGraph** that aggregates data from multiple sources and renders it into a rich, interactive Streamlit UI. The system intelligently routes between a local vector knowledge base and live web search, fetches real-time weather forecasts, retrieves destination images, and presents everything through structured outputs with interactive charts.

Built as a demonstration of agentic AI architecture — the system doesn't just respond to prompts, it *decides* how to fulfill them.

## Architecture

The agent is built as a **LangGraph StateGraph** with conditional routing, parallel execution, and conversation memory:

![LangGraph Topology](graph.png)

### How It Works

1. **User Input** → The user types a city name or travel query into the Streamlit interface
2. **Router Node** → Queries the ChromaDB vector store to check if the city exists in the local knowledge base
3. **Conditional Edge** → Routes to either:
   - **Vector Retriever** (for known cities: Chennai, Mumbai, New Jersey, New York)
   - **Web Search** (for any other city worldwide via DuckDuckGo)
4. **Parallel Fan-Out** → Weather forecast and image retrieval run **concurrently** (not sequentially)
5. **Synthesizer** → Combines all data into a structured Pydantic response object
6. **Streamlit Renderer** → Parses the JSON to display summary, Plotly chart, and image gallery

### Key Design Decisions

**Why conditional routing instead of always searching the web?**
For cities we have detailed knowledge about, the vector store provides richer, more reliable information than a quick web search. The router checks ChromaDB similarity scores and only falls back to web search when the city is genuinely unknown. This mirrors how a real travel system would work — curated content for popular destinations, dynamic search for everything else.

**Why parallel fan-out for weather and images?**
Weather data and image retrieval are completely independent operations. Running them sequentially would double the latency for no reason. The graph defines both as separate branches from the same parent node, and LangGraph executes them concurrently.

**Why manual tool execution instead of ToolNode?**
To demonstrate understanding of the raw LLM tool-calling protocol. The `tool_executor` node manually parses the `tool_calls` payload from the AI message, looks up functions in a registry dictionary, executes them, and constructs `ToolMessage` objects with matching `tool_call_id` values. No framework abstractions are used.

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Orchestration | LangGraph | Required — provides state management, conditional edges, and parallel execution |
| Frontend | Streamlit | Required — renders the multi-modal response as an interactive GUI |
| LLM | Groq (Llama 3.3 70B) | Free tier with OpenAI-compatible API; project also supports OpenAI GPT-4o and Anthropic Claude 3.5 Sonnet |
| Vector Store | ChromaDB | Persistent embeddings with cosine similarity search and metadata filtering |
| Embeddings | all-MiniLM-L6-v2 | Lightweight sentence transformer, runs on CPU, no API key needed |
| Weather | Open-Meteo API | Free, no API key, global coverage, 16-day forecast |
| Web Search | DuckDuckGo | Free, no API key, worldwide results |
| Charts | Plotly | Interactive line charts with hover details and dual-axis support |

## Project Structure

```
VEXHALIA/
├── app.py                          # Streamlit entry point
├── config/
│   └── settings.py                 # Centralized configuration (env vars, defaults)
├── agents/
│   ├── state.py                    # TypedDict for graph state
│   ├── graph.py                    # LangGraph definition (nodes + edges + memory)
│   └── nodes/
│       ├── router.py               # Conditional routing (vector store vs web)
│       ├── retriever.py            # Vector store retrieval + LLM synthesis
│       ├── web_search.py           # DuckDuckGo search + LLM synthesis
│       ├── tool_executor.py        # Manual tool call parsing (no ToolNode)
│       ├── weather_fetcher.py      # Parallel weather data fetching
│       ├── image_fetcher.py        # Parallel image retrieval
│       └── synthesizer.py          # Final structured output composition
├── tools/
│   ├── weather_tool.py             # Open-Meteo API integration + mock fallback
│   ├── image_tool.py               # Curated Wikimedia URLs + placeholder fallback
│   └── search_tool.py              # DuckDuckGo wrapper + mock fallback
├── data/
│   ├── city_knowledge.py           # Rich knowledge base for 4 cities
│   └── vector_store.py             # ChromaDB initialization and querying
├── models/
│   └── schemas.py                  # Pydantic models (TravelResponse, WeatherDataPoint)
├── utils/
│   └── helpers.py                  # LLM factory, city name extraction, follow-up detection
├── graph.png                       # LangGraph topology visualization
├── requirements.txt                # Pinned dependencies
└── .env.example                    # Environment variable template
```

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- A free Groq API key (get one at [console.groq.com](https://console.groq.com))

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
   Edit `.env` and add your API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`

### Using OpenAI or Anthropic Instead

The project is designed to work with any OpenAI-compatible LLM. To switch providers, update your `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

The `ChatOpenAI` class from LangChain handles both Groq and OpenAI endpoints — only the base URL and model name change.

## Usage

### Basic Query
Type a city name like `Chennai` or `Tell me about Mumbai` and click **Explore**. The agent will:
- Check if the city is in the knowledge base
- Fetch a 7-day weather forecast from Open-Meteo
- Retrieve relevant images
- Display everything in a structured layout

### Follow-Up Queries (Memory)
After asking about a city, try a follow-up like `What about next week?`. The agent preserves context — it knows you're still asking about the same city and only re-fetches the weather data without repeating the city summary.

### Unknown Cities
Ask about any city not in the knowledge base (e.g., `Kyoto`, `Barcelona`, `Snohomish`). The router automatically switches to DuckDuckGo web search and the LLM synthesizes the results.

## Distinction Challenges Implemented

### 1. Manual Tool Execution ("Manual Transmission")
Located in [`agents/nodes/tool_executor.py`](agents/nodes/tool_executor.py). The node:
- Parses the raw `tool_calls` array from the LLM's `AIMessage`
- Looks up each function name in a `TOOL_REGISTRY` dictionary
- Executes the function with the provided arguments
- Wraps results in `ToolMessage` objects with matching `tool_call_id`
- No `ToolNode`, `create_tool_calling_agent`, or any prebuilt abstraction is used

### 2. Parallel Fan-Out
Defined in [`agents/graph.py`](agents/graph.py). After the city summary is obtained, the graph branches into two independent nodes:
- `fetch_weather` — calls the Open-Meteo API
- `fetch_images` — retrieves curated or placeholder images

Both edges originate from the same parent node and converge at the `synthesizer`. LangGraph executes them concurrently, reducing total latency.

### 3. Human-in-the-Loop & Memory (Time Travel)
Implemented via `MemorySaver` checkpointer in [`agents/graph.py`](agents/graph.py). Each conversation is assigned a `thread_id`, and the checkpointer preserves the full state between invocations. Follow-up detection logic in [`utils/helpers.py`](utils/helpers.py) identifies when a user references time changes without naming a new city, triggering only the weather update path.

## Mock Mode

If API keys are unavailable or you want to test offline, enable mock mode in `.env`:

```env
USE_MOCK_WEATHER=true
USE_MOCK_IMAGES=true
USE_MOCK_SEARCH=true
```

Mock functions return realistic, structured data so the full agent pipeline executes end-to-end. The assignment specification explicitly permits this approach.

## License

This project was built as a technical assessment submission. All code is original.
