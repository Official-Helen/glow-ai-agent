import streamlit as st
import requests
import json
import datetime

# ----------------------------
# Secrets (Set these in Streamlit Secrets)
# ----------------------------
PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
BLOGGER_BLOG_ID = st.secrets.get("BLOGGER_BLOG_ID", "")
BLOGGER_CLIENT_ID = st.secrets.get("BLOGGER_CLIENT_ID", "")
BLOGGER_CLIENT_SECRET = st.secrets.get("BLOGGER_CLIENT_SECRET", "")
BLOGGER_ACCESS_TOKEN = st.secrets.get("BLOGGER_ACCESS_TOKEN", "")

# ----------------------------
# Initialize session state for chat history
# ----------------------------
if "blog_history" not in st.session_state:
    st.session_state.blog_history = []

# ----------------------------
# Groq API - Text Generation
# ----------------------------
def generate_blog_content(topic, length=500):
    url = "https://api.groq.com/v1/generate"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"Write a detailed, SEO-optimized blog post about '{topic}' in HTML format. Start with H2 headings, include H3 subheadings, and make it informative and long. Do not include raw affiliate links, instead write like 'Get this product: [link]'."
    payload = {"prompt": prompt, "max_output_tokens": length}

    response = requests.post(url, headers=headers, json=payload)
    try:
        data = response.json()
        return data.get("output_text", "<p>No content generated</p>")
    except ValueError:
        st.error(f"Groq API returned invalid JSON: {response.text}")
        return "<p>Error generating content</p>"

# ----------------------------
# Pexels API - Image Generation
# ----------------------------
def generate_image(topic):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": topic, "per_page": 1}

    response = requests.get(url, headers=headers, params=params)
    try:
        data = response.json()
    except ValueError:
        st.error(f"Pexels API returned invalid JSON: {response.text}")
        return "https://via.placeholder.com/800x400?text=Blog+Image"

    if "photos" in data and len(data["photos"]) > 0:
        return data["photos"][0]["src"]["original"]
    return "https://via.placeholder.com/800x400?text=Blog+Image"

# ----------------------------
# Generate HTML Blog
# ----------------------------
def generate_blog_html(topic, seo_description=""):
    content = generate_blog_content(topic)
    image_url = generate_image(topic)

    html = f"""
    <!-- SEO Meta Description -->
    <meta name="description" content="{seo_description}">

    <!-- Blog Title -->
    <h2>{topic}</h2>

    <!-- Blog Image -->
    <img src="{image_url}" alt="{topic}" style="max-width:100%; height:auto;">

    <!-- Blog Content -->
    {content}
    """
    return html, image_url, content

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Glow AI Blog Generator", layout="wide")
st.title("✨ Glow AI Blog Generator")

# Sidebar - History
with st.sidebar:
    st.header("Blog History")
    for idx, item in enumerate(st.session_state.blog_history[::-1]):
        if st.button(f"{item['topic']} ({item['date']})", key=f"hist{idx}"):
            st.session_state.selected_blog = item

    if st.button("Clear History"):
        st.session_state.blog_history = []
        st.experimental_rerun()

# Main input
topic_input = st.text_input("Enter blog topic or click auto-trending:")
seo_desc_input = st.text_input("Enter SEO meta description (optional):")

# Generate blog button
if st.button("Generate Blog"):
    if not topic_input:
        st.warning("Please enter a blog topic.")
    else:
        html_content, image_url, content = generate_blog_html(topic_input, seo_desc_input)
        st.code(html_content, language="html")
        st.image(image_url, caption="Generated Blog Image", use_column_width=True)

        # Save to history
        st.session_state.blog_history.append({
            "topic": topic_input,
            "html": html_content,
            "image_url": image_url,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

# Selected blog from history
if "selected_blog" in st.session_state:
    blog = st.session_state.selected_blog
    st.subheader(f"History: {blog['topic']}")
    st.code(blog["html"], language="html")
    st.image(blog["image_url"], use_column_width=True)
