#!/usr/bin/env python3
"""
Glow AI Agent - Complete Beauty & Fashion Blog Content Creator
Automatically generates SEO-optimized blog posts for "Glow With Helen"

This single-file app includes:
- Config
- TrendAnalyzer (uses pytrends if available)
- ProductDatabase (with Amazon affiliate link generation)
- ImageManager (Pexels API or placeholders)
- ContentGenerator (HTML content with f-strings properly closed)
- BloggerPublisher (optional; only if Google APIs are installed)
- Streamlit UI (text input, generate button, preview, download, optional publish)
"""

import os
import sys
import requests
import json
import random
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

# ---------- Optional dependencies gate ----------
OPTIONAL_IMPORTS = {
    "google_apis": False,
    "pytrends": False,
    "beautifulsoup": False,
    "schedule": False,
    "streamlit": False,
}

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    OPTIONAL_IMPORTS["google_apis"] = True
except Exception:
    pass

try:
    from pytrends.request import TrendReq
    OPTIONAL_IMPORTS["pytrends"] = True
except Exception:
    TrendReq = None

try:
    from bs4 import BeautifulSoup  # noqa: F401 (not required here, but kept)
    OPTIONAL_IMPORTS["beautifulsoup"] = True
except Exception:
    pass

try:
    import schedule  # noqa: F401 (not used in UI; kept to preserve feature)
    OPTIONAL_IMPORTS["schedule"] = True
except Exception:
    pass

try:
    import streamlit as st
    OPTIONAL_IMPORTS["streamlit"] = True
