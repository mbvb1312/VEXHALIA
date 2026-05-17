"""
VEXHALIA — Multi-Modal Agentic Travel Intelligence System

ChatGPT-style conversational interface powered by Streamlit.
The input box stays at the bottom of the screen, messages scroll
upward, and rich media (weather charts, images) are embedded
inline within assistant responses.

Run with: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import uuid

from config.settings import settings
from utils.helpers import extract_city_name, is_follow_up_query
from agents.graph import run_travel_query


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="VEXHALIA — Travel Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Premium CSS — dark theme with glassmorphism accents
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Root variables */
    :root {
        --primary: #7c3aed;
        --primary-soft: rgba(124, 58, 237, 0.15);
        --accent: #f43f5e;
        --bg-dark: #0f172a;
        --bg-card: rgba(30, 41, 59, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --border-subtle: rgba(148, 163, 184, 0.12);
        --success: #10b981;
        --info: #3b82f6;
    }

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container */
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 6rem;
        max-width: 1100px;
    }

    /* Hide Streamlit header/footer clutter */
    header[data-testid="stHeader"] {
        background: var(--bg-dark);
        border-bottom: 1px solid var(--border-subtle);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }

    /* ---- Chat messages ---- */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid var(--border-subtle);
        backdrop-filter: blur(10px);
    }

    /* ---- Chat input ---- */
    [data-testid="stChatInput"] {
        border-top: 1px solid var(--border-subtle);
    }
    [data-testid="stChatInput"] textarea {
        font-size: 1rem;
        border-radius: 12px;
    }

    /* ---- Source badge styling ---- */
    .vex-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-bottom: 0.6rem;
    }
    .vex-badge-vector {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .vex-badge-web {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* ---- Summary card ---- */
    .vex-summary {
        background: rgba(15, 23, 42, 0.6);
        border-left: 3px solid var(--primary);
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.4rem;
        margin: 0.8rem 0 1rem 0;
        line-height: 1.7;
        color: #e2e8f0;
        font-size: 0.95rem;
    }

    /* ---- Image gallery ---- */
    .vex-gallery-caption {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.78rem;
        margin-top: 4px;
        font-style: italic;
        line-height: 1.3;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    /* ---- Header branding ---- */
    .vex-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .vex-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #7c3aed, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .vex-header p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    /* Plotly chart container */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Session State Initialization
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_city" not in st.session_state:
    st.session_state.last_city = None


# ============================================================
# Sidebar — compact config panel
# ============================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    llm_cfg = settings.get_llm_config()
    provider_name = "Groq (Llama 3.3 70B)" if settings.LLM_PROVIDER == "groq" else "OpenAI (GPT-4o)"
    st.info(f"**LLM:** {provider_name}")

    warnings = settings.validate()
    if warnings:
        for w in warnings:
            st.warning(w)

    st.markdown("---")

    st.markdown("### 🏙️ Pre-loaded Cities")
    st.caption(
        "Chennai · Mumbai · New Jersey · New York\n\n"
        "Other cities are searched via the web."
    )

    st.markdown("---")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.session_state.last_city = None
        st.rerun()

    st.markdown("---")
    st.caption(
        "Built with LangGraph, Streamlit, and Groq.\n"
        "Compatible with OpenAI GPT-4o & Claude 3.5 Sonnet."
    )


# ============================================================
# Header — only shown when chat is empty
# ============================================================

if not st.session_state.chat_history:
    st.markdown("""
    <div class="vex-header">
        <h1>🌍 VEXHALIA</h1>
        <p>Multi-Modal Agentic Travel Intelligence — ask about any city</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Suggestion chips
    cols = st.columns(4)
    suggestions = ["Tell me about Chennai", "Explore New York", "Mumbai travel guide", "What's Kyoto like?"]
    for col, suggestion in zip(cols, suggestions):
        with col:
            if st.button(suggestion, key=f"sug_{suggestion}", use_container_width=True):
                st.session_state.pending_query = suggestion
                st.rerun()


# ============================================================
# Helper: Build weather chart
# ============================================================

