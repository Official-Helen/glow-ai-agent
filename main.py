#!/usr/bin/env python3
"""
Simplified Glow AI Agent - Content Generation Only
Skips Blogger API authentication, generates HTML for manual posting
"""

import os
import requests
import json
import random
import time
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class SimpleConfig:
    PEXELS_API_KEY: str = os.getenv('PEXELS_API_KEY', '')
    AMAZON_AFFILIATE_TAG: str = "helenbeautysh-20"
    BLOG_NAME: str = "Glow With Helen"
    AUTHOR_NAME: str = "Helen"

class SimpleGlowAI:
    """Simplified version that generates content without Blogger API"""
    
    def __init__(self):
        self.config = SimpleConfig()
        
        # Sample trending topics (you can modify these)
        self.trending_topics = [
            {"keyword": "glass skin routine", "interest": 85},
            {"keyword": "retinol for beginners", "interest": 78},
            {"keyword": "winter skincare tips", "interest": 92},
            {"keyword": "affordable makeup dupes", "interest": 88},
            {"keyword": "niacinamide benefits", "interest": 76},
        ]
        
        # Beauty products database
        self.products = [
            {"name": "CeraVe Foaming Facial Cleanser", "id": "B077TGQZPX", "price": "$12.99"},
            {"name": "The Ordinary Niacinamide 10%", "id": "B06XHW8TQL", "price": "$7.20"},
            {"name": "Neutrogena Ultra Sheer Sunscreen", "id": "B002JAYMEE", "price": "$8.47"},
            {"name": "Olay Regenerist Retinol 24", "id": "B07MVJC3J8", "price": "$18.99"},
            {"name": "Maybelline Fit Me Foundation", "id": "B07C2ZS7B8", "price": "$7.99"},
        ]
    
    def generate_content(self, keyword: str) -> Dict:
        """Generate complete blog post content"""
        
        # Generate SEO elements
        title = self.create_seo_title(keyword)
        meta_desc = self.create_meta_description(keyword)
        labels = self.create_labels(keyword)
        
        # Get random products
        selected_products = random.sample(self.products, 3)
        
        # Generate HTML content
        html_content = self.create_html_content(keyword, selected_products)
        
        return {
            "title": title,
            "meta_description": meta_desc,
            "labels": labels,
            "html_content": html_content,
            "keyword": keyword
        }
    
    def create_seo_title(self, keyword: str) -> str:
        """Create SEO-friendly title"""
        templates = [
            f"{keyword.title()}: Complete Guide for 2024",
            f"The Ultimate {keyword.title()} Guide",
            f"{keyword.title()}: Tips That Actually Work",
            f"How to Master {keyword.title()}",
        ]
        title = random.choice(templates)
        return title[:60] if len(title) > 60 else title
    
    def create_meta_description(self, keyword: str) -> str:
        """Create meta description"""
        desc = f"Discover the best {keyword} tips and products. Complete guide with expert advice for glowing, healthy skin."
        return desc[:160]
    
    def create_labels(self, keyword: str) -> List[str]:
        """Create blog labels"""
        base_labels = ["beauty", "skincare", "beauty tips"]
        keyword_parts = keyword.lower().split()
        return list(set(base_labels + keyword_parts))[:6]
    
    def create_affiliate_link(self, product: Dict) -> str:
        """Create Amazon affiliate link"""
        return f'<a href="https://www.amazon.com/dp/{product["id"]}/?tag={self.config.AMAZON_AFFILIATE_TAG}" target="_blank" rel="nofollow">{product["name"]}</a>'
    
    def create_html_content(self, keyword: str, products: List[Dict]) -> str:
        """Generate the full HTML blog post"""
        
        # Sample images (you can replace with actual Pexels URLs)
        sample_images = [
            "https://images.pexels.com/photos/3762879/pexels-photo-3762879.jpeg?auto=compress&cs=tinysrgb&w=800",
            "https://images.pexels.com/photos/3993212/pexels-photo-3993212.jpeg?auto=compress&cs=tinysrgb&w=800",
            "https://images.pexels.com/photos/4041392/pexels-photo-4041392.jpeg?auto=compress&cs=tinysrgb&w=800",
        ]
        
        html = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px;">

