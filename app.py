"""
VEXHALIA — Multi-Modal Agentic Travel Intelligence System

Streamlit frontend that provides an interactive UI for the LangGraph-powered
travel assistant. Users enter a city name and receive a rich, multi-modal
response with a text summary, weather forecast chart, and image gallery.

This is the main entry point: run with `streamlit run app.py`
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
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom CSS for a polished look
# ============================================================

st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: #888;
        font-size: 1.05rem;
    }

    /* City summary card */
    .summary-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }

    /* Data source badge */
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .source-vector {
        background-color: #d4edda;
        color: #155724;
    }

    .source-web {
        background-color: #cce5ff;
        color: #004085;
    }

    /* Image gallery grid */
    .image-caption {
        text-align: center;
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.3rem;
        font-style: italic;
    }

    /* Error styling */
    .error-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Session State Initialization
# ============================================================

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_city" not in st.session_state:
    st.session_state.last_city = None


# ============================================================
# Sidebar — Configuration & Info
# ============================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # LLM Provider display
    llm_cfg = settings.get_llm_config()
    provider_name = "Groq (Llama 3.3 70B)" if settings.LLM_PROVIDER == "groq" else "OpenAI (GPT-4o)"
    st.info(f"**LLM Provider:** {provider_name}")

    # Validate API key
    warnings = settings.validate()
    if warnings:
        for w in warnings:
            st.warning(w)

    st.markdown("---")

    st.markdown("### 📊 About VEXHALIA")
    st.markdown(
        "A multi-modal agentic travel assistant powered by LangGraph. "
        "Ask about any city and get an AI-generated summary, weather "
        "forecast, and image gallery."
    )

    st.markdown("---")

    st.markdown("### 🏙️ Pre-loaded Cities")
    st.markdown(
        "Detailed knowledge is available for:\n"
        "- 🇮🇳 **Chennai**\n"
        "- 🇮🇳 **Mumbai**\n"
        "- 🇺🇸 **New Jersey**\n"
        "- 🇺🇸 **New York**\n\n"
        "Any other city will be searched via the web."
    )

    st.markdown("---")

    st.markdown("### 🔄 Conversation Memory")
    st.markdown(
        "This assistant remembers context. Try asking about a city, "
        "then follow up with *'what about next week?'* — it will "
        "update only the weather forecast."
    )

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.conversation_history = []
        st.session_state.last_result = None
        st.session_state.last_city = None
        st.rerun()


# ============================================================
# Main Content Area
# ============================================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🌍 VEXHALIA</h1>
    <p>Multi-Modal Agentic Travel Intelligence System</p>
</div>
""", unsafe_allow_html=True)

# Input Section
col_input, col_button = st.columns([4, 1])

with col_input:
    user_input = st.text_input(
        "Where would you like to explore?",
        placeholder="e.g., 'Tell me about Chennai' or 'Mumbai' or 'Kyoto'...",
        label_visibility="collapsed",
        key="city_input",
    )

with col_button:
    search_clicked = st.button("🔍 Explore", type="primary", use_container_width=True)


# ============================================================
# Process Query
# ============================================================

if search_clicked and user_input.strip():
    # Detect if this is a follow-up query
    follow_up = is_follow_up_query(user_input)

    if follow_up and st.session_state.last_city:
        city_name = st.session_state.last_city
        st.info(f"🔄 Follow-up detected — updating data for **{city_name}**")
    else:
        city_name = extract_city_name(user_input)
        follow_up = False  # new city = not a follow-up

    if not city_name:
        st.warning("Please enter a valid city name to explore.")
    else:
        # Store in conversation history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input,
        })

        # Run the agent graph
        with st.spinner(f"🌐 Exploring {city_name}... Fetching data from multiple sources..."):
            try:
                result = run_travel_query(
                    user_input=user_input,
                    city_name=city_name,
                    is_follow_up=follow_up,
                    thread_id=st.session_state.thread_id,
                    existing_state=st.session_state.last_result,
                )

                st.session_state.last_result = result
                st.session_state.last_city = city_name
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": result.get("city_summary", ""),
                })

            except Exception as e:
                st.error(f"An error occurred while processing your query: {str(e)}")
                st.info(
                    "**Troubleshooting tips:**\n"
                    "- Check that your API key is set in the `.env` file\n"
                    "- Ensure you have internet connectivity\n"
                    "- Try a different city name"
                )
                result = None


