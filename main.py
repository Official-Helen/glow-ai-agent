#!/usr/bin/env python3
"""
Glow AI Agent - Beauty & Fashion Blog Content Creator
Automatically generates SEO-optimized blog posts for "Glow With Helen"
"""

import os
import requests
import json
import random
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import re
from dataclasses import dataclass
import pickle

# Try to import Google API libraries
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from google.auth.transport.requests import Request
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    print("⚠️  Google API libraries not found. Blogger publishing will be disabled.")
    print("To enable Blogger publishing, install: pip install google-api-python-client google-auth-oauthlib")
    GOOGLE_APIS_AVAILABLE = False

# Configuration
@dataclass
class Config:
    # API Keys (Set these as environment variables)
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

class TrendScraper:
    """Handles scraping trends from Google Trends and Pinterest"""
    
    def __init__(self, config: Config):
        self.config = config
        self.beauty_keywords = [
            "skincare routine", "makeup trends", "beauty tips", "anti aging",
            "acne treatment", "hair care", "nail art", "fashion trends",
            "skincare ingredients", "makeup tutorial", "beauty hacks",
            "natural skincare", "korean skincare", "retinol", "niacinamide",
            "vitamin c serum", "hyaluronic acid", "face masks", "sunscreen"
        ]
    
    def get_trending_topics(self) -> List[Dict]:
        """Get trending beauty/fashion topics"""
        trending_topics = []
        
        # Simulate trend data (replace with actual API calls)
        sample_trends = [
            {"keyword": "glass skin routine", "interest": 85, "competition": "medium"},
            {"keyword": "retinol for beginners", "interest": 78, "competition": "low"},
            {"keyword": "winter skincare tips", "interest": 92, "competition": "high"},
            {"keyword": "affordable makeup dupes", "interest": 88, "competition": "medium"},
            {"keyword": "niacinamide benefits", "interest": 76, "competition": "low"},
            {"keyword": "korean beauty secrets", "interest": 83, "competition": "medium"},
        ]
        
        # Filter for good opportunities (high interest, not overly saturated)
        for trend in sample_trends:
            if trend["interest"] > 75 and trend["competition"] != "high":
                trending_topics.append(trend)
        
        return trending_topics[:3]  # Return top 3 opportunities

class ProductFinder:
    """Finds relevant Amazon affiliate products"""
    
    def __init__(self, config: Config):
        self.config = config
        self.beauty_products = {
            "skincare": [
                {"name": "CeraVe Foaming Facial Cleanser", "id": "B077TGQZPX", "price": "$12.99"},
                {"name": "The Ordinary Niacinamide 10% + Zinc 1%", "id": "B06XHW8TQL", "price": "$7.20"},
                {"name": "Neutrogena Ultra Sheer Sunscreen SPF 55", "id": "B002JAYMEE", "price": "$8.47"},
                {"name": "Olay Regenerist Retinol 24 Night Moisturizer", "id": "B07MVJC3J8", "price": "$18.99"},
            ],
            "makeup": [
                {"name": "Maybelline Fit Me Matte Foundation", "id": "B07C2ZS7B8", "price": "$7.99"},
                {"name": "Urban Decay Naked Eyeshadow Palette", "id": "B004Q8U1ZA", "price": "$54.00"},
                {"name": "Fenty Beauty Gloss Bomb", "id": "B075BYKK7T", "price": "$19.00"},
            ],
            "tools": [
                {"name": "Foreo Luna Mini 3 Face Brush", "id": "B07VQZR8DK", "price": "$139.00"},
                {"name": "Revlon One-Step Hair Dryer", "id": "B01LSUQSB0", "price": "$59.99"},
                {"name": "Real Techniques Makeup Brush Set", "id": "B004TSF8R6", "price": "$19.99"},
            ]
        }
    
    def find_products(self, keyword: str, category: str = "skincare") -> List[Dict]:
        """Find relevant products based on keyword and category"""
        products = self.beauty_products.get(category, self.beauty_products["skincare"])
        return random.sample(products, min(3, len(products)))