except Exception:
    # We'll run CLI-mode if Streamlit isn't available
    st = None

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("glow_ai.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------- Config ----------
@dataclass
class Config:
    # API Keys (set via environment variables)
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    GOOGLE_TRENDS_API_KEY: str = os.getenv("GOOGLE_TRENDS_API_KEY", "")
    BLOGGER_CLIENT_ID: str = os.getenv("BLOGGER_CLIENT_ID", "")
    BLOGGER_CLIENT_SECRET: str = os.getenv("BLOGGER_CLIENT_SECRET", "")
    BLOGGER_BLOG_ID: str = os.getenv("BLOGGER_BLOG_ID", "")
    # Amazon Affiliate
    AMAZON_AFFILIATE_TAG: str = os.getenv("AMAZON_AFFILIATE_TAG", "helenbeautysh-20")
    # Blog settings
    BLOG_NAME: str = "Glow With Helen"
    AUTHOR_NAME: str = "Helen"
    # Controls
    MAX_POSTS_PER_DAY: int = 3
    MIN_KEYWORD_INTEREST: int = 70
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    # Content
    MIN_CONTENT_LENGTH: int = 1500
    MAX_TITLE_LENGTH: int = 60
    META_DESC_LENGTH: int = 155

    def validate(self) -> List[str]:
        issues = []
        if not self.PEXELS_API_KEY:
            issues.append("PEXELS_API_KEY not set - images will use placeholders")
        if not self.BLOGGER_CLIENT_ID or not self.BLOGGER_CLIENT_SECRET:
            issues.append("Blogger credentials not set - publishing disabled")
        if not self.BLOGGER_BLOG_ID:
            issues.append("BLOGGER_BLOG_ID not set - publishing disabled")
        return issues

# ---------- Trends ----------
class TrendAnalyzer:
    """Trend analysis (Google Trends if available; otherwise seasonal fallbacks)."""

    def __init__(self, config: Config):
        self.config = config
        self.beauty_keywords = [
            "skincare routine", "makeup trends", "beauty tips", "anti aging",
            "acne treatment", "hair care", "nail art", "fashion trends",
            "skincare ingredients", "makeup tutorial", "beauty hacks",
            "natural skincare", "korean skincare", "retinol", "niacinamide",
            "vitamin c serum", "hyaluronic acid", "face masks", "sunscreen",
            "glass skin", "slug life", "skin cycling", "dopamine makeup",
            "clean beauty", "sustainable fashion", "cruelty free"
        ]
        self.pytrends = None
        if OPTIONAL_IMPORTS["pytrends"]:
            try:
                self.pytrends = TrendReq(hl="en-US", tz=360)
            except Exception:
                self.pytrends = None

    def get_google_trends(self, keywords: List[str], timeframe: str = "today 3-m") -> Dict:
        if not self.pytrends:
            return {}
        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe, geo="US")
            df = self.pytrends.interest_over_time()
            trends = {}
            if df is not None and not df.empty:
                for kw in keywords:
                    if kw in df.columns:
                        interest_avg = int(df[kw].mean())
                        trend = "rising" if df[kw].iloc[-1] > df[kw].iloc[0] else "falling"
                        trends[kw] = {"interest": interest_avg, "trend": trend}
            return trends
        except Exception as e:
            logger.error(f"Google Trends error: {e}")
            return {}

    def get_pinterest_trends(self) -> List[Dict]:
        # Simulated seasonal trends
        month = datetime.now().month
        seasonal = {
            12: ["winter skincare", "holiday makeup", "party nails"],
            1: ["new year glow up", "dry skin remedies", "detox skincare"],
            2: ["valentine's makeup", "anti-aging", "self care routine"],
            3: ["spring skincare", "fresh makeup", "allergy skin care"],
            4: ["spring cleaning skincare", "refresh routine"],
            5: ["mother's day gifts", "spring trends", "sun protection"],
            6: ["summer skincare", "waterproof makeup", "wedding beauty"],
            7: ["sun care", "beach waves", "sweat proof makeup"],
            8: ["back to school", "quick routines", "budget beauty"],
            9: ["fall skincare", "autumn makeup", "transition routine"],
            10: ["halloween makeup", "fall trends", "cozy skincare"],
            11: ["thanksgiving prep", "dry skin solutions", "holiday prep"],
        }
        chosen = seasonal.get(month, ["general skincare", "makeup tips", "beauty routine"])
        return [{"keyword": t, "source": "pinterest", "interest": random.randint(75, 95)} for t in chosen]

    @staticmethod
    def _competition(keyword: str) -> str:
        if len(keyword.split()) <= 2:
            return "high"
        if "tutorial" in keyword or "guide" in keyword:
            return "medium"
        if len(keyword.split()) >= 4:
            return "low"
        return "medium"

    def get_trending_topics(self) -> List[Dict]:
        logger.info("Analyzing trending topics...")
        topics: List[Dict] = []

        # Google Trends subset
        g_trends = self.get_google_trends(self.beauty_keywords[:5])
        for kw, data in g_trends.items():
            if data["interest"] >= self.config.MIN_KEYWORD_INTEREST:
                topics.append({
                    "keyword": kw,
                    "interest": data["interest"],
                    "competition": self._competition(kw),
                    "trend": data["trend"],
                    "source": "google_trends"
                })

        # Pinterest (simulated)
        topics.extend(self.get_pinterest_trends())

        # If nothing, add evergreen
        if not topics:
            topics.extend([
                {"keyword": "retinol for beginners", "interest": 85, "competition": "low", "trend": "steady"},
                {"keyword": "niacinamide benefits", "interest": 78, "competition": "medium", "trend": "rising"},
                {"keyword": "glass skin routine", "interest": 82, "competition": "medium", "trend": "rising"},
                {"keyword": "affordable skincare dupes", "interest": 88, "competition": "low", "trend": "steady"},
                {"keyword": "korean beauty secrets", "interest": 79, "competition": "medium", "trend": "steady"},
            ])

        filtered = [t for t in topics if t["interest"] >= self.config.MIN_KEYWORD_INTEREST and t.get("competition") != "high"]
        filtered.sort(key=lambda x: x["interest"], reverse=True)
        return filtered[:10]