def build_weather_chart(weather_data: list[dict]) -> go.Figure:
    """Create a Plotly chart from weather forecast data."""
    dates = [w.get("date", f"Day {i+1}") for i, w in enumerate(weather_data)]
    highs = [w.get("temperature_high", 0) for w in weather_data]
    lows = [w.get("temperature_low", 0) for w in weather_data]
    precip = [w.get("precipitation_chance", 0) for w in weather_data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=highs,
        mode="lines+markers",
        name="High (°C)",
        line=dict(color="#ef4444", width=2.5),
        marker=dict(size=7),
        hovertemplate="%{x}<br>High: %{y}°C<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=lows,
        mode="lines+markers",
        name="Low (°C)",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=7),
        hovertemplate="%{x}<br>Low: %{y}°C<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=dates, y=precip,
        name="Rain %",
        marker_color="rgba(59, 130, 246, 0.2)",
        yaxis="y2",
        hovertemplate="%{x}<br>Rain: %{y}%<extra></extra>",
    ))

    fig.update_layout(
        xaxis_title="Date",
        yaxis=dict(title="Temperature (°C)", side="left"),
        yaxis2=dict(
            title="Precipitation (%)",
            side="right",
            overlaying="y",
            range=[0, 100],
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        height=350,
        margin=dict(l=40, r=40, t=25, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


# ============================================================
# Helper: Render a single assistant response
# ============================================================

def render_assistant_response(result: dict):
    """Render the full multi-modal response inside a chat message."""
    city = result.get("city_name", "Unknown")
    summary = result.get("city_summary", "")
    weather = result.get("weather_forecast", [])
    images = result.get("images", [])
    image_urls = result.get("image_urls", [])
    source = result.get("data_source", "unknown")
    error = result.get("error")

    # Source badge
    if source == "vector_store":
        st.markdown(
            '<span class="vex-badge vex-badge-vector">📚 Knowledge Base</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="vex-badge vex-badge-web">🌐 Web Search</span>',
            unsafe_allow_html=True,
        )

    # City name heading
    st.markdown(f"### 🏙️ {city}")

    # Summary card
    if summary:
        st.markdown(
            f'<div class="vex-summary">{summary}</div>',
            unsafe_allow_html=True,
        )

    # Two-column layout: left = visuals, right = weather details
    if weather or images or image_urls:
        vis_col, detail_col = st.columns([3, 2])

        with vis_col:
            # Weather chart
            if weather:
                st.markdown("#### 🌤️ Weather Forecast")
                fig = build_weather_chart(weather)
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{city}_{len(st.session_state.chat_history)}")

            # Image gallery
            display_images = images if images else [{"url": u, "caption": ""} for u in image_urls]
            if display_images:
                st.markdown("#### 📸 Gallery")
                img_cols = st.columns(min(len(display_images), 3))
                for i, img_data in enumerate(display_images[:6]):
                    with img_cols[i % len(img_cols)]:
                        img_url = img_data.get("url", "") if isinstance(img_data, dict) else img_data.url
                        caption = img_data.get("caption", "") if isinstance(img_data, dict) else img_data.caption
                        try:
                            st.image(img_url, use_container_width=True)
                            if caption:
                                st.markdown(
                                    f'<p class="vex-gallery-caption">{caption}</p>',
                                    unsafe_allow_html=True,
                                )
                        except Exception:
                            st.caption(f"📷 {caption or 'Image unavailable'}")

        with detail_col:
            # Weather detail cards
            if weather:
                st.markdown("#### 📋 Daily Conditions")
                for w in weather:
                    date_str = w.get("date", "N/A")
                    cond = w.get("condition", "—")
                    high = w.get("temperature_high", "—")
                    low = w.get("temperature_low", "—")
                    rain = w.get("precipitation_chance", 0)

                    st.markdown(
                        f"**{date_str}** — {cond}  \n"
                        f"🌡️ {high}°C / {low}°C &nbsp; 🌧️ {rain}%"
                    )

    # Error display
    if error:
        st.warning(f"⚠️ {error}")


# ============================================================
# Render Chat History
# ============================================================

for entry in st.session_state.chat_history:
    if entry["role"] == "user":
        with st.chat_message("user"):
            st.markdown(entry["content"])
    else:
        with st.chat_message("assistant", avatar="🌍"):
            render_assistant_response(entry["result"])


# ============================================================
# Chat Input — pinned at the bottom by Streamlit
# ============================================================

# Check for pending query from suggestion buttons
pending = st.session_state.pop("pending_query", None)
prompt = st.chat_input("Ask about any city — e.g. 'Tell me about Chennai' or 'What about next week?'")

# Use whichever input source is available
user_input = pending or prompt

if user_input:
    # Detect follow-up vs. new query
    follow_up = is_follow_up_query(user_input)

    if follow_up and st.session_state.last_city:
        city_name = st.session_state.last_city
    else:
        city_name = extract_city_name(user_input)
        follow_up = False

    if not city_name:
        with st.chat_message("assistant", avatar="🌍"):
            st.warning("Please enter a valid city name to explore.")
    else:
        # Add user message to history and render it
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
        })
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build the previous result for follow-ups
        existing_state = None
        if follow_up:
            prev_assistant_msgs = [
                e for e in st.session_state.chat_history if e["role"] == "assistant"
            ]
            if prev_assistant_msgs:
                existing_state = prev_assistant_msgs[-1].get("result")

        # Run agent and render response
        with st.chat_message("assistant", avatar="🌍"):
            with st.spinner(f"🔍 Exploring {city_name}..."):
                try:
                    result = run_travel_query(
                        user_input=user_input,
                        city_name=city_name,
                        is_follow_up=follow_up,
                        thread_id=st.session_state.thread_id,
                        existing_state=existing_state,
                    )

                    st.session_state.last_city = city_name

                    # Store result in chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "result": result,
                    })

                    render_assistant_response(result)

                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")
                    st.caption(
                        "Check your API key in `.env`, ensure internet "
                        "connectivity, or try a different city."
                    )