<p>Hey gorgeous! ✨ If you've been searching for the ultimate guide to <strong>{keyword}</strong>, you've landed in exactly the right place. I'm Helen, and today we're diving deep into everything you need to know about {keyword}.</p>

<p>Whether you're a complete beginner or looking to level up your current routine, this comprehensive guide will walk you through step-by-step techniques, product recommendations, and insider tips that actually work.</p>

<img src="{sample_images[0]}" alt="{keyword} skincare routine" style="width:100%;height:auto;margin:20px 0;border-radius:8px;">
<p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>

<h2>What is {keyword.title()}?</h2>

<p>Let's start with the basics. {keyword.title()} is more than just a beauty trend – it's an approach that focuses on enhancing your natural beauty while maintaining healthy, glowing skin.</p>

<p>Here's what makes {keyword} so special:</p>
<ul>
<li><strong>Promotes healthy, radiant skin:</strong> Works with your skin's natural processes</li>
<li><strong>Uses gentle, effective ingredients:</strong> No harsh chemicals that damage your skin barrier</li>
<li><strong>Suitable for most skin types:</strong> Adaptable to your unique skin needs</li>
<li><strong>Focuses on long-term results:</strong> Sustainable beauty that lasts</li>
</ul>

<p>One product I absolutely recommend for this is {self.create_affiliate_link(products[0])}. It's been a complete game-changer in my routine and so many of my readers have seen amazing results!</p>

<h2>Step-by-Step {keyword.title()} Guide</h2>

<img src="{sample_images[1]}" alt="{keyword} application steps" style="width:100%;height:auto;margin:20px 0;border-radius:8px;">
<p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>

<h3>Step 1: Preparation is Everything</h3>
<p>Always start with clean hands and a fresh, cleansed face. This ensures maximum product absorption and prevents bacteria from interfering with your routine. Remove any makeup thoroughly with a gentle cleanser.</p>

<h3>Step 2: Apply Your Key Products</h3>
<p>This is where {self.create_affiliate_link(products[1])} really shines. Apply it evenly using gentle patting motions, allowing each layer to absorb completely before adding the next product. Patience is key here!</p>

<h3>Step 3: Lock It All In</h3>
<p>Don't forget to seal everything with a good moisturizer and <em>always</em> apply sunscreen during the day. Sun protection is non-negotiable for healthy skin!</p>

<h2>Common {keyword.title()} Mistakes to Avoid</h2>

<p>Even with the best intentions, it's easy to make mistakes that can sabotage your results. Here are the top ones I see (and have made myself!):</p>

<h3>❌ Using Too Much Product</h3>
<p>Less is definitely more when it comes to {keyword}. Start with small amounts and build up gradually. Your skin needs time to adjust, and overdoing it can cause irritation.</p>

<h3>❌ Inconsistent Application</h3>
<p>Results come from consistency, not perfection. It's better to do a simple routine daily than an elaborate one occasionally. Set reminders if you need to!</p>

<h3>❌ Wrong Product Selection</h3>
<p>Not all products are created equal, and what works for your friend might not work for you. That's why I love {self.create_affiliate_link(products[2])} – it's reliable, gentle, and works for most skin types.</p>

<h2>My Personal Experience with {keyword.title()}</h2>

<p>I'll be honest – when I first started with {keyword}, I was skeptical. I'd tried so many things that promised amazing results but never delivered. But after just two weeks of consistent use, I started noticing real changes.</p>

<p>My skin looked brighter, felt smoother, and that stubborn dullness I'd been battling for years finally started to fade. The key was finding the right combination of products and sticking with it.</p>

<img src="{sample_images[2]}" alt="Glowing skin results from {keyword}" style="width:100%;height:auto;margin:20px 0;border-radius:8px;">
<p style="font-style:italic;font-size:12px;color:#666;">Image Source: Pexels</p>

<h2>Product Recommendations That Actually Work</h2>

<p>Based on my experience and countless hours of research, here are my top product picks for {keyword}:</p>

<h3>🌟 Best Overall Product</h3>
<p><strong>{products[0]["name"]} ({products[0]["price"]})</strong> - This has been my holy grail product. {self.create_affiliate_link(products[0])} delivers consistent results without breaking the bank.</p>

