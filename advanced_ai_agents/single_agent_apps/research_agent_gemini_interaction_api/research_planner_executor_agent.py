"""Research Planner using Multi-Provider Support (Gemini, OpenRouter, Ollama, vLLM)."""

import streamlit as st
import time
import re
from llm_client import GeminiClient, OpenAICompatibleClient

def parse_tasks(text):
    return [{"num": m.group(1), "text": m.group(2).strip().replace('\n', ' ')} 
            for m in re.finditer(r'^(\d+)[\.\)\-]\s*(.+?)(?=\n\d+[\.\)\-]|\n\n|\Z)', text, re.MULTILINE | re.DOTALL)]

# Setup
st.set_page_config(page_title="Research Planner", page_icon="🔬", layout="wide")
st.title("🔬 AI Research Planner & Executor Agent (Multi-Provider) ✨")

# Session State
for k in ["plan_id", "plan_text", "tasks", "research_id", "research_text", "synthesis_text", "infographic"]:
    if k not in st.session_state: st.session_state[k] = [] if k == "tasks" else None

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    provider = st.selectbox("Select Provider", ["Google Gemini", "OpenRouter", "Ollama", "vLLM"])
    
    api_key = ""
    base_url = ""
    model_name = ""
    
    if provider == "Google Gemini":
        api_key = st.text_input("🔑 Google API Key", type="password")
    elif provider == "OpenRouter":
        api_key = st.text_input("🔑 OpenRouter API Key", type="password")
        base_url = "https://openrouter.ai/api/v1"
        model_name = st.text_input("Model Name", value="google/gemini-2.0-flash-exp:free")
    elif provider == "Ollama":
        base_url = st.text_input("Base URL", value="http://localhost:11434/v1")
        model_name = st.text_input("Model Name", value="llama3")
        api_key = "ollama" # Dummy key
    elif provider == "vLLM":
        api_key = st.text_input("🔑 API Key", type="password", value="EMPTY")
        base_url = st.text_input("Base URL", value="http://localhost:8000/v1")
        model_name = st.text_input("Model Name")

    if st.button("Reset State"):
        for k in ["plan_id", "plan_text", "tasks", "research_id", "research_text", "synthesis_text", "infographic"]:
            setattr(st.session_state, k, [] if k == "tasks" else None)
        st.rerun()

    st.markdown("""
    ### How It Works
    1. **Plan** → Creates research tasks
    2. **Select** → Choose tasks to research  
    3. **Research** → Deep Research (Gemini) or Web Search + Analyze (Others)
    4. **Synthesize** → Writes report
    """)

# Client Initialization
client = None
if api_key:
    if provider == "Google Gemini":
        client = GeminiClient(api_key=api_key)
    elif provider in ["OpenRouter", "Ollama", "vLLM"]:
        if base_url and model_name:
            client = OpenAICompatibleClient(api_key=api_key, base_url=base_url, model=model_name)

if not client:
    st.info("👆 Configure the provider in the sidebar to start")
    st.stop()

# Phase 1: Plan
research_goal = st.text_area("📝 Research Goal", placeholder="e.g., Research B2B HR SaaS market in Germany")
if st.button("📋 Generate Plan", disabled=not research_goal, type="primary"):
    with st.spinner("Planning..."):
        result = client.create_plan(research_goal)
        if result and result.get("text"):
            st.session_state.plan_id = result.get("id")
            st.session_state.plan_text = result.get("text")
            st.session_state.tasks = parse_tasks(result.get("text"))
        else:
             st.error("Failed to generate plan.")

# Phase 2: Select & Research  
if st.session_state.plan_text:
    st.divider()
    st.subheader("🔍 Select Tasks & Research")
    
    # Task Selection
    selected = []
    if st.session_state.tasks:
        for t in st.session_state.tasks:
            if st.checkbox(f"**{t['num']}.** {t['text']}", True, key=f"t{t['num']}"):
                selected.append(f"{t['num']}. {t['text']}")
    else:
        st.warning("No tasks parsed. Check the plan format.")
        st.text(st.session_state.plan_text)

    st.caption(f"✅ {len(selected)}/{len(st.session_state.tasks)} selected")
    
    if st.button("🚀 Start Research", type="primary", disabled=not selected):
        with st.spinner("Researching (this may take a while)..."):
            result = client.execute_research(selected, previous_context=st.session_state.plan_id)
            if result and result.get("text"):
                st.session_state.research_id = result.get("id")
                st.session_state.research_text = result.get("text")
                st.rerun()
            else:
                st.error("Research failed.")

if st.session_state.research_text:
    st.divider()
    st.subheader("📄 Research Results")
    st.markdown(st.session_state.research_text)

# Phase 3: Synthesis + Infographic
if st.session_state.research_text: # Changed condition: Synthesis depends on research text, not ID (ID is optional for non-Gemini)
    if st.button("📊 Generate Executive Report", type="primary"):
        with st.spinner("Synthesizing report..."):
            synthesis = client.synthesize_report(st.session_state.research_text, previous_context=st.session_state.research_id)
            if synthesis:
                st.session_state.synthesis_text = synthesis
            else:
                st.error("Synthesis failed")
        
        # Infographic (Optional)
        with st.spinner("Attempting infographic..."):
            infographic = client.generate_infographic(st.session_state.synthesis_text)
            if infographic:
                st.session_state.infographic = infographic
            else:
                 if provider == "Google Gemini": # Only warn for Gemini if it failed, others silently skip
                    st.warning("Infographic generation failed or not supported.")
        st.rerun()

if st.session_state.synthesis_text:
    st.divider()
    st.markdown("## 📊 Executive Report")
    
    # TL;DR Infographic at the top
    if st.session_state.infographic:
        st.markdown("### 🎨 TL;DR")
        st.image(st.session_state.infographic, use_container_width=True)
        st.divider()
    
    st.markdown(st.session_state.synthesis_text)
    st.download_button("📥 Download Report", st.session_state.synthesis_text, "research_report.md", "text/markdown")

st.divider()
st.caption("Powered by Multi-Provider AI Agent")
