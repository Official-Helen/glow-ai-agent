import streamlit as st
import requests
import json
import random
import re
from datetime import datetime
from typing import Dict, List

# ======================
# CONFIG
# ======================
AMAZON_TAG = "helenbeautysh-20"

BLOGGER_API_KEY = "YOUR_BLOGGER_API_KEY"
BLOG_ID = "YOUR_BLOG_ID"

# ======================
# SAMPLE AMAZON PRODUCTS
# ======================
AMAZON_PRODUCTS: Dict[str, List[str]] = {
    "skincare": [
        f"https://www.amazon.com/dp/B00949CTQQ?tag={AMAZON_TAG}",  # Paula’s Choice BHA
        f"https://www.amazon.com/dp/B0D663VWFC?tag={AMAZON_TAG}",  # COSRX Snail Mucin
        f"https://www.amazon.com/dp/B0F6D35G3G?tag={AMAZON_TAG}",  # La Roche-Posay Moisturizer
    ],
    "makeup": [
        f"https://www.amazon.com/dp/B07FNWB5LR?tag={AMAZON_TAG}",  # Maybelline Fit Me Foundation
        f"https://www.amazon.com/dp/B08R9V5ZKJ?tag={AMAZON_TAG}",  # NYX Lip Gloss
    ],
}

# ======================
# HELPER FUNCTIONS
# ======================

def fetch_google_trends():
    try:
        url = "https://trends.google.com/trending/rss?geo=US"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        items = re.findall(r"<title>(.*?)</title>", resp.text)
        return [i for i in items if i.lower() != "top stories"]
    except Exception as e:
        return [f"⚠️ Google Trends fetch failed: {e}"]

def fetch_pinterest_trends():
    try:
        url = "https://www.pinterest.com/trending/"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        items = re.findall(r"\"name\":\"(.*?)\"", resp.text)
        return list(set(items[:10]))
    except Exception as e:
        return [f"⚠️ Pinterest Trends fetch failed: {e}"]

def generate_seo_title(base: str) -> str:
    words = base.split()
    return " ".join(words[:8])  # keep title short (max ~60 chars)

def generate_meta_description(content: str) -> str:
    clean = re.sub(r"<.*?>", "", content)
    return clean[:155]

def generate_labels(keywords: List[str]) -> List[str]:
    return keywords[:5]

def generate_blog_post(topic: str, trend_keywords: List[str], niche: str):
    # Pick Amazon products for this niche
    products = AMAZON_PRODUCTS.get(niche, [])
    product_links = "".join([f'<li><a href="{p}" target="_blank">Buy on Amazon</a></li>' for p in products])

    # Content
    content = f"""
    <h2>{topic}</h2>
    <p>{topic} is trending right now! Let’s explore why it matters in beauty & skincare.</p>

    <p>Here are some powerful insights:</p>
    <ul>
        {"".join([f"<li>{kw}</li>" for kw in trend_keywords[:5]])}
    </ul>

    <p>Recommended products you’ll love:</p>
    <ul>{product_links}</ul>

    <p>Remember, beauty is about confidence and care. Use these tips to glow daily ✨</p>
    """

    return content

def publish_to_blogger(title: str, content: str, labels: List[str]):
    try:
        url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/?key={BLOGGER_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "kind": "blogger#post",
            "blog": {"id": BLOG_ID},
            "title": title,
            "labels": labels,
            "content": content,
        }
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
        if resp.status_code == 200:
            return "✅ Post published successfully!"
        else:
            return f"⚠️ Blogger publish failed: {resp.text}"
    except Exception as e:
        return f"⚠️ Blogger publish error: {e}"

# ======================
# STREAMLIT UI
# ======================
st.set_page_config(page_title="✨ Glow AI Agent", page_icon="✨", layout="wide")

st.title("✨ Glow AI Agent - Blogger Auto Publisher")
st.write("Generate SEO blog posts with Google + Pinterest trends, Amazon products, and auto-publish to Blogger.")

# Sidebar
st.sidebar.header("🔧 Settings")
niche = st.sidebar.selectbox("Choose niche:", list(AMAZON_PRODUCTS.keys()))

# Fetch trends
google_trends = fetch_google_trends()
pinterest_trends = fetch_pinterest_trends()

st.subheader("🔥 Latest Trends")
col1, col2 = st.columns(2)
with col1:
    st.write("**Google Trends:**")
    st.write(google_trends)
with col2:
    st.write("**Pinterest Trends:**")
    st.write(pinterest_trends)

# Post generation
st.subheader("✍️ Generate Blog Post")
topic = st.text_input("Enter a topic (or pick from trends):", random.choice(google_trends))
if st.button("Generate Post"):
    trend_keywords = google_trends[:3] + pinterest_trends[:3]
    content = generate_blog_post(topic, trend_keywords, niche)
    seo_title = generate_seo_title(topic)
    meta_desc = generate_meta_description(content)
    labels = generate_labels(trend_keywords)

    st.write("### Preview")
    st.markdown(f"**SEO Title:** {seo_title}")
    st.markdown(f"**Meta Description:** {meta_desc}")
    st.markdown(f"**Labels:** {', '.join(labels)}")
    st.markdown(content, unsafe_allow_html=True)

    if st.button("🚀 Publish to Blogger"):
        result = publish_to_blogger(seo_title, content, labels)
        st.success(result)
