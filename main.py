import streamlit as st
import requests
import re
import base64
import json
from datetime import datetime
from typing import Optional, List

# ------------------------- PAGE CONFIG -------------------------
st.set_page_config(
    page_title="✨ Glow AI Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------- CUSTOM CSS -------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Poppins', sans-serif; }
    .main-header { text-align:center; padding:1rem; background:rgba(255,255,255,0.1); border-radius:20px; margin:1rem 0; }
    .main-title { font-size:2.5rem; font-weight:700; color:white; }
    .main-subtitle { font-size:1rem; color:rgba(255,255,255,0.9); }
    .content-card { background: rgba(255,255,255,0.15); backdrop-filter:blur(10px); border-radius:20px; padding:2rem; margin:1rem 0; border:1px solid rgba(255,255,255,0.2); }
    .stTextInput input { background: rgba(255,255,255,0.2) !important; border-radius:15px !important; color:white !important; }
    .stButton button { background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important; color:white !important; border-radius:25px !important; padding:0.75rem 2rem !important; font-weight:600 !important; }
    .stButton button:hover { transform: translateY(-3px) !important; }
</style>
""", unsafe_allow_html=True)

# ------------------------- SESSION STATE -------------------------
if "chats" not in st.session_state:
    st.session_state.chats = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = -1

# ------------------------- CONFIG FUNCTION -------------------------
@st.cache_data
def get_config():
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "")
        pexels_api_key = st.secrets.get("PEXELS_API_KEY", "")
        amazon_tag = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
        return groq_api_key, replicate_token, pexels_api_key, amazon_tag
    except Exception as e:
        st.error(f"Configuration error: {str(e)}")
        st.stop()

GROQ_API_KEY, REPLICATE_TOKEN, PEXELS_API_KEY, AMAZON_TAG = get_config()

# ------------------------- HELPER FUNCTIONS -------------------------
def append_affiliate_tag(url: str) -> str:
    if "amazon." not in url:
        return url
    if "tag=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_TAG}"

def tag_all_amazon_links(html: str) -> str:
    pattern = re.compile(r'(https?://(?:www\.)?amazon\.[^\s"\'\)]+)')
    def repl(m):
        return append_affiliate_tag(m.group(1))
    return pattern.sub(repl, html)

def choose_model(user_choice: Optional[str], candidates: List[str]) -> str:
    if user_choice and user_choice != "auto":
        return user_choice
    return candidates[0]

def call_groq_text(model: str, prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    groq_model = model.replace("groq/", "") if "groq/" in model else "llama-3.1-8b-instant"
    payload = {"messages":[{"role":"user","content":prompt}], "model":groq_model, "temperature":0.7, "max_tokens":1500}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except:
        return "❌ Error generating text."

def fetch_pexels_image(query: str) -> Optional[str]:
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        data = r.json()
        if data.get("photos"):
            return data["photos"][0]["src"].get("large") or data["photos"][0]["src"].get("medium")
        return None
    except:
        return None

def call_replicate_image(prompt: str) -> Optional[bytes]:
    try:
        url = "https://api.replicate.com/v1/predictions"
        headers = {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type":"application/json"}
        payload = {"version":"replicate/stable-diffusion-v1","input":{"prompt":prompt}}
        r = requests.post(url, headers=headers, json=payload, timeout=180)
        result_url = r.json()["output"][0]
        img_bytes = requests.get(result_url).content
        return img_bytes
    except:
        return None

# ------------------------- SIDEBAR -------------------------
with st.sidebar:
    st.markdown("## 💬 Your Chats")
    if st.button("+ New Chat"):
        st.session_state.chats.append({"messages": [], "generated_blog": "", "featured_image": None})
        st.session_state.current_chat_index = len(st.session_state.chats) - 1

    if st.session_state.chats:
        chat_titles = [f"Chat {i+1}" for i in range(len(st.session_state.chats))]
        selected_chat = st.selectbox("Select Chat", chat_titles, index=st.session_state.current_chat_index)
        st.session_state.current_chat_index = chat_titles.index(selected_chat)

        if st.button("🗑️ Delete Current Chat"):
            del st.session_state.chats[st.session_state.current_chat_index]
            st.session_state.current_chat_index = max(0, st.session_state.current_chat_index - 1) if st.session_state.chats else -1

# ------------------------- MAIN HEADER -------------------------
st.markdown("""
<div class="main-header">
    <div class="main-title">✨ Glow AI Agent</div>
    <div class="main-subtitle">SEO Blog + Pinterest Pin Generator + Chat</div>
</div>
""", unsafe_allow_html=True)

# ------------------------- MAIN CONTENT -------------------------
if st.session_state.current_chat_index >= 0:
    current_chat = st.session_state.chats[st.session_state.current_chat_index]

    # Display chat messages
    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input section
    if prompt := st.chat_input("💄 Ask me to generate blog, Pinterest pin, or advice..."):
        current_chat["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Generating..."):
                # Build prompt for Groq
                today = datetime.utcnow().strftime("%B %d, %Y")
                ai_prompt = f"""
You are a professional beauty blogger and skincare expert. 
Generate informative, long, SEO-optimized content or answer the user’s task. 
Start with <h2> for Blogger SEO, use proper headings (<h2>, <h3>, <p>, <ul>, <li>). 
Insert 1-2 affiliate product links naturally, but backend will tag them. 
Date: {today}
Task/Question: {prompt}
Response:
"""
                response = call_groq_text("groq/llama-3.1-70b-versatile", ai_prompt)
                response_tagged = tag_all_amazon_links(response)
                st.markdown(response_tagged, unsafe_allow_html=True)
                current_chat["messages"].append({"role": "assistant", "content": response_tagged})

                # Generate featured image via Pexels
                featured_image = fetch_pexels_image(prompt)
                if featured_image:
                    st.image(featured_image, caption="Featured Image", use_column_width=True)
                    current_chat["featured_image"] = featured_image

                # Generate Pinterest pin via Replicate
                pin_prompt = f"Pinterest pin, beauty niche, vertical, aesthetic, theme: {prompt}"
                pin_bytes = call_replicate_image(pin_prompt)
                if pin_bytes:
                    st.image(pin_bytes, caption="Pinterest Pin")
                    st.download_button("⬇️ Download Pin", data=pin_bytes, file_name="pin.png", mime="image/png")