class ImageFinder:
    """Finds relevant images from Pexels"""
    
    def __init__(self, config: Config):
        self.config = config
        self.headers = {"Authorization": config.PEXELS_API_KEY}
    
    def search_images(self, query: str, count: int = 3) -> List[Dict]:
        """Search for images on Pexels"""
        if not self.config.PEXELS_API_KEY:
            # Return placeholder images if no API key
            return [
                {
                    "url": "https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg",
                    "alt": f"Beautiful {query} image",
                    "photographer": "Pexels"
                } for _ in range(count)
            ]
        
        url = "https://api.pexels.com/v1/search"
        params = {
            "query": f"{query} beauty skincare",
            "per_page": count,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data.get("photos", []):
                    images.append({
                        "url": photo["src"]["large"],
                        "alt": f"{query} - {photo.get('alt', 'Beauty image')}",
                        "photographer": photo["photographer"]
                    })
                return images
        except Exception as e:
            print(f"Error fetching images: {e}")
        
        # Fallback to placeholder
        return self.search_images("", count)

class ContentGenerator:
    """Generates SEO-optimized blog content"""
    
    def __init__(self, config: Config):
        self.config = config
        self.product_finder = ProductFinder(config)
        self.image_finder = ImageFinder(config)
    
    def generate_seo_title(self, keyword: str) -> str:
        """Generate SEO-friendly title (max 60 chars)"""
        templates = [
            f"{keyword.title()}: Complete Guide for 2024",
            f"The Ultimate {keyword.title()} Guide",
            f"{keyword.title()}: Tips That Actually Work",
            f"How to {keyword.title()} Like a Pro",
            f"{keyword.title()}: Everything You Need to Know"
        ]
        
        title = random.choice(templates)
        return title[:60] if len(title) > 60 else title
    
    def generate_meta_description(self, keyword: str, title: str) -> str:
        """Generate meta description (150-160 chars)"""
        desc = f"Discover the best {keyword} tips and products. Our complete guide covers everything you need for glowing, healthy skin."
        return desc[:160] if len(desc) > 160 else desc
    
    def generate_labels(self, keyword: str) -> List[str]:
        """Generate relevant labels/tags"""
        base_labels = ["beauty", "skincare", "beauty tips"]
        keyword_parts = keyword.lower().split()
        
        labels = base_labels + keyword_parts
        # Remove duplicates and return unique labels
        return list(set(labels))[:8]  # Blogger recommends max 8 labels
    
    def create_affiliate_link(self, product: Dict) -> str:
        """Create Amazon affiliate link"""
        return f'<a href="https://www.amazon.com/dp/{product["id"]}/?tag={self.config.AMAZON_AFFILIATE_TAG}" target="_blank" rel="nofollow">{product["name"]}</a>'
    
    def generate_blog_post(self, topic: Dict) -> Dict:
        """Generate complete blog post content"""
        keyword = topic["keyword"]
        title = self.generate_seo_title(keyword)
        meta_desc = self.generate_meta_description(keyword, title)
        labels = self.generate_labels(keyword)
        
        # Get products and images
        products = self.product_finder.find_products(keyword)
        images = self.image_finder.search_images(keyword, 4)
        
        # Generate content sections
        content = self._generate_content_body(keyword, products, images)
        
        return {
            "title": title,
            "meta_description": meta_desc,
            "labels": labels,
            "content": content,
            "keyword": keyword
        }
    
    def _generate_content_body(self, keyword: str, products: List[Dict], images: List[Dict]) -> str:
        """Generate the main blog post content"""
        
        # Introduction
        intro = f"""
        <p>Hey gorgeous! ✨ If you've been searching for the ultimate guide to <strong>{keyword}</strong>, you've landed in exactly the right place. I'm Helen, and today we're diving deep into everything you need to know about {keyword}.</p>
        
        <p>Whether you're a complete beginner or looking to level up your current routine, this comprehensive guide will walk you through step-by-step techniques, product recommendations, and insider tips that actually work.</p>
        
        <img src="{images[0]['url']}" alt="{images[0]['alt']}" style="width:100%;height:auto;margin:20px 0;">
        <p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>
        """
        
        # Main sections
        sections = self._generate_sections(keyword, products, images[1:])
        
        # Conclusion
        conclusion = f"""
        <h2>Final Thoughts</h2>
        <p>There you have it, beauties! Your complete guide to {keyword}. Remember, consistency is key when it comes to any beauty routine. Start slowly, listen to your skin, and don't be afraid to adjust your approach as needed.</p>
        
        <p>What's your favorite tip from this guide? I'd love to hear about your {keyword} journey in the comments below! 💕</p>
        
        <img src="{images[-1]['url']}" alt="{images[-1]['alt']}" style="width:100%;height:auto;margin:20px 0;">
        <p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>
        
        <p style="font-style:italic;margin-top:30px;padding-top:20px;border-top:1px solid #eee;">
        This article may contain affiliate links. If you purchase through these links, I may earn a small commission at no extra cost to you.
        </p>
        """
        
        return intro + sections + conclusion
    
    def _generate_sections(self, keyword: str, products: List[Dict], images: List[Dict]) -> str:
        """Generate main content sections"""
        
        sections = []
        
        # Section 1: What is [keyword]
        sections.append(f"""
        <h2>What is {keyword.title()}?</h2>
        <p>Let's start with the basics. {keyword.title()} is more than just a beauty trend – it's a approach that focuses on enhancing your natural beauty while maintaining healthy skin.</p>
        
        <p>Here's what makes {keyword} so special:</p>
        <ul>
        <li>Promotes healthy, glowing skin</li>
        <li>Uses gentle, effective ingredients</li>
        <li>Suitable for most skin types</li>
        <li>Focuses on long-term results</li>
        </ul>
        
        <p>One product I absolutely recommend for this is {self.create_affiliate_link(products[0])}. It's been a game-changer in my routine!</p>
        """)
        
        # Section 2: Step-by-step guide
        if images:
            sections.append(f"""
            <h2>Step-by-Step {keyword.title()} Guide</h2>
            
            <img src="{images[0]['url']}" alt="{images[0]['alt']}" style="width:100%;height:auto;margin:20px 0;">
            <p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>
            
            <h3>Step 1: Preparation</h3>
            <p>Always start with clean hands and a fresh face. Remove any makeup and cleanse gently with a mild cleanser.</p>
            
            <h3>Step 2: Apply Your Products</h3>
            <p>This is where {self.create_affiliate_link(products[1])} really shines. Apply it evenly and allow it to absorb completely.</p>
            
            <h3>Step 3: Follow Up</h3>
            <p>Don't forget to moisturize and apply sunscreen during the day. Consistency is absolutely key!</p>
            """)
        
        # Section 3: Common mistakes
        sections.append(f"""
        <h2>Common {keyword.title()} Mistakes to Avoid</h2>
        <p>Even with the best intentions, it's easy to make mistakes. Here are the top ones I see:</p>
        
        <h3>Using Too Much Product</h3>
        <p>Less is definitely more when it comes to {keyword}. Start with small amounts and build up gradually.</p>
        
        <h3>Inconsistent Application</h3>
        <p>Results come from consistency, not perfection. It's better to do a simple routine daily than an elaborate one occasionally.</p>
        
        <h3>Wrong Product Choice</h3>
        <p>Not all products are created equal. That's why I love {self.create_affiliate_link(products[2])} – it's reliable and effective for most people.</p>
        """)
        
        return "".join(sections)

class BloggerPublisher:
    """Handles publishing to Blogger via API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Blogger API"""
        if not GOOGLE_APIS_AVAILABLE:
            print("❌ Google API libraries not available. Cannot authenticate with Blogger.")
            return
            
        try:
            # OAuth 2.0 setup for Blogger API
            SCOPES = ['https://www.googleapis.com/auth/blogger']
            
            creds = None
            # Token file stores the user's access and refresh tokens
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = Flow.from_client_config(
                        {
                            "web": {
                                "client_id": self.config.BLOGGER_CLIENT_ID,
                                "client_secret": self.config.BLOGGER_CLIENT_SECRET,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token"
                            }
                        },
                        SCOPES
                    )
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    
                    print("Please visit this URL to authorize the application:")
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(auth_url)
                    
                    code = input("Enter the authorization code: ")
                    flow.fetch_token(code=code)
                    creds = flow.credentials
                
                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('blogger', 'v3', credentials=creds)
            print("Successfully authenticated with Blogger API")
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            print("Continuing without Blogger publishing capability")
    
    def publish_post(self, post_data: Dict) -> Optional[str]:
        """Publish blog post to Blogger"""
        if not self.service:
            print("Blogger service not available. Post content:")
            print(f"Title: {post_data['title']}")
            print(f"Labels: {', '.join(post_data['labels'])}")
            print("Content:", post_data['content'][:200] + "...")
            return None
        
        try:
            post_body = {
                'title': post_data['title'],
                'content': post_data['content'],
                'labels': post_data['labels']
            }
            
            request = self.service.posts().insert(
                blogId=self.config.BLOGGER_BLOG_ID,
                body=post_body
            )
            
            response = request.execute()
            post_url = response.get('url')
            print(f"✅ Post published successfully: {post_url}")
            return post_url
            
        except Exception as e:
            print(f"Failed to publish post: {e}")
            return None

class GlowAIAgent:
    """Main AI Agent class that orchestrates the entire process"""
    
    def __init__(self):
        self.config = Config()
        self.trend_scraper = TrendScraper(self.config)
        self.content_generator = ContentGenerator(self.config)
        self.blogger_publisher = BloggerPublisher(self.config)
    
    def run_full_workflow(self):
        """Execute the complete workflow"""
        print("🌟 Starting Glow AI Agent workflow...")
        
        # Step 1: Get trending topics
        print("📊 Scraping trends...")
        trending_topics = self.trend_scraper.get_trending_topics()
        
        if not trending_topics:
            print("❌ No trending topics found")
            return
        
        print(f"✅ Found {len(trending_topics)} trending topics")
        
        # Step 2: Generate content for each topic
        for i, topic in enumerate(trending_topics, 1):
            print(f"\n📝 Generating post {i}: {topic['keyword']}")
            
            # Generate blog post
            post_data = self.content_generator.generate_blog_post(topic)
            
            print(f"✅ Generated post: '{post_data['title']}'")
            print(f"📊 Meta description: {post_data['meta_description']}")
            print(f"🏷️ Labels: {', '.join(post_data['labels'])}")
            
            # Step 3: Publish to Blogger
            print("🚀 Publishing to Blogger...")
            post_url = self.blogger_publisher.publish_post(post_data)
            
            if post_url:
                print(f"🎉 Successfully published: {post_url}")
            else:
                print("⚠️ Publishing failed, but content was generated")
            
            # Add delay between posts
            if i < len(trending_topics):
                print("⏱️ Waiting 30 seconds before next post...")
                time.sleep(30)
        
        print("\n🌟 Glow AI Agent workflow completed!")
    
    def generate_single_post(self, keyword: str):
        """Generate a single post for a specific keyword"""
        print(f"📝 Generating single post for: {keyword}")
        
        topic = {"keyword": keyword, "interest": 80, "competition": "medium"}
        post_data = self.content_generator.generate_blog_post(topic)
        
        print(f"✅ Generated post: '{post_data['title']}'")
        
        # Publish
        post_url = self.blogger_publisher.publish_post(post_data)
        
        if post_url:
            print(f"🎉 Successfully published: {post_url}")
        else:
            print("⚠️ Publishing failed, but content was generated")
            # Print content for manual posting
            print("\n" + "="*50)
            print("TITLE:", post_data['title'])
            print("META DESCRIPTION:", post_data['meta_description'])
            print("LABELS:", ', '.join(post_data['labels']))
            print("CONTENT:")
            print(post_data['content'])
            print("="*50)

def main():
    """Main function"""
    print("🌟 Welcome to Glow AI Agent!")
    print("Beauty & Fashion Blog Content Creator for 'Glow With Helen'")
    print("-" * 60)
    
    # Initialize the AI Agent
    agent = GlowAIAgent()
    
    # Menu system
    while True:
        print("\nChoose an option:")
        print("1. Run full workflow (scrape trends + generate posts)")
        print("2. Generate single post by keyword")
        print("3. Test trend scraping")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            agent.run_full_workflow()
        
        elif choice == '2':
            keyword = input("Enter keyword/topic: ").strip()
            if keyword:
                agent.generate_single_post(keyword)
            else:
                print("❌ Please enter a valid keyword")
        
        elif choice == '3':
            trends = agent.trend_scraper.get_trending_topics()
            print(f"\n📊 Found {len(trends)} trending topics:")
            for trend in trends:
                print(f"  • {trend['keyword']} (Interest: {trend['interest']}, Competition: {trend['competition']})")
        
        elif choice == '4':
            print("👋 Goodbye! Happy blogging!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
