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
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 1rem 0 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: fadeInDown 1s ease-out;
    }
    
    .main-title {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #ff6b6b, #ffd93d, #6bcf7f, #4d94ff);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease-in-out infinite;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 300;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Card styling for content */
    .content-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInUp 0.6s ease-out;
    }
    
    .content-card h2, .content-card h3 {
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Input styling */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.2) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: white !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus {
        border-color: #ff6b6b !important;
        box-shadow: 0 0 20px rgba(255, 107, 107, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #ff6b6b, #ffd93d) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.5) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05)) !important;
        backdrop-filter: blur(20px) !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #6bcf7f, #4d94ff) !important;
        border-radius: 15px !important;
        border: none !important;
        animation: bounceIn 0.6s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff6b6b, #ff8e8e) !important;
        border-radius: 15px !important;
        border: none !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        margin: 0.5rem 0 !important;
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating particles background */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-20px) rotate(120deg); }
        66% { transform: translateY(-10px) rotate(240deg); }
    }
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        color: white !important;
    }
    
    /* Code block styling */
    .stCodeBlock {
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Image styling */
    .stImage {
        border-radius: 20px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease !important;
    }
    
    .stImage:hover {
        transform: scale(1.02) !important;
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #ff6b6b !important;
    }
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
        # Get API keys (Groq for text, HF for images, with Replicate as premium upgrade)
        try:
            groq_api_key = st.secrets.get("GROQ_API_KEY", "")
            hf_api_key = st.secrets.get("HUGGINGFACE_API_KEY", "")
            replicate_token = st.secrets.get("REPLICATE_API_TOKEN", "")
            pexels_api_key = st.secrets["PEXELS_API_KEY"]
            amazon_tag = st.secrets.get("AMAZON_TAG", "glowbeauty-20")
        except:
            st.error("Please add your API keys to Streamlit secrets!")
            st.stop()
        
        # Text models - prioritize Groq for better quality
        text_models = [
            "groq/llama-3.1-70b-versatile",  # Groq - BEST quality
            "groq/llama-3.1-8b-instant",    # Groq - Fast
            "groq/mixtral-8x7b-32768",      # Groq - Good for long content
            "gpt2-medium",                   # HF fallback
            "microsoft/DialoGPT-medium"      # HF fallback
        ]
        
        # Image models - Free HF models with premium Replicate option
        image_models = [
            "replicate/ideogram-v2",         # Premium - best quality (when you upgrade)
            "black-forest-labs/FLUX.1-schnell",  # Free - good quality
            "stabilityai/sdxl-turbo",       # Free - fast
            "runwayml/stable-diffusion-v1-5", # Free - reliable
            "segmind/SSD-1B"                # Free - lightweight
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
    """Call Groq API for text generation"""
    import requests
    
    if not GROQ_API_KEY:
        return call_hf_text(model, prompt)  # Fallback to HF
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Extract model name for Groq
    groq_model = model.replace("groq/", "") if "groq/" in model else "llama-3.1-8b-instant"
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": groq_model,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return call_hf_text("gpt2-medium", prompt)  # Fallback
        
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return call_hf_text("gpt2-medium", prompt)  # Fallback

def call_hf_text(model: str, prompt: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    # Enhanced parameters for better text generation
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
        
        # Handle different response formats (simplified - no Mistral cleanup needed)
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
            
        # Handle error responses
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

# Sidebar configuration with new styling
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <h2 style="color: white; margin-bottom: 1rem;">🎛️ Glow Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    
    selected_text_model = st.selectbox(
        "🤖 Text Model", 
        ["auto"] + TEXT_MODEL_CANDIDATES,
        index=0
    )
    
    selected_image_model = st.selectbox(
        "🎨 Image Model", 
        ["auto"] + IMAGE_MODEL_CANDIDATES,
        index=0
    )

# Main header with animation
st.markdown("""
<div class="main-header">
    <div class="main-title">✨ Glow AI Agent</div>
    <div class="main-subtitle">Professional Beauty Blog & Pinterest Pin Generator</div>
</div>
""", unsafe_allow_html=True)

# Tab interface with beautiful styling
tab1, tab2, tab3 = st.tabs(["📝 Blog Generator", "📌 Pinterest Pins", "💬 Chat Mode"])

# Blog Generator Tab
with tab1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("## 📝 Beauty Blog Generator")
    st.markdown("*Generate SEO-optimized beauty blog posts with Amazon affiliate links*")
    
    blog_topic = st.text_input(
        "", 
        placeholder="✨ Enter your blog topic (e.g., Best skincare routine for dry skin)",
        key="blog_topic"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_blog = st.button("🚀 Generate Blog Post", key="generate_blog")
    
    if generate_blog and blog_topic:
        with st.spinner("Generating your beauty blog post... ✍️"):
            model = choose_model(selected_text_model, TEXT_MODEL_CANDIDATES)
            today = datetime.utcnow().strftime("%B %d, %Y")
            
            # Updated rules for Mistral format
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
            
            # Standard format for all models (removed Mistral special formatting)
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
            
            st.success("✅ Blog post generated successfully!")
            st.info(f"🤖 Model used: **{model}**")
            
            if pexels_image:
                st.image(pexels_image, caption=f"Featured image: {blog_topic}", use_column_width=True)
            
            st.markdown("### 📄 Generated Blog Content:")
            st.code(blog_content_tagged, language="html")
            
            with st.expander("📖 Preview Blog Post", expanded=False):
                st.markdown(blog_content_tagged, unsafe_allow_html=True)
    
    elif generate_blog:
        st.warning("⚠️ Please enter a blog topic!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Pinterest Pins Tab
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("## 📌 Pinterest Pin Generator")
    st.markdown("*Create beautiful Pinterest pins for your beauty content*")
    
    pin_prompt = st.text_input(
        "", 
        placeholder="🎨 Describe your pin (e.g., Glowing skin morning routine)",
        key="pin_prompt"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_pin = st.button("🎨 Generate Pinterest Pin", key="generate_pin")
    
    if generate_pin and pin_prompt:
        with st.spinner("Creating your Pinterest pin... 🎨"):
            model = choose_model(selected_image_model, IMAGE_MODEL_CANDIDATES)
            enhanced_prompt = f"""Pinterest pin, high quality, beauty niche, aesthetic, clean composition, soft lighting, professional photography style. Theme: {pin_prompt}. Vertical format, minimal text overlay, Instagram-worthy, trending beauty style."""
            
            pin_image = call_hf_image(model, enhanced_prompt)
            
            if pin_image:
                st.success("✅ Pinterest pin generated!")
                st.info(f"🎨 Model used: **{model}**")
                
                if pin_image.startswith("data:image"):
                    base64_data = pin_image.split(",")[1]
                    image_bytes = base64.b64decode(base64_data)
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(image_bytes, caption=f"Pinterest Pin: {pin_prompt}")
                        st.download_button(
                            label="⬇️ Download Pin",
                            data=image_bytes,
                            file_name=f"pinterest_pin_{pin_prompt[:20].replace(' ', '_')}.png",
                            mime="image/png"
                        )
            else:
                st.error("❌ Failed to generate pin. Try again!")
    
    elif generate_pin:
        st.warning("⚠️ Please enter a pin description!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat Mode Tab
with tab3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("## 💬 Chat with Glow Agent")
    st.markdown("*Ask questions about beauty, skincare, and makeup*")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("💄 Ask me about beauty, skincare, or makeup..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                model = choose_model(selected_text_model, TEXT_MODEL_CANDIDATES)
                
                # Standard format for all models (removed Mistral special formatting)
                beauty_prompt = f"""You are a professional beauty expert and skincare specialist. Answer this question with helpful, accurate advice about beauty, skincare, makeup, or wellness. Be friendly and informative.

Question: {prompt}

Answer:"""
                
                # Use Groq for better chat responses
                if "groq/" in model:
                    response = call_groq_text(model, beauty_prompt)
                else:
                    response = call_hf_text(model, beauty_prompt)
                st.markdown(response)
                
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar status with new styling
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Status")
    st.success("✅ Glow Agent Online!")
    st.markdown(f"🤖 Text: `{selected_text_model}`")
    st.markdown(f"🎨 Image: `{selected_image_model}`")
    st.markdown(f"💰 Amazon Tag: `{AMAZON_TAG}`")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Features:")
    st.markdown("• **Latest HF Models**: 2025 free models")
    st.markdown("• **Zephyr AI**: Advanced chat responses")
    st.markdown("• **Blog Generator**: SEO-optimized posts")
    st.markdown("• **Pinterest Pins**: Beauty content ready")
    st.markdown("• **Chat Mode**: Expert beauty advice")
    st.markdown("• **Auto Amazon Tags**: Monetize content!")
    
    st.markdown("---")
    st.markdown("*Made with ❤️ by Glow Agent*")
