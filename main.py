import streamlit as st
import requests
import json
import base64
import re
from datetime import datetime
from typing import Optional, List
from pytrends.request import TrendReq

# --- Page config ---
st.set_page_config(page_title="✨ Glow AI Blog Generator", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Helper functions ---
def get_trending_topic(category='beauty'):
    pytrends = TrendReq(hl='en-US', tz=360)
    trending_searches = pytrends.trending_searches(pn='united_states')
    filtered = [s for s in trending_searches[0] if category.lower() in s.lower()]
    return filtered[0] if filtered else trending_searches[0][0]

def append_affiliate_tag(url: str, amazon_tag: str):
    if "amazon." not in url:
        return url
    if "tag=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={amazon_tag}"

def tag_all_amazon_links(html: str, amazon_tag: str) -> str:
    pattern = re.compile(r'(https?://(?:www\.)?amazon\.[^\s"\'\)]+)')
    return pattern.sub(lambda m: append_affiliate_tag(m.group(1), amazon_tag), html)

def call_groq_text(model: str, prompt: str, groq_api_key: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"}
    payload = {"messages": [{"role": "user", "content": prompt}], "model": model, "temperature": 0.7, "max_tokens": 2000}
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code != 200:
        return f"❌ Error {r.status_code}"
    return r.json()["choices"][0]["message"]["content"]

def fetch_pixel_image(query: str, pixel_api_key: str) -> Optional[str]:
    url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=1"
    headers = {"Authorization": pixel_api_key}
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        data = r.json()
        photo = data["photos"][0]["src"]["large"]
        return photo
    except:
        return None

# --- Blogger Publish Function ---
def publish_to_blogger(blog_id: str, title: str, content_html: str, seo_description: str, access_token: str, featured_image_url: Optional[str] = None):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    post_data = {
        "kind": "blogger#post",
        "title": title,
        "content": content_html + f"<p><strong>SEO Description:</strong> {seo_description}</p>"
    }
    if featured_image_url:
        post_data["images"] = [{"url": featured_image_url}]
    r = requests.post(url, headers=headers, data=json.dumps(post_data))
    if r.status_code in [200, 201]:
        return r.json().get("url")
    else:
        return f"❌ Error {r.status_code}: {r.text}"

# --- Config ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
PIXEL_API_KEY = st.secrets.get("PIXEL_API_KEY", "")
AMAZON_TAG = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
BLOGGER_BLOG_ID = st.secrets.get("BLOGGER_BLOG_ID", "")
BLOGGER_ACCESS_TOKEN = st.secrets.get("BLOGGER_ACCESS_TOKEN", "")

# --- Session State ---
if "chats" not in st.session_state:
    st.session_state.chats = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = 0

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 💬 Chats")
    for i, chat in enumerate(st.session_state.chats):
        if st.button(f"Chat {i+1}", key=f"chat_{i}"):
            st.session_state.current_chat_index = i
            st.experimental_rerun()
    if st.button("➕ New Chat"):
        st.session_state.chats.append({"messages": [], "featured_image": None})
        st.session_state.current_chat_index = len(st.session_state.chats) - 1
        st.experimental_rerun()

# --- Main Chat Interface ---
current_chat = st.session_state.chats[st.session_state.current_chat_index] if st.session_state.chats else {"messages": [], "featured_image": None}

st.markdown("## ✨ Glow AI Blog Generator")

# Input for topic
st.subheader("📝 Topic Input")
use_auto_trend = st.checkbox("Generate topic automatically from Google & Pinterest trends", value=True)
custom_topic = st.text_input("Or enter your custom topic:")

# Input SEO description
seo_description_input = st.text_input("SEO Description for Blog Post (optional, else AI will generate inside content)")

if st.button("🚀 Generate Blog Post"):
    topic = ""
    if use_auto_trend:
        google_trend = get_trending_topic(category="beauty")
        pinterest_trend = get_trending_topic(category="fashion")
        topic = f"{google_trend} | {pinterest_trend}"
    elif custom_topic:
        topic = custom_topic
    else:
        st.warning("Please choose auto-trend or input a topic")
        st.stop()

    prompt = f"""
    You are a professional beauty blogger. Generate a **long, informative, and SEO-optimized blog post** in **HTML format** for Blogger. 
    - Start with <h2> (never use <h1>).
    - Include headings, subheadings, <p>, <ul>, <li>, <strong>, <em>.
    - Include 1-2 Amazon products naturally as: "Get this product [Product Name](Affiliate Link)".
    - Include a search description meta inside: <p><strong>Search Description:</strong> ...</p>
    Topic: {topic}
    """

    with st.spinner("Generating blog post..."):
        blog_html = call_groq_text("groq/llama-3.1-70b-versatile", prompt, GROQ_API_KEY)
        blog_html_tagged = tag_all_amazon_links(blog_html, AMAZON_TAG)

        # Generate image
        featured_image = fetch_pixel_image(topic, PIXEL_API_KEY)

        # Save to chat history
        current_chat["messages"].append({"role": "assistant", "content": blog_html_tagged})
        current_chat["featured_image"] = featured_image

# Display chat history
st.subheader("💬 Chat History")
for msg in current_chat["messages"]:
    st.markdown(msg["content"], unsafe_allow_html=True)

# Display featured image
if current_chat.get("featured_image"):
    st.image(current_chat["featured_image"], caption="Featured Image for Blog Post", use_column_width=True)

# --- Blogger Publishing ---
st.subheader("📢 Publish to Blogger")
blog_title_input = st.text_input("Blog Title", value=custom_topic or "New Blog Post")

if st.button("Publish to Blogger"):
    if not current_chat.get("messages"):
        st.warning("No generated blog post to publish!")
        st.stop()
    blog_html_to_publish = current_chat["messages"][-1]["content"]
    featured_image_to_publish = current_chat.get("featured_image")
    seo_desc = seo_description_input or f"Read this article about {blog_title_input}."

    with st.spinner("Publishing to Blogger..."):
        result_url = publish_to_blogger(
            BLOGGER_BLOG_ID,
            blog_title_input,
            blog_html_to_publish,
            seo_desc,
            BLOGGER_ACCESS_TOKEN,
            featured_image_url=featured_image_to_publish
        )
        if result_url.startswith("http"):
            st.success(f"✅ Blog published successfully! View it [here]({result_url})")
        else:
            st.error(result_url)
