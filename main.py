import streamlit as st
import requests
import re
import base64
import json
from datetime import datetime
from typing import Optional, List

# =========================
# Page configuration
# =========================
st.set_page_config(
    page_title="✨ Glow AI Agent - Beauty Blog & Pin Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Custom CSS for UI
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Poppins', sans-serif; }
.main-header { text-align: center; padding: 2rem 0; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; margin: 1rem 0 2rem 0; border: 1px solid rgba(255,255,255,0.2); }
.main-title { font-size: 3.5rem; background: linear-gradient(45deg, #ff6b6b, #ffd93d, #6bcf7f, #4d94ff); background-size: 300% 300%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; margin-bottom: 0.5rem; }
.main-subtitle { color: rgba(255,255,255,0.9); font-size: 1.2rem; font-weight: 300; }
.content-card { background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.2); }
.stTextInput input { background: rgba(255,255,255,0.2) !important; border: 2px solid rgba(255,255,255,0.3) !important; border-radius: 15px !important; color: white !important; font-size: 16px !important; transition: all 0.3s ease !important; }
.stTextInput input:focus { border-color: #ff6b6b !important; box-shadow: 0 0 20px rgba(255,107,107,0.3) !important; transform: translateY(-2px) !important; }
.stButton button { background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important; color: white !important; border: none !important; border-radius: 25px !important; padding: 0.75rem 2rem !important; font-weight: 600 !important; font-size: 16px !important; transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(255,107,107,0.3) !important; }
.stButton button:hover { transform: translateY(-3px) !important; box-shadow: 0 8px 25px rgba(255,107,107,0.5) !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# Load API keys from Streamlit secrets
# =========================
@st.cache_data
def get_config():
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "")
        pexels_api_key = st.secrets.get("PEXELS_API_KEY", "")
        amazon_tag = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
        return groq_api_key, replicate_token, pexels_api_key, amazon_tag
    except Exception as e:
        st.error(f"⚠️ Configuration error: {str(e)}")
        st.stop()

GROQ_API_KEY, REPLICATE_TOKEN, PEXELS_API_KEY, AMAZON_TAG = get_config()

# =========================
# Helper functions
# =========================
def append_affiliate_tag(url: str) -> str:
    if "amazon." not in url: return url
    if "tag=" in url: return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_TAG}"

def tag_all_amazon_links(html: str) -> str:
    pattern = re.compile(r'(https?://(?:www\.)?amazon\.[^\s"\'\)]+)')
    return pattern.sub(lambda m: append_affiliate_tag(m.group(1)), html)

def call_groq_text(model: str, prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"messages":[{"role":"user","content":prompt}], "model":model, "temperature":0.7, "max_tokens":1500}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except: return "❌ Error generating text."

def fetch_pexels_image(query: str) -> Optional[str]:
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        data = r.json()
        if data.get("photos"):
            return data["photos"][0]["src"].get("large") or data["photos"][0]["src"].get("medium")
        return None
    except: return None

# =========================
# Initialize session state
# =========================
if "chats" not in st.session_state:
    st.session_state.chats = []  # list of chats
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = -1

# =========================
# Sidebar: New Chat + Select Chat
# =========================
with st.sidebar:
    st.markdown("## 💬 Chats")
    if st.button("+ New Chat"):
        st.session_state.chats.append({
            "messages": [],
            "generated_blog": "",
            "featured_image": None
        })
        st.session_state.current_chat_index = len(st.session_state.chats) - 1
        st.experimental_rerun()

    chat_titles = [f"Chat {i+1}" for i in range(len(st.session_state.chats))]
    if chat_titles:
        selected = st.selectbox("Select Chat", chat_titles, index=st.session_state.current_chat_index if st.session_state.current_chat_index>=0 else 0)
        st.session_state.current_chat_index = chat_titles.index(selected)

    st.markdown("---")
    if st.button("🗑️ Delete Current Chat") and st.session_state.current_chat_index >= 0:
        st.session_state.chats.pop(st.session_state.current_chat_index)
        st.session_state.current_chat_index = len(st.session_state.chats)-1
        st.experimental_rerun()

# =========================
# Main Header
# =========================
st.markdown("""
<div class="main-header">
    <div class="main-title">✨ Glow AI Agent</div>
    <div class="main-subtitle">Beauty Blog & Pinterest Content Generator</div>
</div>
""", unsafe_allow_html=True)

# =========================
# Current Chat Handling
# =========================
if st.session_state.current_chat_index < 0:
    st.info("⚠️ Start a new chat from the sidebar!")
    st.stop()

chat = st.session_state.chats[st.session_state.current_chat_index]

chat_container = st.container()

# Display blog if exists
if chat["generated_blog"]:
    st.markdown("## 📝 Generated Blog Post")
    if chat["featured_image"]:
        st.image(chat["featured_image"], caption="Featured Image", use_column_width=True)
    st.markdown(chat["generated_blog"], unsafe_allow_html=True)

# Display chat history
st.markdown("## 💬 Chat History")
for msg in chat["messages"]:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**Glow AI:** {msg['content']}")

# Chat input
if prompt := st.chat_input("💄 Ask me to generate blog or Pinterest content..."):
    chat["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating content..."):
            ai_prompt = f"""
You are a professional beauty blogger and AI assistant.
- If user asks a blog: generate long, SEO-friendly post, start with <h2>, include 150-160 char search description, suggest affiliate products as 'Get this product here: [link]'.
- Generate a featured image using Pixel API.
- If user asks Pinterest pin: generate pin description and image via Replicate API or Pexels fallback.
- Maintain chat history and allow referencing previous outputs.
- Keep text friendly, informative, and professional.

User input: {prompt}
"""
            response = call_groq_text("groq/llama-3.1-70b-versatile", ai_prompt)
            chat["messages"].append({"role": "assistant", "content": response})

            # Try fetching a featured image via Pexels
            featured_img = fetch_pexels_image(prompt)
            if featured_img:
                chat["featured_image"] = featured_img

            st.markdown(response)