# ============================================================
# Display Results
# ============================================================

result = st.session_state.last_result

if result:
    city = result.get("city_name", "Unknown")
    summary = result.get("city_summary", "")
    weather = result.get("weather_forecast", [])
    image_urls = result.get("image_urls", [])
    images = result.get("images", [])
    source = result.get("data_source", "unknown")

    # ---- Data Source Badge ----
    badge_class = "source-vector" if source == "vector_store" else "source-web"
    badge_text = "📚 Knowledge Base" if source == "vector_store" else "🌐 Web Search"
    st.markdown(
        f'<span class="source-badge {badge_class}">{badge_text}</span>',
        unsafe_allow_html=True,
    )

    # ---- City Summary ----
    st.markdown(f"## 🏙️ {city}")
    st.markdown(f'<div class="summary-card">{summary}</div>', unsafe_allow_html=True)

    # ---- Weather Forecast Chart ----
    if weather:
        st.markdown("---")
        st.markdown("## 🌤️ 7-Day Weather Forecast")

        # Build Plotly chart
        dates = [w.get("date", f"Day {i+1}") for i, w in enumerate(weather)]
        highs = [w.get("temperature_high", 0) for w in weather]
        lows = [w.get("temperature_low", 0) for w in weather]
        precip = [w.get("precipitation_chance", 0) for w in weather]
        conditions = [w.get("condition", "N/A") for w in weather]

        fig = go.Figure()

        # High temperature line
        fig.add_trace(go.Scatter(
            x=dates, y=highs,
            mode="lines+markers",
            name="High (°C)",
            line=dict(color="#ef5350", width=3),
            marker=dict(size=8),
            hovertemplate="%{x}<br>High: %{y}°C<extra></extra>",
        ))

        # Low temperature line
        fig.add_trace(go.Scatter(
            x=dates, y=lows,
            mode="lines+markers",
            name="Low (°C)",
            line=dict(color="#42a5f5", width=3),
            marker=dict(size=8),
            hovertemplate="%{x}<br>Low: %{y}°C<extra></extra>",
        ))

        # Precipitation chance as bar chart on secondary axis
        fig.add_trace(go.Bar(
            x=dates, y=precip,
            name="Rain Chance (%)",
            marker_color="rgba(100, 181, 246, 0.3)",
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
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            template="plotly_white",
            height=400,
            margin=dict(l=50, r=50, t=30, b=50),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Weather conditions table
        with st.expander("📋 Detailed Daily Conditions"):
            col_headers = st.columns(len(weather))
            for i, (col, w) in enumerate(zip(col_headers, weather)):
                with col:
                    st.markdown(f"**{dates[i]}**")
                    st.caption(conditions[i])
                    st.metric(
                        label="High / Low",
                        value=f"{highs[i]}°C",
                        delta=f"{lows[i]}°C low",
                    )

    # ---- Image Gallery ----
    if images or image_urls:
        st.markdown("---")
        st.markdown("## 📸 Photo Gallery")

        display_images = images if images else [{"url": u, "caption": ""} for u in image_urls]

        cols = st.columns(min(len(display_images), 4))
        for i, img_data in enumerate(display_images):
            with cols[i % len(cols)]:
                img_url = img_data.get("url", "") if isinstance(img_data, dict) else img_data.url
                caption = img_data.get("caption", "") if isinstance(img_data, dict) else img_data.caption
                st.image(img_url, use_container_width=True)
                if caption:
                    st.markdown(f'<p class="image-caption">{caption}</p>', unsafe_allow_html=True)

    # ---- Error Display ----
    error = result.get("error")
    if error:
        st.markdown(
            f'<div class="error-box">⚠️ <strong>Note:</strong> {error}</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# Conversation History (expandable)
# ============================================================

if st.session_state.conversation_history:
    with st.expander("💬 Conversation History"):
        for msg in st.session_state.conversation_history:
            role = "🧑 You" if msg["role"] == "user" else "🤖 VEXHALIA"
            st.markdown(f"**{role}:** {msg['content'][:500]}")


# ============================================================
# Footer
# ============================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.85rem;'>"
    "VEXHALIA — Built with LangGraph, Streamlit, and Groq | "
    "Compatible with OpenAI GPT-4o & Anthropic Claude 3.5 Sonnet"
    "</div>",
    unsafe_allow_html=True,
)
