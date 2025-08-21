import streamlit as st
import requests
import re
import base64
import json
from datetime import datetime
from typing import Optional, List

# Page configuration
st.set_page_config(
    page_title="✨ Glow AI Agent - Beauty Blog & Pin Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling and animations
st.markdown("""
<style>
    /* (CSS content unchanged for brevity) */
</style>

<!-- Floating particles -->
<div class="particles">
    <div class="particle" style="left: 10%; animation-delay: 0s;"></div>
    <div class="particle" style="left: 20%; animation-delay: 1s;"></div>
    <div class="particle" style="left: 30%; animation-delay: 2s;"></div>
    <div class="particle" style="left: 40%; animation-delay: 3s;"></div>
    <div class="particle" style="left: 50%; animation-delay: 4s;"></div>
    <div class="particle" style="left: 60%; animation-delay: 5s;"></div>
    <div class="particle" style="left: 70%; animation-delay: 2s;"></div>
    <div class="particle" style="left: 80%; animation-delay: 1s;"></div>
    <div class="particle" style="left: 90%; animation-delay: 3s;"></div>
</div>
""", unsafe_allow_html=True)

# Get API keys and settings from Streamlit secrets
@st.cache_data
def get_config():
    try:
        try:
            groq_api_key = st.secrets.get("GROQ_API_KEY", "")
            hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
            replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "")
            pexels_api_key = st.secrets["PEXELS_API_KEY"]
            amazon_tag = st.secrets.get("AMAZON_TAG", "helenbeautysh-20")
        except:
            st.error("Please add your API keys to Streamlit secrets!")
            st.stop()
        
        text_models = [
            "groq/llama-3.1-70b-versatile",
            "groq/llama-3.1-8b-instant",
            "groq/mixtral-8x7b-32768",
            "gpt2-medium",
            "microsoft/DialoGPT-medium"
        ]
        
        image_models = [
            "replicate/ideogram-v2",
            "black-forest-labs/FLUX.1-schnell",
            "stabilityai/sdxl-turbo",
            "runwayml/stable-diffusion-v1-5",
            "segmind/SSD-1B"
        ]
        
        return groq_api_key, hf_api_key, replicate_token, pexels_api_key, amazon_tag, text_models, image_models
    except Exception as e:
        st.error(f"⚠️ Configuration error: {str(e)}")
        st.error("Please add HUGGINGFACE_API_KEY and PEXELS_API_KEY to Streamlit secrets!")
        st.stop()

# Initialize configuration
GROQ_API_KEY, HF_API_KEY, REPLICATE_TOKEN, PEXELS_API_KEY, AMAZON_TAG, TEXT_MODEL_CANDIDATES, IMAGE_MODEL_CANDIDATES = get_config()

# Helper functions
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
    import requests
    if not GROQ_API_KEY:
        return call_hf_text(model, prompt)
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    groq_model = model.replace("groq/", "") if "groq/" in model else "llama-3.1-8b-instant"
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": groq_model,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return call_hf_text("gpt2-medium", prompt)
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return call_hf_text("gpt2-medium", prompt)

def call_hf_text(model: str, prompt: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True
        },
        "options": {"wait_for_model": True}
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        if r.status_code != 200:
            return f"❌ Error: {r.status_code} - {r.text[:200]}"
        data = r.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        if isinstance(data, dict) and "error" in data:
            return f"❌ Model Error: {data['error']}"
        return json.dumps(data)[:3000]
    except Exception as e:
        return f"❌ Error calling Hugging Face: {str(e)}"

def call_hf_image(model: str, prompt: str) -> Optional[str]:
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=180)
        if r.status_code != 200:
            st.error(f"Image generation error: {r.status_code} - {r.text[:200]}")
            return None
        if "image" not in r.headers.get("content-type", "").lower():
            st.error("Response is not an image")
            return None
        b64 = base64.b64encode(r.content).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

def fetch_pexels_image(query: str) -> Optional[str]:
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            return None
        data = r.json()
        if not data.get("photos"):
            return None
        return data["photos"][0]["src"].get("large") or data["photos"][0]["src"].get("medium")
    except Exception as e:
        st.error(f"Error fetching Pexels image: {str(e)}")
        return None

# Sidebar configuration, main tabs, etc remain same
# Blog Generator Tab corrected section:
    if generate_blog and blog_topic:
        with st.spinner("Generating your beauty blog post... ✍️"):
            model = choose_model(selected_text_model, TEXT_MODEL_CANDIDATES)
            today = datetime.utcnow().strftime("%B %d, %Y")
            rules = """You are a professional beauty blogger writing for Blogger platform. STRICT RULES:
- Do NOT include <html>, <head>, <body>, <title>, or any <meta> tags.
- Start with <h2> (never use <h1>).
- Use clean HTML with <h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>.
- Title must be under 60 characters (return inside the first <p><strong>Title:</strong> ...</p> line).
- Include a 150-160 char search description (return inside <p><strong>Search Description:</strong> ...</p>).
- Use headings hierarchy correctly.
- Write engaging, helpful, step-by-step content.
- Insert 1-2 Amazon product mentions naturally (just plain URLs like https://www.amazon.com/dp/B00TTD9BRC). Do NOT write affiliate tags; backend will add them.
- Be aware of the current date and year for trend awareness but DO NOT stuff the year."""
            prompt = f"""{rules}

Topic: "{blog_topic}"
Current date (UTC): {today}

Write the body HTML now:"""

            # Use Groq for better quality, HF as fallback
            if "groq/" in model:
                blog_content = call_groq_text(model, prompt)
            else:
                blog_content = call_hf_text(model, prompt)

            blog_content_tagged = tag_all_amazon_links(blog_content)
            pexels_image = fetch_pexels_image(blog_topic)
