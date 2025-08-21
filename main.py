#!/usr/bin/env python3
"""
Glow AI Agent - Complete Beauty & Fashion Blog Content Creator
Automatically generates SEO-optimized blog posts for "Glow With Helen"
"""

import os
import sys
import requests
import json
import random
import time
import webbrowser
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union
import re
from dataclasses import dataclass
import pickle
import logging
from urllib.parse import urlparse, parse_qs

# Import validation and graceful degradation for optional dependencies
OPTIONAL_IMPORTS = {}

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    OPTIONAL_IMPORTS['google_apis'] = True
except ImportError as e:
    print(f"⚠️  Google API libraries not installed: {e}")
    print("Install with: pip install google-api-python-client google-auth-oauthlib")
    OPTIONAL_IMPORTS['google_apis'] = False

try:
    import pytrends
    from pytrends.request import TrendReq
    OPTIONAL_IMPORTS['pytrends'] = True
except ImportError:
    print("⚠️  PyTrends not installed. Using fallback trend data.")
    print("Install with: pip install pytrends")
    OPTIONAL_IMPORTS['pytrends'] = False

try:
    from bs4 import BeautifulSoup
    OPTIONAL_IMPORTS['beautifulsoup'] = True
except ImportError:
    print("⚠️  BeautifulSoup not installed. Web scraping limited.")
    print("Install with: pip install beautifulsoup4")
    OPTIONAL_IMPORTS['beautifulsoup'] = False

try:
    import schedule
    OPTIONAL_IMPORTS['schedule'] = True