<h3>💰 Best Budget Option</h3>
<p><strong>{products[1]["name"]} ({products[1]["price"]})</strong> - Proof that great skincare doesn't have to be expensive. {self.create_affiliate_link(products[1])} punches way above its price point.</p>

<h3>✨ Best for Sensitive Skin</h3>
<p><strong>{products[2]["name"]} ({products[2]["price"]})</strong> - If you have reactive skin like I do, {self.create_affiliate_link(products[2])} is incredibly gentle yet effective.</p>

<h2>Frequently Asked Questions</h2>

<h3>How long before I see results?</h3>
<p>Most people start noticing improvements within 2-4 weeks of consistent use. However, significant changes typically take 6-8 weeks as your skin completes its natural renewal cycle.</p>

<h3>Can I use this with other skincare products?</h3>
<p>Absolutely! {keyword.title()} plays well with most other skincare ingredients. Just introduce new products gradually to avoid overwhelming your skin.</p>

<h3>Is this suitable for all skin types?</h3>
<p>Yes, but start slowly if you have sensitive skin. Everyone's skin is different, so pay attention to how yours responds and adjust accordingly.</p>

<h2>Final Thoughts</h2>

<p>There you have it, beauties! Your complete guide to {keyword}. Remember, skincare is a journey, not a destination. Be patient with yourself, stay consistent, and don't be afraid to adjust your routine as your skin's needs change.</p>

<p>The most important thing is to listen to your skin and give it what it needs. Some days that might be extra hydration, other days it might need gentle exfoliation. Trust the process and trust yourself.</p>

<p>What's your experience with {keyword}? I'd love to hear about your journey in the comments below! And if you try any of these tips or products, tag me on social media – I love seeing your glowing results! 💕</p>

<div style="margin-top:40px;padding-top:20px;border-top:2px solid #f0f0f0;">
<p style="font-style:italic;color:#666;font-size:14px;">
<em>This article may contain affiliate links. If you purchase through these links, I may earn a small commission at no extra cost to you. This helps support the blog and allows me to continue creating helpful content for you!</em>
</p>
</div>

</div>
"""
        return html
    
    def run_content_generator(self):
        """Main function to generate content"""
        print("🌟 Welcome to Glow AI Content Generator!")
        print("💡 This version generates blog content without Blogger API")
        print("-" * 60)
        
        while True:
            print("\nOptions:")
            print("1. Generate from trending topics")
            print("2. Generate from custom keyword")
            print("3. View trending topics")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                topic = random.choice(self.trending_topics)
                self.generate_and_display(topic['keyword'])
                
            elif choice == '2':
                keyword = input("Enter your keyword: ").strip()
                if keyword:
                    self.generate_and_display(keyword)
                else:
                    print("❌ Please enter a keyword")
                    
            elif choice == '3':
                print("\n📊 Trending Topics:")
                for i, topic in enumerate(self.trending_topics, 1):
                    print(f"{i}. {topic['keyword']} (Interest: {topic['interest']})")
                    
            elif choice == '4':
                print("👋 Happy blogging!")
                break
                
            else:
                print("❌ Invalid choice")
    
    def generate_and_display(self, keyword: str):
        """Generate content and display results"""
        print(f"\n📝 Generating content for: {keyword}")
        print("⏳ This may take a few seconds...")
        
        content = self.generate_content(keyword)
        
        print(f"\n✅ Content generated successfully!")
        print(f"📊 Title: {content['title']}")
        print(f"📝 Meta Description: {content['meta_description']}")
        print(f"🏷️  Labels: {', '.join(content['labels'])}")
        
        # Save to file
        filename = f"blog_post_{keyword.replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"<!-- TITLE: {content['title']} -->\n")
            f.write(f"<!-- META DESCRIPTION: {content['meta_description']} -->\n")
            f.write(f"<!-- LABELS: {', '.join(content['labels'])} -->\n\n")
            f.write(content['html_content'])
        
        print(f"💾 Content saved to: {filename}")
        print("\n📋 You can now:")
        print("1. Copy the HTML content to Blogger")
        print("2. Edit the file if needed")
        print("3. Use the title and meta description for SEO")

if __name__ == "__main__":
    app = SimpleGlowAI()
    app.run_content_generator()
