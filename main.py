import requests
import json
import re
from typing import Dict, List
from datetime import datetime

# -------------------------------
# CONFIGURATION
# -------------------------------
AMAZON_TAG = "helenbeautysh-20"

# ✅ Affiliate Product Mapping (Fixed dictionary)
AMAZON_PRODUCTS: Dict[str, List[str]] = {
    "skincare": [
        f"https://www.amazon.com/dp/B00949CTQQ/?tag={AMAZON_TAG}",  # Paula’s Choice 2% BHA Exfoliant
        f"https://amzn.to/4eXaTxE",  # The Ordinary Niacinamide
        f"https://www.amazon.com/dp/B0D663VWFC/?tag={AMAZON_TAG}",  # COSRX Snail Mucin Essence
        f"https://www.amazon.com/dp/B0F6D35G3G/?tag={AMAZON_TAG}",  # La Roche-Posay Moisturizer
    ],
    "sunscreen": [
        f"https://amzn.to/4kQjLqe",  # EltaMD UV Clear
        f"https://amzn.to/4flUkvp",  # La Roche-Posay Anthelios
        f"https://amzn.to/40RfWtM",  # Black Girl Sunscreen
    ],
    "makeup": [
        f"https://www.amazon.com/dp/B07HR8JS2Q/?tag={AMAZON_TAG}",  # Maybelline Foundation
        f"https://www.amazon.com/dp/B01J24K8MK/?tag={AMAZON_TAG}",  # L’Oreal Mascara
    ],
}  # ✅ Now properly closed

BLOG_ID = "YOUR_BLOGGER_BLOG_ID"
ACCESS_TOKEN = "YOUR_GOOGLE_OAUTH_ACCESS_TOKEN"

# -------------------------------
# TREND SCRAPER PLACEHOLDERS
# -------------------------------
def fetch_google_trends(keyword: str) -> List[str]:
    # Placeholder: Replace with pytrends or API
    return [f"{keyword} skincare", f"best {keyword} routine", f"{keyword} tips"]

def fetch_pinterest_trends(keyword: str) -> List[str]:
    # Placeholder: Replace with Pinterest API or scraping
    return [f"{keyword} ideas", f"{keyword} hacks", f"{keyword} products"]

# -------------------------------
# BLOG POST GENERATOR
# -------------------------------
def generate_blog_post(keyword: str, category: str) -> Dict[str, str]:
    # Fetch trends
    google_trends = fetch_google_trends(keyword)
    pinterest_trends = fetch_pinterest_trends(keyword)
    combined_keywords = google_trends + pinterest_trends

    # Pick some labels
    labels = list(set([kw.split()[0].capitalize() for kw in combined_keywords[:5]]))

    # Title (SEO short and clear)
    title = f"{keyword.capitalize()} Skincare Tips in 2025"

    # Meta description (not stuffed, natural)
    meta_description = (
        f"Discover {keyword} skincare trends for 2025. "
        "Learn easy routines, dermatologist-approved tips, and products people love."
    )

    # Body (humanized, not just sales)
    body = f"""
<p><strong>{keyword.capitalize()} skincare</strong> has become one of the most searched beauty topics in 2025. 
People are not just looking for products—they want routines that feel natural, safe, and effective.</p>

<p>Based on <em>Google Trends</em> and <em>Pinterest insights</em>, here are some things people are searching for:</p>
<ul>
    {''.join([f"<li>{kw}</li>" for kw in combined_keywords[:6]])}
</ul>

<p>Here are some trusted products that can help improve your {keyword} routine:</p>
<ul>
    {''.join([f'<li><a href="{link}" target="_blank" rel="nofollow">Check on Amazon</a></li>' for link in AMAZON_PRODUCTS.get(category, [])])}
</ul>

<p>Remember, skincare is not about buying everything—it’s about finding what works for your skin and sticking to a consistent routine.</p>
    """

    return {
        "title": title,
        "body": body,
        "meta_description": meta_description,
        "labels": labels,
    }

# -------------------------------
# BLOGGER PUBLISHER
# -------------------------------
def publish_to_blogger(post: Dict[str, str]):
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

    data = {
        "kind": "blogger#post",
        "blog": {"id": BLOG_ID},
        "title": post["title"],
        "content": f"""
<!-- Meta Description -->
<meta name="description" content="{post['meta_description']}">

{post['body']}
        """,
        "labels": post["labels"],
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("✅ Blog post published successfully!")
        return response.json()
    else:
        print("❌ Failed to publish:", response.text)
        return None

# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    keyword = "hydration"
    category = "skincare"

    post = generate_blog_post(keyword, category)
    publish_to_blogger(post)
