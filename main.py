# main.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# -------------------------------
# CONFIGURATION
# -------------------------------
PIXEL_API_KEY = "AaH9XXg6G9njbOo7Y28TsSSS9ofZ304nZS0q8ZBEWhS5vkNPKyH4Srea"
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
BLOGGER_BLOG_ID = "YOUR_BLOGGER_BLOG_ID"
BLOGGER_ACCESS_TOKEN = "YOUR_BLOGGER_ACCESS_TOKEN"

st.set_page_config(
    page_title="Glow AI Blog Generator",
    page_icon="✨",
    layout="wide"
)

# -------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "current_post" not in st.session_state:
    st.session_state.current_post = {}

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def fetch_google_trends(category="beauty"):
    """
    Scrape Google Trends for a specific category (beauty, skincare, fashion)
    """
    try:
        url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")
        results = []
        for item in items:
            title = item.title.text
            if category.lower() in title.lower():
                results.append(title)
        return list(dict.fromkeys(results))[:5]  # remove duplicates
    except Exception as e:
        return [f"Error fetching trends: {e}"]

def fetch_pinterest_trends(category="beauty"):
    """
    Scrape Pinterest trends (simplified placeholder)
    """
    try:
        url = f"https://www.pinterest.com/search/pins/?q={category}&rs=typed"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        pins = soup.find_all("h3")
        results = [pin.get_text() for pin in pins if pin.get_text()]
        return list(dict.fromkeys(results))[:5]
    except Exception as e:
        return [f"Error fetching Pinterest trends: {e}"]

def generate_image(prompt):
    """
    Use Pixel API to generate an image for the blog post
    """
    url = "https://api.pixel.com/generate"
    payload = {
        "prompt": prompt,
        "size": "1024x1024",
        "n": 1
    }
    headers = {"Authorization": f"Bearer {PIXEL_API_KEY}"}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return data.get("images", [{}])[0].get("url", "")

def generate_blog_html(topic, seo_title="", seo_description=""):
    """
    Use Groq API to generate a full HTML blog post
    """
    prompt = f"Write a long, informative, SEO-friendly HTML blog post about '{topic}'. Use H2 for headings and include a featured image placeholder."
    url = "https://api.groq.com/v1/generate"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"prompt": prompt, "max_tokens": 1500}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    html_content = data.get("text", "")

    # Generate featured image
    image_url = generate_image(topic)
    if image_url:
        image_html = f'<img src="{image_url}" alt="{topic}" style="max-width:100%;"/>'
        html_content = image_html + "\n" + html_content

    return html_content, image_url

def publish_to_blogger(title, html_content, seo_description):
    """
    Publish post to Blogger
    """
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOGGER_BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {BLOGGER_ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": html_content
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text

# -------------------------------
# UI LAYOUT
# -------------------------------
st.title("✨ Glow AI Blog Generator")

# Sidebar history panel
st.sidebar.header("History")
for i, post in enumerate(reversed(st.session_state.history)):
    if st.sidebar.button(f"Delete {post['title']}", key=f"del_{i}"):
        st.session_state.history.pop(len(st.session_state.history) - 1 - i)
        st.experimental_rerun()
    st.sidebar.markdown(f"**{post['title']}**")

# Main blog generator
st.subheader("Generate Blog Post")
mode = st.radio("Mode", ["Auto Trend Blog", "Manual Topic Blog"])

if mode == "Auto Trend Blog":
    category = st.selectbox("Select Category", ["Beauty", "Skincare", "Fashion"])
    if st.button("Generate Auto Trend Blog"):
        google_trends = fetch_google_trends(category)
        pinterest_trends = fetch_pinterest_trends(category)
        combined_trends = list(dict.fromkeys(google_trends + pinterest_trends))
        topic = combined_trends[0] if combined_trends else category
        html_content, image_url = generate_blog_html(topic)
        st.session_state.current_post = {
            "title": topic,
            "content": html_content,
            "seo_description": f"Learn about {topic} trends in beauty and fashion.",
            "image": image_url
        }
        st.session_state.history.append(st.session_state.current_post)
        st.success("Blog generated successfully!")

if mode == "Manual Topic Blog":
    manual_topic = st.text_input("Enter your topic")
    seo_title = st.text_input("SEO Title")
    seo_description = st.text_input("SEO Description")
    if st.button("Generate Manual Blog"):
        if manual_topic:
            html_content, image_url = generate_blog_html(manual_topic)
            st.session_state.current_post = {
                "title": manual_topic,
                "content": html_content,
                "seo_description": seo_description,
                "image": image_url
            }
            st.session_state.history.append(st.session_state.current_post)
            st.success("Manual blog generated successfully!")
        else:
            st.error("Please enter a topic.")

# Display current blog
if st.session_state.current_post:
    st.subheader("Preview Blog Post (HTML)")
    st.markdown(st.session_state.current_post["content"], unsafe_allow_html=True)

    if st.button("Publish to Blogger"):
        status_code, response_text = publish_to_blogger(
            st.session_state.current_post["title"],
            st.session_state.current_post["content"],
            st.session_state.current_post["seo_description"]
        )
        if status_code == 200:
            st.success("Blog published to Blogger successfully!")
        else:
            st.error(f"Error publishing: {response_text}")
