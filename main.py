import streamlit as st
from datetime import datetime
import requests

# -----------------------------
# TRENDING TOPICS FUNCTION
# -----------------------------
def get_trending_topics(category="beauty"):
    """
    Fetch trending topics using pytrends or fallback to predefined list.
    Only include topics related to the given category.
    """
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='en-US', tz=360)
        trending_searches = pytrends.trending_searches(pn='united_states')
        # Filter based on category keywords
        filtered = [t for t in trending_searches[0] if category.lower() in t.lower()]
        return filtered[:5] if filtered else trending_searches[0][:5]
    except Exception as e:
        print(f"⚠️ Pytrends error: {e}")
        # fallback static topics
        fallback_topics = {
            "beauty": ["Best Skincare Routine 2025", "Top Makeup Trends", "Vegan Beauty Products", "Anti-aging Skincare", "Hydrating Masks"],
            "skincare": ["Glowing Skin Tips", "Acne Treatment Products", "Niacinamide Benefits", "Best Serums 2025", "Hydrating Moisturizers"],
            "fashion": ["Street Style Trends", "Summer Dresses 2025", "Sustainable Fashion", "Statement Accessories", "Workwear Fashion"]
        }
        return fallback_topics.get(category.lower(), ["Trending Topic 1", "Trending Topic 2"])

# -----------------------------
# PIXEL API IMAGE GENERATION
# -----------------------------
def generate_blog_image(prompt, pixel_api_key):
    url = "https://api.pixel.com/v1/generate"
    headers = {"Authorization": f"Bearer {pixel_api_key}"}
    payload = {"prompt": prompt, "size": "1024x1024"}
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # return URL of generated image
        return data.get("image_url")
    else:
        print("⚠️ Pixel API error:", response.text)
        return None

# -----------------------------
# BLOG POST GENERATOR
# -----------------------------
def generate_blog_post_html(title, content, image_url, affiliate_links=None):
    """
    Returns HTML formatted blog post for Blogger.
    """
    # HTML formatting
    html = f"""<h2>{title}</h2>
<img src="{image_url}" alt="{title}" style="max-width:100%; height:auto;" />
<div>{content}</div>
"""
    # Add affiliate links if provided
    if affiliate_links:
        html += "<ul>"
        for product_name, link in affiliate_links.items():
            html += f'<li>Get this product: <a href="{link}" target="_blank">{product_name}</a></li>'
        html += "</ul>"
    return html

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.title("Glow AI Agent - Auto Blog Generator")

pixel_api_key = st.text_input("Enter your Pixel API Key:", type="password")

category = st.selectbox("Select category:", ["beauty", "skincare", "fashion"])

st.header("Trending Topics")
topics = get_trending_topics(category)
st.write(topics)

selected_topic = st.selectbox("Select topic to generate blog:", topics)

# Optional user input to customize content
user_prompt = st.text_area("Additional instructions for AI content:")

if st.button("Generate Blog Post"):
    # 1. Generate image via Pixel
    image_url = generate_blog_image(selected_topic, pixel_api_key)
    if not image_url:
        st.warning("Image generation failed. Using placeholder.")
        image_url = "https://via.placeholder.com/1024x512.png?text=Blog+Image"

    # 2. Generate blog content using Groq API
    import requests

    groq_api_key = st.text_input("Enter your Groq API Key:", type="password")
    groq_endpoint = "https://api.groq.ai/v1/generate"

    prompt_text = f"Write a detailed, SEO-optimized blog post in HTML about '{selected_topic}'. {user_prompt or ''}"
    headers = {"Authorization": f"Bearer {groq_api_key}"}
    payload = {"prompt": prompt_text, "max_tokens": 1500, "temperature": 0.7}

    response = requests.post(groq_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        blog_content = response.json().get("text", "Content generation failed.")
    else:
        blog_content = f"Error generating content: {response.text}"

    # 3. Example affiliate links dictionary
    affiliate_links = {
        "The Ordinary Niacinamide 10% + Zinc 1%": "https://amzn.to/4eXaTxE",
        "Paula’s Choice 2% BHA Exfoliant": "https://www.amazon.com/dp/B00949CTQQ/?tag=helenbeautysh-20"
    }

    # 4. Generate final HTML
    blog_html = generate_blog_post_html(selected_topic, blog_content, image_url, affiliate_links)

    st.subheader("Generated Blog Post (HTML)")
    st.code(blog_html, language="html")

    # 5. Optional: auto-publish to Blogger (requires OAuth flow)
    if st.button("Publish to Blogger"):
        st.info("Publishing functionality requires OAuth integration. Implement Blogger API here.")
