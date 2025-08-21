# main.py

import streamlit as st
from datetime import datetime
import json
from typing import List, Dict
import requests
from pytrends.request import TrendReq

# --- CONFIGURATION ---
PIXEL_API_KEY = "AaH9XXg6G9njbOo7Y28TsSSS9ofZ304nZS0q8ZBEWhS5vkNPKyH4Srea"  # Replace with your Pixel API key

# Blogger OAuth credentials
BLOGGER_CLIENT_ID = "YOUR_CLIENT_ID"
BLOGGER_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
BLOGGER_REDIRECT_URI = "https://glowwithhelen.blogspot.com/"  # or your Streamlit URL for OAuth redirect

# --- INITIALIZE SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []

if "current_chat" not in st.session_state:
    st.session_state.current_chat = {"title": "", "seo_desc": "", "content": "", "featured_image": ""}

# --- UTILITIES ---

def get_trending_topics(category: str = "beauty") -> List[str]:
    pytrends = TrendReq()
    trending_searches = pytrends.trending_searches(pn="united_states")
    trending_list = trending_searches[0].tolist()
    # Filter by category keywords
    filtered = [topic for topic in trending_list if category.lower() in topic.lower()]
    return filtered[:10] if filtered else trending_list[:10]

def generate_pixel_image(prompt: str) -> str:
    """
    Generate image URL using Pixel API based on prompt.
    Returns direct URL for embedding in HTML.
    """
    headers = {"Authorization": f"Bearer {PIXEL_API_KEY}"}
    data = {"prompt": prompt, "size": "1024x1024"}
    response = requests.post("https://api.pixel.com/v1/generate", headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("url")
    return ""

def generate_blog_html(title: str, seo_desc: str, topic: str) -> Dict[str, str]:
    """
    Generate HTML blog post with H2 headings and Pixel image.
    """
    # For simplicity, placeholder content; replace with Groq API call if needed
    content = f"""
    <h2>{topic}</h2>
    <p>This is a detailed blog post about {topic}, optimized for SEO and user engagement. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    """
    # Generate Pixel image
    image_url = generate_pixel_image(f"{topic} beauty fashion skincare")
    if image_url:
        content = f'<img src="{image_url}" alt="{topic}" style="width:100%;max-width:800px;">' + content

    html_post = f"""
    <h2>{topic}</h2>
    <p>{seo_desc}</p>
    {content}
    """
    return {"title": title, "seo_desc": seo_desc, "content": html_post, "featured_image": image_url}

def publish_to_blogger(blog_post: Dict[str, str]):
    """
    Publish blog post to Blogger using OAuth credentials.
    """
    access_token = st.session_state.get("blogger_token")
    if not access_token:
        st.warning("Blogger OAuth token missing. Authenticate first.")
        return
    url = f"https://www.googleapis.com/blogger/v3/blogs/YOUR_BLOG_ID/posts/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {
        "kind": "blogger#post",
        "title": blog_post["title"],
        "content": blog_post["content"]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        st.success("Blog post published successfully!")
    else:
        st.error(f"Error publishing post: {response.text}")

# --- STREAMLIT UI ---
st.set_page_config(page_title="Glow AI Blog Generator", layout="wide")

st.title("✨ Glow AI Blog Generator")

# Sidebar - Chat History
with st.sidebar:
    st.header("Chat History")
    if st.session_state.history:
        for idx, chat in enumerate(st.session_state.history):
            if st.button(f"{chat['title']}", key=f"hist_{idx}"):
                st.session_state.current_chat = chat
    if st.button("Clear History"):
        st.session_state.history = []

# Main input
topic_input = st.text_input("Enter topic (or leave empty for trending topics):")
category = st.selectbox("Category for trending topics:", ["Beauty", "Skincare", "Fashion"])

if st.button("Generate Blog Post"):
    # Determine topic
    if not topic_input:
        trending = get_trending_topics(category=category)
        topic_input = trending[0]  # pick first trending
    title = f"{topic_input} - Glow With Helen"
    seo_desc = f"Learn everything about {topic_input} in beauty, skincare, and fashion."
    blog_post = generate_blog_html(title, seo_desc, topic_input)
    st.session_state.current_chat = blog_post
    st.session_state.history.append(blog_post)

# Display generated post
if st.session_state.current_chat.get("content"):
    st.subheader("Generated Blog Post (HTML Format)")
    st.code(st.session_state.current_chat["content"], language="html")
    if st.button("Publish to Blogger"):
        publish_to_blogger(st.session_state.current_chat)
