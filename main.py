import streamlit as st
import requests
import base64
import json
from datetime import datetime
from typing import Optional, List

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="✨ Glow AI Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
.stApp { background: linear-gradient(135deg,#667eea 0%,#764ba2 100%); font-family:'Poppins', sans-serif; }
.main-header { text-align:center;padding:2rem 0;background: rgba(255,255,255,0.1);backdrop-filter: blur(10px);border-radius:20px;margin:1rem 0 2rem 0;border:1px solid rgba(255,255,255,0.2);}
.main-title { font-size:3.5rem;background:linear-gradient(45deg,#ff6b6b,#ffd93d,#6bcf7f,#4d94ff); background-size:300% 300%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; animation: gradientShift 3s ease-in-out infinite;font-weight:700;margin-bottom:0.5rem;}
.main-subtitle { color:rgba(255,255,255,0.9); font-size:1.2rem; font-weight:300;}
.content-card { background: rgba(255,255,255,0.15);backdrop-filter: blur(20px);border-radius: 20px;padding: 2rem;margin: 1rem 0;border: 1px solid rgba(255,255,255,0.2);}
.stTextInput input { background: rgba(255,255,255,0.2) !important; border: 2px solid rgba(255,255,255,0.3) !important;border-radius:15px !important; color:white !important;}
.stButton button { background: linear-gradient(135deg,#ff6b6b,#ffd93d) !important; color:white !important;border-radius:25px !important;}
.stImage { border-radius: 20px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important; transition: transform 0.3s ease !important; }
.stImage:hover { transform: scale(1.02) !important; }
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "posts_history" not in st.session_state:
    st.session_state.posts_history = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = [{"messages": [], "name": "Default Chat"}]
if "current_chat_idx" not in st.session_state:
    st.session_state.current_chat_idx = 0

# ------------------ API KEYS ------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
REPLICATE_API_TOKEN = st.secrets.get("REPLICATE_API_TOKEN", "")
PEXELS_API_KEY = st.secrets.get("PEXELS_API_KEY", "")
AMAZON_TAG = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
BLOGGER_CLIENT_ID = st.secrets.get("BLOGGER_CLIENT_ID", "")
BLOGGER_CLIENT_SECRET = st.secrets.get("BLOGGER_CLIENT_SECRET", "")
BLOGGER_REDIRECT_URI = st.secrets.get("BLOGGER_REDIRECT_URI", "")

# ------------------ HELPER FUNCTIONS ------------------
def append_affiliate_tag(url: str) -> str:
    if "amazon." not in url: return url
    if "tag=" in url: return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_TAG}"

def tag_affiliate_links(html: str) -> str:
    import re
    pattern = re.compile(r'(https?://(?:www\.)?amazon\.[^\s"\'\)]+)')
    return pattern.sub(lambda m: append_affiliate_tag(m.group(1)), html)

def call_groq_text(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}
    payload = {"messages":[{"role":"user","content":prompt}],"model":"llama-3.1-8b-instant","temperature":0.7,"max_tokens":1500}
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        return r.json()["choices"][0]["message"]["content"]
    except: return "❌ Error generating content."

def call_replicate_image(prompt: str) -> str:
    headers = {"Authorization": f"Token {REPLICATE_API_TOKEN}"}
    payload = {"version":"replicate/ideogram-v2","input":{"prompt":prompt}}
    try:
        r = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload)
        data = r.json()
        # Wait until output is ready
        import time
        while data["status"] not in ["succeeded","failed"]:
            time.sleep(2)
            r = requests.get(f'https://api.replicate.com/v1/predictions/{data["id"]}', headers=headers)
            data = r.json()
        return data["output"][0]
    except: return None

def generate_pin_overlay(title: str, summary: str) -> str:
    return f"{title} - {summary[:50]}"

def generate_pin_seo(topic: str, summary: str):
    seo_title = f"{topic} | Glow With Helen"
    seo_desc = f"{summary[:150]}"
    hashtags = f"#{topic.replace(' ','')} #Beauty #Skincare"
    return seo_title, seo_desc, hashtags

def fetch_pexels_image(query: str) -> str:
    try:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
        r = requests.get(url, headers={"Authorization": PEXELS_API_KEY})
        return r.json()["photos"][0]["src"]["large"]
    except: return None

# ------------------ HEADER ------------------
st.markdown("""
<div class="main-header">
    <div class="main-title">✨ Glow AI Agent</div>
    <div class="main-subtitle">SEO Blog & Pinterest Pin Generator</div>
</div>
""", unsafe_allow_html=True)

# ------------------ SINGLE TAB FOR EVERYTHING ------------------
st.subheader("💻 Content & Chat")

# ---------- AUTO-TRENDING ----------
st.markdown("### 🔥 Auto-Trending Blog Post")
auto_btn = st.button("Generate Auto-Trending Post")
if auto_btn:
    trending_topic = "Google Trend Topic | Pinterest Trend Topic"
    prompt_blog = f"Write a long, SEO-optimized, informative blog about: {trending_topic}. Start with H2, include p description, naturally mention 1-2 Amazon products."
    blog_content = call_groq_text(prompt_blog)
    blog_content_tagged = tag_affiliate_links(blog_content)
    summary = blog_content_tagged[:200]

    blog_image = fetch_pexels_image(trending_topic)
    pin_overlay = generate_pin_overlay(trending_topic, summary)
    pin_prompt = f"Pinterest pin vertical, realistic, beauty niche, overlay text: '{pin_overlay}'"
    pin_image = call_replicate_image(pin_prompt)
    pin_title, pin_desc, pin_hashtags = generate_pin_seo(trending_topic, summary)

    st.markdown("#### Blog Content")
    st.markdown(blog_content_tagged, unsafe_allow_html=True)
    if blog_image:
        st.image(blog_image, caption="Featured Image")
    st.markdown("#### Pinterest Pin")
    st.image(pin_image)
    st.markdown(f"**SEO Title:** {pin_title}")
    st.markdown(f"**Description:** {pin_desc}")
    st.markdown(f"**Hashtags:** {pin_hashtags}")

    st.session_state.posts_history.append({
        "topic": trending_topic,
        "blog": blog_content_tagged,
        "pin_image": pin_image,
        "pin_title": pin_title,
        "pin_desc": pin_desc,
        "pin_hashtags": pin_hashtags,
        "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

# ---------- MANUAL INPUT ----------
st.markdown("### ✍️ Manual Topic")
manual_topic = st.text_input("Enter your topic:")
manual_btn = st.button("Generate Blog & Pin")
if manual_btn and manual_topic:
    prompt_blog = f"Write a long, SEO-optimized, informative blog about: {manual_topic}. Start with H2, include p description, naturally mention 1-2 Amazon products."
    blog_content = call_groq_text(prompt_blog)
    blog