except ImportError:
    print("⚠️  Schedule library not installed. No automated scheduling.")
    print("Install with: pip install schedule")
    OPTIONAL_IMPORTS['schedule'] = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('glow_ai.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
@dataclass
class Config:
    # API Keys (Set these as environment variables for security)
    PEXELS_API_KEY: str = os.getenv('PEXELS_API_KEY', '')
    GOOGLE_TRENDS_API_KEY: str = os.getenv('GOOGLE_TRENDS_API_KEY', '')
    BLOGGER_CLIENT_ID: str = os.getenv('BLOGGER_CLIENT_ID', '')
    BLOGGER_CLIENT_SECRET: str = os.getenv('BLOGGER_CLIENT_SECRET', '')
    BLOGGER_BLOG_ID: str = os.getenv('BLOGGER_BLOG_ID', '')
    
    # Amazon Affiliate Tag
    AMAZON_AFFILIATE_TAG: str = "helenbeautysh-20"
    
    # Blog Settings
    BLOG_NAME: str = "Glow With Helen"
    AUTHOR_NAME: str = "Helen"
    
    # Advanced Settings
    MAX_POSTS_PER_DAY: int = 3
    MIN_KEYWORD_INTEREST: int = 70
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 30
    
    # Content Settings
    MIN_CONTENT_LENGTH: int = 1500  # characters
    MAX_TITLE_LENGTH: int = 60
    META_DESC_LENGTH: int = 155
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not self.PEXELS_API_KEY:
            issues.append("PEXELS_API_KEY not set - images will use placeholders")
        
        if not self.BLOGGER_CLIENT_ID or not self.BLOGGER_CLIENT_SECRET:
            issues.append("Blogger credentials not set - publishing disabled")
            
        if not self.BLOGGER_BLOG_ID:
            issues.append("BLOGGER_BLOG_ID not set - publishing disabled")
            
        return issues

class TrendAnalyzer:
    """Advanced trend analysis using multiple sources"""
    
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
        
        if OPTIONAL_IMPORTS['pytrends']:
            self.pytrends = TrendReq(hl='en-US', tz=360)
        else:
            self.pytrends = None
    
    def get_google_trends(self, keywords: List[str], timeframe: str = 'today 3-m') -> Dict:
        """Get real Google Trends data"""
        if not self.pytrends:
            return {}
        
        try:
            self.pytrends.build_payload(keywords, timeframe=timeframe, geo='US')
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                # Get average interest for each keyword
                trends = {}
                for keyword in keywords:
                    if keyword in interest_over_time.columns:
                        trends[keyword] = {
                            'interest': int(interest_over_time[keyword].mean()),
                            'trend': 'rising' if interest_over_time[keyword].iloc[-1] > interest_over_time[keyword].iloc[0] else 'falling'
                        }
                return trends
        except Exception as e:
            logger.error(f"Error getting Google Trends: {e}")
            
        return {}
    
    def get_pinterest_trends(self) -> List[Dict]:
        """Simulate Pinterest trends (replace with actual API when available)"""
        # Pinterest Trends API is limited, so we simulate based on seasonal patterns
        current_month = datetime.now().month
        seasonal_trends = {
            12: ["winter skincare", "holiday makeup", "party nails"],  # December
            1: ["new year glow up", "dry skin remedies", "detox skincare"],  # January
            2: ["valentine's makeup", "anti-aging", "self care routine"],  # February
            3: ["spring skincare", "fresh makeup", "allergy skin care"],  # March
            4: ["easter makeup", "spring cleaning skincare", "refresh routine"],  # April
            5: ["mother's day gifts", "spring trends", "sun protection"],  # May
            6: ["summer skincare", "waterproof makeup", "wedding beauty"],  # June
            7: ["sun care", "beach waves", "sweat proof makeup"],  # July
            8: ["back to school", "quick routines", "budget beauty"],  # August
            9: ["fall skincare", "autumn makeup", "transition routine"],  # September
            10: ["halloween makeup", "fall trends", "cozy skincare"],  # October
            11: ["thanksgiving prep", "dry skin solutions", "holiday prep"]  # November
        }
        
        trends = seasonal_trends.get(current_month, ["general skincare", "makeup tips", "beauty routine"])
        return [{"keyword": trend, "source": "pinterest", "interest": random.randint(75, 95)} for trend in trends]
    
    def analyze_competition(self, keyword: str) -> str:
        """Analyze keyword competition level"""
        # Simple competition analysis based on keyword characteristics
        if len(keyword.split()) <= 2:
            return "high"
        elif "tutorial" in keyword or "guide" in keyword:
            return "medium"
        elif len(keyword.split()) >= 4:
            return "low"
        else:
            return "medium"
    
    def get_trending_topics(self) -> List[Dict]:
        """Get comprehensive trending topics from multiple sources"""
        logger.info("Analyzing trending topics...")
        
        trending_topics = []
        
        # Get Google Trends data
        google_trends = self.get_google_trends(self.beauty_keywords[:5])  # Limit to avoid rate limits
        
        for keyword, data in google_trends.items():
            if data['interest'] >= self.config.MIN_KEYWORD_INTEREST:
                trending_topics.append({
                    "keyword": keyword,
                    "interest": data['interest'],
                    "competition": self.analyze_competition(keyword),
                    "trend": data['trend'],
                    "source": "google_trends"
                })
        
        # Get Pinterest trends
        pinterest_trends = self.get_pinterest_trends()
        trending_topics.extend(pinterest_trends)
        
        # Add some evergreen topics with simulated data if no real trends
        if not trending_topics:
            evergreen_topics = [
                {"keyword": "retinol for beginners", "interest": 85, "competition": "low", "trend": "steady"},
                {"keyword": "niacinamide benefits", "interest": 78, "competition": "medium", "trend": "rising"},
                {"keyword": "glass skin routine", "interest": 82, "competition": "medium", "trend": "rising"},
                {"keyword": "affordable skincare dupes", "interest": 88, "competition": "low", "trend": "steady"},
                {"keyword": "korean beauty secrets", "interest": 79, "competition": "medium", "trend": "steady"}
            ]
            trending_topics.extend(evergreen_topics)
        
        # Filter and sort by interest
        filtered_topics = [
            topic for topic in trending_topics 
            if topic["interest"] >= self.config.MIN_KEYWORD_INTEREST and topic["competition"] != "high"
        ]
        
        # Sort by interest level
        filtered_topics.sort(key=lambda x: x["interest"], reverse=True)
        
        logger.info(f"Found {len(filtered_topics)} trending topics")
        return filtered_topics[:10]  # Return top 10

class ProductDatabase:
    """Comprehensive beauty product database with Amazon affiliate integration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.products = {
            "skincare": [
                {"name": "CeraVe Foaming Facial Cleanser", "id": "B077TGQZPX", "price": "$12.99", "rating": "4.5", "category": "cleanser"},
                {"name": "The Ordinary Niacinamide 10% + Zinc 1%", "id": "B06XHW8TQL", "price": "$7.20", "rating": "4.3", "category": "serum"},
                {"name": "Neutrogena Ultra Sheer Sunscreen SPF 55", "id": "B002JAYMEE", "price": "$8.47", "rating": "4.4", "category": "sunscreen"},
                {"name": "Olay Regenerist Retinol 24 Night Moisturizer", "id": "B07MVJC3J8", "price": "$18.99", "rating": "4.2", "category": "moisturizer"},
                {"name": "Paula's Choice 2% BHA Liquid Exfoliant", "id": "B00949CTQQ", "price": "$29.50", "rating": "4.4", "category": "exfoliant"},
                {"name": "Drunk Elephant Vitamin C Serum", "id": "B071K62ZMX", "price": "$80.00", "rating": "4.1", "category": "serum"},
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
            ]
        }
    
    def find_relevant_products(self, keyword: str, count: int = 3) -> List[Dict]:
        """Find products relevant to the keyword"""
        keyword_lower = keyword.lower()
        relevant_products = []
        
        # Keyword to category mapping
        category_mapping = {
            "cleanser": ["cleanser", "cleansing", "wash"],
            "serum": ["serum", "vitamin c", "niacinamide", "retinol"],
            "moisturizer": ["moisturizer", "cream", "hydrat"],
            "sunscreen": ["sunscreen", "spf", "sun protection"],
            "foundation": ["foundation", "base makeup"],
            "eyeshadow": ["eyeshadow", "eye makeup", "palette"],
            "mascara": ["mascara", "lashes"],
            "lipstick": ["lipstick", "lip"],
            "tools": ["tool", "brush", "mirror"]
        }
        
        # Find products by keyword relevance
        for category, products in self.products.items():
            for product in products:
                # Check if keyword matches product category or name
                if any(term in keyword_lower for term in category_mapping.get(product.get('category', ''), [])):
                    relevant_products.append(product)
                elif any(term in product['name'].lower() for term in keyword_lower.split()):
                    relevant_products.append(product)
        
        # If no specific matches, get random products from skincare (most versatile)
        if not relevant_products:
            relevant_products = self.products['skincare']
        
        # Remove duplicates and limit count
        seen = set()
        unique_products = []
        for product in relevant_products:
            if product['id'] not in seen:
                unique_products.append(product)
                seen.add(product['id'])
        
        return random.sample(unique_products, min(count, len(unique_products)))
    
    def create_affiliate_link(self, product: Dict) -> str:
        """Create Amazon affiliate link with proper formatting"""
        base_url = f"https://www.amazon.com/dp/{product['id']}"
        affiliate_url = f"{base_url}/?tag={self.config.AMAZON_AFFILIATE_TAG}"
        return f'<a href="{affiliate_url}" target="_blank" rel="nofollow sponsored">{product["name"]}</a>'

class ImageManager:
    """Advanced image management with Pexels API integration"""
    
    def __init__(self, config: Config):
        self.config = config
        self.headers = {"Authorization": config.PEXELS_API_KEY} if config.PEXELS_API_KEY else {}
        self.cache = {}  # Simple in-memory cache
    
    def search_pexels_images(self, query: str, count: int = 3) -> List[Dict]:
        """Search for high-quality images on Pexels"""
        if not self.config.PEXELS_API_KEY:
            return self._get_placeholder_images(query, count)
        
        # Check cache first
        cache_key = f"{query}_{count}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        url = "https://api.pexels.com/v1/search"
        params = {
            "query": f"{query} beauty skincare makeup",
            "per_page": count + 2,  # Get extra images for variety
            "orientation": "landscape",
            "size": "large"
        }
        
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                params=params, 
                timeout=self.config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                images = []
                
                for photo in data.get("photos", [])[:count]:
                    images.append({
                        "url": photo["src"]["large"],
                        "url_medium": photo["src"]["medium"],
                        "alt": f"{query} - {photo.get('alt', 'Beauty and skincare image')}",
                        "photographer": photo["photographer"],
                        "photographer_url": photo["photographer_url"],
                        "pexels_url": photo["url"]
                    })
                
                # Cache the results
                self.cache[cache_key] = images
                logger.info(f"Found {len(images)} images for '{query}'")
                return images
                
        except requests.RequestException as e:
            logger.error(f"Error fetching Pexels images: {e}")
        
        return self._get_placeholder_images(query, count)
    
    def _get_placeholder_images(self, query: str, count: int) -> List[Dict]:
        """Generate placeholder images when API is not available"""
        placeholder_images = [
            {
                "url": f"https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": f"https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Beautiful skincare routine",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "pexels_url": "https://www.pexels.com"
            },
            {
                "url": f"https://images.pexels.com/photos/3993212/pexels-photo-3993212.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": f"https://images.pexels.com/photos/3993212/pexels-photo-3993212.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Natural beauty and wellness",
                "photographer": "Pexels", 
                "photographer_url": "https://www.pexels.com",
                "pexels_url": "https://www.pexels.com"
            },
            {
                "url": f"https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=800",
                "url_medium": f"https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=600",
                "alt": f"{query} - Glowing healthy skin",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com", 
                "pexels_url": "https://www.pexels.com"
            }
        ]
        
        return placeholder_images[:count]

class ContentGenerator:
    """Advanced AI-powered content generation with SEO optimization"""
    
    def __init__(self, config: Config):
        self.config = config
        self.product_db = ProductDatabase(config)
        self.image_manager = ImageManager(config)
        
        # Content templates and patterns
        self.intro_templates = [
            "Hey gorgeous! ✨ If you've been searching for the ultimate guide to {keyword}, you've landed in exactly the right place.",
            "Beauty lovers, gather around! 💕 Today we're diving deep into everything you need to know about {keyword}.",
            "Ready to transform your beauty routine? I'm so excited to share this comprehensive guide to {keyword} with you!",
            "If {keyword} has been on your wishlist but you don't know where to start, this guide is for you, babe!"
        ]
        
        self.conclusion_templates = [
            "There you have it, beauties! Your complete guide to {keyword}. Remember, consistency is key when it comes to any beauty routine.",
            "I hope this guide helps you on your {keyword} journey! What's your favorite tip from this post?",
            "That's a wrap on our {keyword} deep dive! I'd love to hear about your experience - drop a comment below!",
            "Thanks for joining me on this {keyword} adventure! Remember, the best beauty routine is the one you'll actually stick to."
        ]
    
    def generate_seo_title(self, keyword: str) -> str:
        """Generate SEO-optimized title with A/B testing variations"""
        templates = [
            f"{keyword.title()}: Complete Guide for {datetime.now().year}",
            f"The Ultimate {keyword.title()} Guide That Actually Works",
            f"{keyword.title()}: Step-by-Step Tutorial + Tips",
            f"How to Master {keyword.title()} Like a Pro",
            f"Everything You Need to Know About {keyword.title()}",
            f"{keyword.title()}: Beginner's Guide + Product Recs",
            f"The Best {keyword.title()} Tips for Glowing Skin"
        ]
        
        title = random.choice(templates)
        
        # Ensure title is within SEO limits
        if len(title) > self.config.MAX_TITLE_LENGTH:
            # Try shorter template
            short_templates = [
                f"{keyword.title()}: Complete Guide",
                f"Ultimate {keyword.title()} Guide",
                f"{keyword.title()}: Tips That Work"
            ]
            title = random.choice(short_templates)
        
        return title
    
    def generate_meta_description(self, keyword: str, title: str) -> str:
        """Generate compelling meta description"""
        templates = [
            f"Discover the best {keyword} tips and products. Our complete guide covers everything for glowing, healthy skin. Expert advice + product recommendations inside!",
            f"Learn {keyword} like a pro with our step-by-step guide. Includes product recommendations, tips, and everything you need for amazing results.",
            f"Master {keyword} with our comprehensive guide. From beginner tips to expert techniques, plus the best products that actually work.",
        ]
        
        meta_desc = random.choice(templates)
        
        # Ensure within character limits
        if len(meta_desc) > self.config.META_DESC_LENGTH:
            meta_desc = f"Complete {keyword} guide with expert tips, product recommendations, and step-by-step instructions for glowing, healthy skin."
        
        return meta_desc[:self.config.META_DESC_LENGTH]
    
    def generate_labels(self, keyword: str) -> List[str]:
        """Generate relevant blog labels/tags"""
        base_labels = ["beauty", "skincare", "beauty tips", "glow with helen"]
        
        # Extract keywords
        keyword_parts = [word.lower() for word in keyword.split() if len(word) > 2]
        
        # Add contextual labels
        contextual_labels = []
        if any(term in keyword.lower() for term in ["skincare", "skin", "face"]):
            contextual_labels.extend(["skincare routine", "healthy skin"])
        if any(term in keyword.lower() for term in ["makeup", "beauty", "cosmetic"]):
            contextual_labels.extend(["makeup tips", "beauty routine"])
        if "routine" in keyword.lower():
            contextual_labels.append("daily routine")
        
        # Combine all labels
        all_labels = base_labels + keyword_parts + contextual_labels
        
        # Remove duplicates and limit to 8 labels (Blogger recommendation)
        unique_labels = list(set(all_labels))[:8]
        
        return unique_labels
    
    def create_structured_content(self, keyword: str, products: List[Dict], images: List[Dict]) -> str:
        """Generate comprehensive, structured blog content"""
        
        intro = random.choice(self.intro_templates).format(keyword=keyword)
        conclusion = random.choice(self.conclusion_templates).format(keyword=keyword)
        
        # Main content sections
        sections = []
        
        # Introduction with hero image
        sections.append(f"""
        <div class="intro-section">
            <p>{intro} I'm Helen, and today we're diving deep into everything you need to know about {keyword}.</p>
            
            <p>Whether you're a complete beginner or looking to level up your current routine, this comprehensive guide will walk you through step-by-step techniques, product recommendations, and insider tips that actually work.</p>
            
            {self._create_image_html(images[0]) if images else ''}
        </div>
        """)
        
        # What is [keyword] section
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
        
        <p>One product that's been absolutely revolutionary in my {keyword} journey is {self.product_db.create_affiliate_link(products[0])}. This little miracle worker has completely transformed my routine, and I can't recommend it enough!</p>
        """)
        
        # Step-by-step guide
        if len(images) > 1:
            sections.append(f"""
            <h2>Step-by-Step {keyword.title()} Guide</h2>
            
            {self._create_image_html(images[1])}
            
            <p>Now let's get into the nitty-gritty! Here's my foolproof method that I've perfected over years of trial and error:</p>
            
            <h3>Step 1: Preparation is Everything</h3>
            <p>Before we dive in, make sure you're starting with a clean slate. Always begin with freshly washed hands and a thoroughly cleansed face. This step is crucial because it ensures maximum product absorption and prevents any bacteria from interfering with your routine.</p>
            
            <p>Remove any makeup thoroughly using a gentle cleanser or micellar water. I love using a double cleanse method – it really makes a difference in how well your products absorb.</p>
            
            <h3>Step 2: Apply Your Key Products</h3>
            <p>This is where the magic happens! {self.product_db.create_affiliate_link(products[1])} has been my holy grail for this step. Apply it evenly using gentle patting motions – never rub or pull at your delicate skin.</p>
            
            <p>Take your time here. Allow each layer to absorb completely before adding the next product. I know it's tempting to rush, but patience is truly key to getting the best results.</p>
            
            <h3>Step 3: Lock Everything In</h3>
            <p>Don't forget this crucial final step! Seal in all that goodness with a quality moisturizer. And if you're doing this routine in the morning, sunscreen is absolutely non-negotiable.</p>
            
            <p>Remember: consistency beats perfection every single time. It's better to do a simple routine religiously than a complicated one sporadically.</p>
            """)
        
        # Common mistakes section
        sections.append(f"""
        <h2>Common {keyword.title()} Mistakes to Avoid</h2>
        
        <p>Let's talk about the mistakes I see people making all the time – and trust me, I've made most of these myself when I was starting out!</p>
        
        <h3>❌ Mistake #1: Using Too Much Product</h3>
        <p>I get it – when you love a product, you want to slather it on. But less is definitely more when it comes to {keyword}. Start with small amounts and build up gradually. Your skin needs time to adjust, and overdoing it can actually cause irritation or breakouts.</p>
        
        <h3>❌ Mistake #2: Being Inconsistent</h3>
        <p>Results come from consistency, not perfection. I'd rather you do a simple {keyword} routine every day than an elaborate one once a week. Set reminders on your phone if you need to – whatever it takes to make it a habit!</p>
        
        <h3>❌ Mistake #3: Wrong Product Selection</h3>
        <p>Not all products are created equal, and what works for your favorite influencer might not work for your skin. That's why I'm so careful about my recommendations. {self.product_db.