# ---------- Products ----------
class ProductDatabase:
    """Product DB + Amazon affiliate link generation."""

    def __init__(self, config: Config):
        self.config = config
        self.products = {
            "skincare": [
                {"name": "CeraVe Foaming Facial Cleanser", "id": "B077TGQZPX", "price": "$12.99", "rating": "4.5", "category": "cleanser"},
                {"name": "The Ordinary Niacinamide 10% + Zinc 1%", "id": "B06XHW8TQL", "price": "$7.20", "rating": "4.3", "category": "serum"},
                {"name": "Neutrogena Ultra Sheer Sunscreen SPF 55", "id": "B002JAYMEE", "price": "$8.47", "rating": "4.4", "category": "sunscreen"},
                {"name": "Olay Regenerist Retinol 24 Night Moisturizer", "id": "B07MVJC3J8", "price": "$18.99", "rating": "4.2", "category": "moisturizer"},
                {"name": "Paula's Choice 2% BHA Liquid Exfoliant", "id": "B00949CTQQ", "price": "$29.50", "rating": "4.4", "category": "exfoliant"},
                {"name": "La Roche-Posay Toleriane Caring Wash", "id": "B01N7T7JKJ", "price": "$14.99", "rating": "4.3", "category": "cleanser"},
                {"name": "Eucerin Daily Protection Face Lotion SPF 30", "id": "B001ET76EE", "price": "$8.97", "rating": "4.2", "category": "sunscreen"},
            ],
            "makeup": [
                {"name": "Maybelline Fit Me Matte Foundation", "id": "B07C2ZS7B8", "price": "$7.99", "rating": "4.2", "category": "foundation"},
                {"name": "Urban Decay Naked Eyeshadow Palette", "id": "B004Q8U1ZA", "price": "$54.00", "rating": "4.5", "category": "eyeshadow"},
                {"name": "Fenty Beauty Gloss Bomb Universal Lip Luminizer", "id": "B075BYKK7T", "price": "$19.00", "rating": "4.3", "category": "lip_gloss"},
                {"name": "L'Oréal Paris Voluminous Lash Paradise Mascara", "id": "B06Y5ZTQTX", "price": "$8.99", "rating": "4.1", "category": "mascara"},
                {"name": "Rare Beauty Soft Pinch Liquid Blush", "id": "B08F7RQ9Q8", "price": "$20.00", "rating": "4.4", "category": "blush"},
                {"name": "Charlotte Tilbury Pillow Talk Lipstick", "id": "B07D7R8G5K", "price": "$38.00", "rating": "4.6", "category": "lipstick"},
            ],
            "tools": [
                {"name": "Foreo Luna Mini 3 Face Cleansing Brush", "id": "B07VQZR8DK", "price": "$139.00", "rating": "4.0", "category": "cleansing_tool"},
                {"name": "Revlon One-Step Hair Dryer and Volumizer", "id": "B01LSUQSB0", "price": "$59.99", "rating": "4.2", "category": "hair_tool"},
                {"name": "Real Techniques Makeup Brush Set", "id": "B004TSF8R6", "price": "$19.99", "rating": "4.3", "category": "brushes"},
                {"name": "Jade Roller and Gua Sha Set", "id": "B07L9QZXR3", "price": "$12.99", "rating": "4.1", "category": "facial_tool"},
                {"name": "Conair Double-Sided Lighted Makeup Mirror", "id": "B00002N5Z1", "price": "$39.99", "rating": "4.2", "category": "mirror"},
            ],
        }

    def find_relevant_products(self, keyword: str, count: int = 3) -> List[Dict]:
        kw = keyword.lower()
        relevant: List[Dict] = []

        category_mapping = {
            "cleanser": ["cleanser", "cleansing", "wash"],
            "serum": ["serum", "vitamin c", "niacinamide", "retinol"],
            "moisturizer": ["moisturizer", "cream", "hydrat"],
            "sunscreen": ["sunscreen", "spf", "sun protection"],
            "foundation": ["foundation", "base makeup"],
            "eyeshadow": ["eyeshadow", "eye makeup", "palette"],
            "mascara": ["mascara", "lashes"],
            "lipstick": ["lipstick", "lip"],
            "tools": ["tool", "brush", "mirror"],
        }

        for _, products in self.products.items():
            for p in products:
                terms = category_mapping.get(p.get("category", ""), [])
                if any(t in kw for t in terms):
                    relevant.append(p)
                elif any(term in p["name"].lower() for term in kw.split()):
                    relevant.append(p)

        if not relevant:
            relevant = self.products["skincare"]

        # Deduplicate by id
        seen = set()
        unique: List[Dict] = []
        for p in relevant:
            if p["id"] not in seen:
                unique.append(p)
                seen.add(p["id"])

        return random.sample(unique, min(count, len(unique)))

    def create_affiliate_link(self, product: Dict) -> str:
        base_url = f"https://www.amazon.com/dp/{product['id']}"
        link = f"{base_url}/?tag={self.config.AMAZON_AFFILIATE_TAG}"
        return f'<a href="{link}" target="_blank" rel="nofollow sponsored">{product["name"]}</a>'

# ---------- Images ----------
class ImageManager:
    """Pexels integration with graceful fallback to placeholders."""

    def __init__(self, config: Config):
        self.config = config
        self.headers = {"Authorization": config.PEXELS_API_KEY} if config.PEXELS_API_KEY else {}
        self.cache: Dict[str, List[Dict]] = {}

    def search_pexels_images(self, query: str, count: int = 3) -> List[Dict]:
        if not self.config.PEXELS_API_KEY:
            return self._placeholders(query, count)

        key = f"{query}_{count}"
        if key in self.cache:
            return self.cache[key]

        url = "https://api.pexels.com/v1/search"
        params = {
            "query": f"{query} beauty skincare makeup",
            "per_page": count + 2,
            "orientation": "landscape",
            "size": "large",
        }
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=self.config.REQUEST_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                photos = data.get("photos", [])[:count]
                images = []
                for photo in photos:
                    images.append({
                        "url": photo["src"]["large"],
                        "url_medium": photo["src"]["medium"],
                        "alt": f"{query} - {photo.get('alt', 'Beauty and skincare image')}",
                        "photographer": photo["photographer"],
                        "photographer_url": photo["photographer_url"],
                        "pexels_url": photo["url"],
                    })
                self.cache[key] = images
                return images
        except Exception as e:
            logger.error(f"Pexels error: {e}")

        return self._placeholders(query, count)

    @staticmethod
    def _placeholders(query: str, count: int) -> List[Dict]:
        bank = [
            {
                "url": "https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": "https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Beautiful skincare routine",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "pexels_url": "https://www.pexels.com",
            },
            {
                "url": "https://images.pexels.com/photos/3993212/pexels-photo-3993212.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": "https://images.pexels.com/photos/3993212/pexels-photo-3993212.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Natural beauty and wellness",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "pexels_url": "https://www.pexels.com",
            },
            {
                "url": "https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": "https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Glowing healthy skin",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "pexels_url": "https://www.pexels.com",
            },
        ]
        return bank[:count]

# ---------- Content generation ----------
class ContentGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.product_db = ProductDatabase(config)
        self.image_manager = ImageManager(config)

        self.intro_templates = [
            "Hey gorgeous! ✨ If you've been searching for the ultimate guide to {keyword}, you've landed in exactly the right place.",
            "Beauty lovers, gather around! 💕 Today we're diving deep into everything you need to know about {keyword}.",
            "Ready to transform your beauty routine? I'm so excited to share this comprehensive guide to {keyword} with you!",
            "If {keyword} has been on your wishlist but you don't know where to start, this guide is for you, babe!",
        ]
        self.conclusion_templates = [
            "There you have it, beauties! Your complete guide to {keyword}. Remember, consistency is key when it comes to any beauty routine.",
            "I hope this guide helps you on your {keyword} journey! What's your favorite tip from this post?",
            "That's a wrap on our {keyword} deep dive! I'd love to hear about your experience - drop a comment below!",
            "Thanks for joining me on this {keyword} adventure! Remember, the best beauty routine is the one you'll actually stick to.",
        ]

    def generate_seo_title(self, keyword: str) -> str:
        templates = [
            f"{keyword.title()}: Complete Guide for {datetime.now().year}",
            f"The Ultimate {keyword.title()} Guide That Actually Works",
            f"{keyword.title()}: Step-by-Step Tutorial + Tips",
            f"How to Master {keyword.title()} Like a Pro",
            f"Everything You Need to Know About {keyword.title()}",
            f"{keyword.title()}: Beginner's Guide + Product Recs",
            f"The Best {keyword.title()} Tips for Glowing Skin",
        ]
        title = random.choice(templates)
        if len(title) > self.config.MAX_TITLE_LENGTH:
            title = random.choice([
                f"{keyword.title()}: Complete Guide",
                f"Ultimate {keyword.title()} Guide",
                f"{keyword.title()}: Tips That Work",
            ])
        return title

    def generate_meta_description(self, keyword: str, title: str) -> str:
        templates = [
            f"Discover the best {keyword} tips and products. Our complete guide covers everything for glowing, healthy skin. Expert advice + product recommendations inside!",
            f"Learn {keyword} like a pro with our step-by-step guide. Includes product recommendations, tips, and everything you need for amazing results.",
            f"Master {keyword} with our comprehensive guide. From beginner tips to expert techniques, plus the best products that actually work.",
        ]
        meta = random.choice(templates)
        if len(meta) > self.config.META_DESC_LENGTH:
            meta = f"Complete {keyword} guide with expert tips, product recommendations, and step-by-step instructions for glowing, healthy skin."
        return meta[:self.config.META_DESC_LENGTH]

    def generate_labels(self, keyword: str) -> List[str]:
        base = ["beauty", "skincare", "beauty tips", "glow with helen"]
        parts = [w.lower() for w in keyword.split() if len(w) > 2]
        contextual: List[str] = []
        if any(t in keyword.lower() for t in ["skincare", "skin", "face"]):
            contextual += ["skincare routine", "healthy skin"]
        if any(t in keyword.lower() for t in ["makeup", "beauty", "cosmetic"]):
            contextual += ["makeup tips", "beauty routine"]
        if "routine" in keyword.lower():
            contextual.append("daily routine")
        labels = list(dict.fromkeys(base + parts + contextual))[:8]
        return labels

    @staticmethod
    def _img_block(img: Dict) -> str:
        if not img:
            return ""
        return (
            f'<figure class="post-image">'
            f'<img src="{img.get("url", "")}" alt="{img.get("alt", "")}" loading="lazy" />'
            f'<figcaption>Photo by <a href="{img.get("photographer_url", "#")}" target="_blank" rel="noopener">{img.get("photographer", "Pexels")}</a></figcaption>'
            f'</figure>'
        )

    def create_structured_content(self, keyword: str, products: List[Dict], images: List[Dict]) -> str:
        intro = random.choice(self.intro_templates).format(keyword=keyword)
        conclusion = random.choice(self.conclusion_templates).format(keyword=keyword)

        sections: List[str] = []

        hero_html = self._img_block(images[0]) if images else ""
        sections.append(f"""
<div class="intro-section">
    <p>{intro} I'm Helen, and today we're diving deep into everything you need to know about {keyword}.</p>
    <p>Whether you're a complete beginner or looking to level up your current routine, this comprehensive guide will walk you through step-by-step techniques, product recommendations, and insider tips that actually work.</p>
    {hero_html}
</div>
""")

        product0_link = self.product_db.create_affiliate_link(products[0]) if len(products) > 0 else ""
        sections.append(f"""
<h2>What is {keyword.title()}?</h2>
<p>Let's start with the basics, shall we? {keyword.title()} is more than just a beauty trend – it's a comprehensive approach that focuses on enhancing your natural beauty while maintaining healthy, glowing skin.</p>
<p>Here's what makes {keyword} so special and why it's taking the beauty world by storm:</p>
<ul>
    <li><strong>Promotes healthy, radiant skin:</strong> Works with your skin's natural processes rather than against them</li>
    <li><strong>Uses gentle, effective ingredients:</strong> No harsh chemicals that can damage your precious skin barrier</li>
    <li><strong>Suitable for most skin types:</strong> Adaptable techniques that work whether you have oily, dry, or combination skin</li>
    <li><strong>Focuses on long-term results:</strong> Sustainable beauty practices that deliver lasting improvements</li>
    <li><strong>Budget-friendly options available:</strong> You don't need to break the bank to see amazing results</li>
</ul>
<p>One product that's been absolutely revolutionary in my {keyword} journey is {product0_link}. This little miracle worker has completely transformed my routine, and I can't recommend it enough!</p>
""")

        if len(images) > 1:
            product1_link = self.product_db.create_affiliate_link(products[1]) if len(products) > 1 else ""
            sections.append(f"""
<h2>Step-by-Step {keyword.title()} Guide</h2>
{self._img_block(images[1])}
<p>Now let's get into the nitty-gritty! Here's my foolproof method that I've perfected over years of trial and error:</p>
<h3>Step 1: Preparation is Everything</h3>
<p>Before we dive in, make sure you're starting with a clean slate. Always begin with freshly washed hands and a thoroughly cleansed face. This step is crucial because it ensures maximum product absorption and prevents any bacteria from interfering with your routine.</p>
<h3>Step 2: Apply Your Key Products</h3>
<p>This is where the magic happens! {product1_link} has been my holy grail for this step. Apply it evenly using gentle patting motions – never rub or pull at your delicate skin.</p>
<h3>Step 3: Lock Everything In</h3>
<p>Seal in all that goodness with a quality moisturizer. And if you're doing this routine in the morning, sunscreen is absolutely non-negotiable.</p>
<p>Remember: consistency beats perfection every single time. It's better to do a simple routine religiously than a complicated one sporadically.</p>
""")

        product2_link = self.product_db.create_affiliate_link(products[2]) if len(products) > 2 else ""
        sections.append(f"""
<h2>Common {keyword.title()} Mistakes to Avoid</h2>
<p>Let's talk about the mistakes I see people making all the time – and trust me, I've made most of these myself when I was starting out!</p>
<h3>❌ Mistake #1: Using Too Much Product</h3>
<p>Less is more with {keyword}. Start with small amounts and build up gradually to avoid irritation.</p>
<h3>❌ Mistake #2: Being Inconsistent</h3>
<p>Results come from consistency, not perfection. A simple daily routine beats a complex once-a-week ritual.</p>
<h3>❌ Mistake #3: Wrong Product Selection</h3>
<p>Not all products are created equal. {product2_link} is one of my top picks because it's gentle, effective, and delivers results without overwhelming your skin.</p>
""")

        sections.append(f"""
<h2>Top Tips for {keyword.title()}</h2>
<ul>
    <li>Patch test new products before applying them to your whole face.</li>
    <li>Introduce one active ingredient at a time so you can tell how your skin reacts.</li>
    <li>Use sunscreen every morning — the most important anti-aging product you’ll ever own.</li>
    <li>Be patient: skin improvements take time—usually several weeks to months.</li>
</ul>
<h2>FAQ</h2>
<h3>How often should I do this routine?</h3>
<p>Start with a simple morning and night routine. Introduce actives like retinol slowly (1–2x per week) and ramp up as your skin tolerates it.</p>
<div class="conclusion">
    <p>{conclusion}</p>
</div>
""")

        return "\n".join(sections)

# ---------- Blogger publisher (optional) ----------
class BloggerPublisher:
    """Publish to Blogger using Google APIs (only if available)."""

    def __init__(self, config: Config):
        self.config = config
        self.enabled = OPTIONAL_IMPORTS["google_apis"] and bool(config.BLOGGER_BLOG_ID)

    def publish(self, title: str, html: str, labels: List[str]) -> Dict:
        if not self.enabled:
            raise RuntimeError("Google APIs not available or BLOGGER_BLOG_ID not set.")
        try:
            # This assumes default ADC or service account is properly configured.
            service = build("blogger", "v3")
            body = {"kind": "blogger#post", "title": title, "content": html, "labels": labels}
            post = service.posts().insert(blogId=self.config.BLOGGER_BLOG_ID, body=body, isDraft=False).execute()
            return {"id": post.get("id"), "url": post.get("url")}
        except Exception as e:
            logger.exception("Failed to publish to Blogger")
            raise

# ---------- Utilities ----------
def save_post_to_file(title: str, html: str, filename: str = "post.html") -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"<!-- {title} -->\n")
            f.write(html)
        logger.info(f"Saved post to {filename}")
    except Exception as e:
        logger.error(f"Error saving post: {e}")

def generate_example_post() -> Dict:
    cfg = Config()
    gen = ContentGenerator(cfg)
    keyword = "glass skin routine"
    products = gen.product_db.find_relevant_products(keyword, count=3)
    images = gen.image_manager.search_pexels_images(keyword, count=3)
    html = gen.create_structured_content(keyword, products, images)
    title = gen.generate_seo_title(keyword)
    meta = gen.generate_meta_description(keyword, title)
    labels = gen.generate_labels(keyword)
    save_post_to_file(title, html, filename="example_post.html")
    return {"title": title, "meta": meta, "labels": labels, "html": html}

# ---------- Streamlit UI ----------
def run_streamlit_app():
    st.set_page_config(page_title="✨ Glow AI Agent - Beauty Blog Generator", page_icon="✨", layout="wide")
    st.title("✨ Glow AI Agent")
    st.markdown("Generate SEO-optimized **beauty & fashion blog posts** with Amazon affiliate products.")

    cfg = Config()
    issues = cfg.validate()
    if issues:
        with st.expander("Configuration notices"):
            for msg in issues:
                st.info(f"• {msg}")

    keyword = st.text_input("Enter a beauty/fashion keyword", "glass skin routine")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        generate_btn = st.button("Generate Blog Post", type="primary")
    with col2:
        trends_btn = st.button("Suggest Trending Topics")
    with col3:
        publish_toggle = st.toggle("Publish to Blogger", value=False, help="Requires Google API creds + BLOGGER_BLOG_ID")

    if trends_btn:
        ta = TrendAnalyzer(cfg)
        topics = ta.get_trending_topics()
        if topics:
            st.subheader("🔥 Trending Topics")
            st.write(", ".join([t["keyword"] for t in topics]))
        else:
            st.info("No trends available (pytrends not installed or API limited).")

    if generate_btn:
        gen = ContentGenerator(cfg)
        products = gen.product_db.find_relevant_products(keyword, count=3)
        images = gen.image_manager.search_pexels_images(keyword, count=3)

        title = gen.generate_seo_title(keyword)
        meta = gen.generate_meta_description(keyword, title)
        labels = gen.generate_labels(keyword)
        html = gen.create_structured_content(keyword, products, images)

        st.subheader("📝 Title")
        st.write(title)
        st.subheader("🔑 Meta Description")
        st.write(meta)
        st.subheader("🏷️ Labels")
        st.write(", ".join(labels))

        st.subheader("📄 Blog Post Preview")
        st.components.v1.html(html, height=700, scrolling=True)

        st.download_button(
            label="💾 Download HTML",
            data=html,
            file_name=f"{title.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True,
        )

        if publish_toggle:
            if not OPTIONAL_IMPORTS["google_apis"] or not cfg.BLOGGER_BLOG_ID:
                st.error("Google APIs not available or BLOGGER_BLOG_ID not set.")
            else:
                try:
                    publisher = BloggerPublisher(cfg)
                    result = publisher.publish(title, html, labels)
                    st.success(f"Published! Post ID: {result.get('id')}")
                    if result.get("url"):
                        st.markdown(f"[Open post]({result['url']})")
                except Exception as e:
                    st.error(f"Failed to publish: {e}")

# ---------- Entrypoint ----------
if __name__ == "__main__":
    if OPTIONAL_IMPORTS["streamlit"]:
        run_streamlit_app()
    else:
        # CLI fallback (no Streamlit)
        logger.info("Streamlit not installed; running CLI example...")
        data = generate_example_post()
        print("Title:", data["title"])
        print("Meta:", data["meta"])
        print("Labels:", ", ".join(data["labels"]))
        print("Saved preview to example_post.html")  
