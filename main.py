import streamlit as st
import requests
import re
import base64
import json
from datetime import datetime
from typing import Optional, List
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="✨ Glow AI Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# CSS Styling (UI Improvements)
# -------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(135deg,#667eea,#764ba2); font-family: 'Poppins', sans-serif; }
.main-header { text-align:center; padding:2rem 0; background:rgba(255,255,255,0.1); border-radius:20px; margin:1rem 0; border:1px solid rgba(255,255,255,0.2); }
.main-title { font-size:3rem; font-weight:700; background:linear-gradient(45deg,#ff6b6b,#ffd93d,#6bcf7f,#4d94ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation: gradientShift 3s ease-in-out infinite; margin-bottom:0.5rem; }
.main-subtitle { color:rgba(255,255,255,0.9); font-size:1.2rem; font-weight:300; }
.content-card { background: rgba(255,255,255,0.15); backdrop-filter: blur(20px); border-radius: 20px; padding:2rem; margin:1rem 0; border:1px solid rgba(255,255,255,0.2); }
.stButton button { background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important; color: white !important; border:none !important; border-radius:25px !important; padding:0.75rem 2rem !important; font-weight:600 !important; font-size:16px !important; transition: all 0.3s ease !important; box-shadow:0 4px 15px rgba(255,107,107,0.3) !important; }
.stButton button:hover { transform: translateY(-3px) !important; box-shadow:0 8px 25px rgba(255,107,107,0.5) !important; }
.stTextInput input { background: rgba(255,255,255,0.2) !important; border: 2px solid rgba(255,255,255,0.3) !important; border-radius: 15px !important; color:white !important; font-size:16px !important; }
.stTextInput input:focus { border-color:#ff6b6b !important; box-shadow:0 0 20px rgba(255,107,107,0.3) !important; }
.stSelectbox [data-baseweb="select"] { background: rgba(255,255,255,0.2) !important; border-radius: 15px !important; border: 2px solid rgba(255,255,255,0.3) !important; }
.stImage { border-radius:20px !important; box-shadow:0 10px 30px rgba(0,0,0,0.3) !important; transition: transform 0.3s ease !important; }
.stImage:hover { transform: scale(1.02) !important; }
@keyframes gradientShift { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Config / API Keys
# -------------------------------
@st.cache_data
def get_config():
    try:
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
        REPLICATE_API_KEY = st.secrets.get("REPLICATE_API_KEY", "")
        PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
        AMAZON_TAG = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
        return GROQ_API_KEY, REPLICATE_API_KEY, PEXELS_API_KEY, AMAZON_TAG
    except:
        st.error("Please add your API keys to Streamlit secrets!")
        st.stop()

GROQ_API_KEY, REPLICATE_API_KEY, PEXELS_API_KEY, AMAZON_TAG = get_config()

# -------------------------------
# Helper Functions
# -------------------------------
def append_affiliate_tag(url: str) -> str:
    if "amazon." not in url: return url
    if "tag=" in url: return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_TAG}"

def tag_all_amazon_links(html: str) -> str:
    pattern = re.compile(r'(https?://(?:www\.)?amazon\.[^\s"\'\)]+)')
    return pattern.sub(lambda m: append_affiliate_tag(m.group(1)), html)

def call_groq_text(prompt: str) -> str:
    import requests
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"messages":[{"role":"user","content":prompt}], "model":"llama-3.1-70b-versatile","temperature":0.7,"max_tokens":2000}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "❌ Error generating text."

def fetch_pexels_image(query: str) -> Optional[str]:
    try:
        r = requests.get(f"https://api.pexels.com/v1/search?query={query}&per_page=1", headers={"Authorization": PEXELS_API_KEY})
        data = r.json()
        if data.get("photos"): return data["photos"][0]["src"]["large"]
        return None
    except: return None

def call_replicate_image(prompt: str) -> Optional[str]:
    url = "https://api.replicate.com/v1/predictions"
    headers = {"Authorization": f"Token {REPLICATE_API_KEY}", "Content-Type": "application/json"}
    payload = {"version":"YOUR_MODEL_VERSION_ID","input":{"prompt":prompt}}
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 201: 
            prediction = r.json()
            return prediction["output"][0]
        return None
    except: return None

# -------------------------------
# Blogger API Integration
# -------------------------------
def get_blogger_service(creds_dict):
    creds = Credentials(**creds_dict)
    service = build('blogger', 'v3', credentials=creds)
    return service

def publish_to_blogger(title: str, content: str, blog_id: str, seo_desc: str, image_url: Optional[str], creds_dict):
    service = get_blogger_service(creds_dict)
    body = {"kind":"blogger#post","title":title,"content":content,"labels":["AI Blog"]}
    post = service.posts().insert(blogId=blog_id, body=body).execute()
    return post.get("url")

# -------------------------------
# Chat History & Session State
# -------------------------------
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = {"messages":[],"title":"","seo_desc":"","featured_image":""}

# -------------------------------
# Main UI
# -------------------------------
st.markdown('<div class="main-header"><div class="main-title">✨ Glow AI Agent</div><div class="main-subtitle">All-in-one Blog, Pinterest & Chat</div></div>', unsafe_allow_html=True)

# New chat / switch chat
col1, col2 = st.columns([3,1])
with col1:
    if st.button("➕ New Chat"):
        st.session_state.current_chat = {"messages":[],"title":"","seo_desc":"","featured_image":""}
        st.session_state.chat_sessions.append(st.session_state.current_chat)

with st.expander("💬 Chat & Generate Blog"):
    user_input = st.text_area("Type your topic or question here...", key="chat_input")
    generate_btn = st.button("🚀 Generate Content")
    
    if generate_btn and user_input.strip():
        with st.spinner("Generating blog & SEO description..."):
            # Generate blog
            blog_prompt = f"You are a professional beauty blogger. Write a detailed SEO-optimized blog post starting with <h2> for the topic: {user_input}"
            blog_content = call_groq_text(blog_prompt)
            blog_content = tag_all_amazon_links(blog_content)
            
            # Generate SEO description separately
            seo_prompt = f"Write a 155-character SEO meta description for the following blog post topic: {user_input}"
            seo_desc = call_groq_text(seo_prompt)
            
            # Generate featured image
            featured_image = fetch_pexels_image(user_input)
            
            # Save to session
            st.session_state.current_chat["messages"].append({"role":"assistant","content":blog_content})
            st.session_state.current_chat["title"] = user_input
            st.session_state.current_chat["seo_desc"] = seo_desc
            st.session_state.current_chat["featured_image"] = featured_image
            
            st.success("✅ Blog & SEO Description generated!")

    # Display chat messages
    for msg in st.session_state.current_chat["messages"]:
        st.markdown(f"**AI:** {msg['content']}")
        
    if st.session_state.current_chat["featured_image"]:
