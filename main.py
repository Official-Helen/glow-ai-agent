# ================================
# Glow AI – Blogger Auto Publisher
# ================================
# Features:
# - Google Trends (beauty/skincare/fashion-filtered) + Pinterest-like trends (robust fallback)
# - Groq-written, human & SEO-optimized HTML (starts at <h2>, no <meta> in body)
# - Section-matched Pexels images with photographer credit
# - Amazon affiliate links inserted with your tag
# - Auto labels: SEO keyword + trends
# - Title <= 60 chars, searchDescription 150–160 chars
# - Auto-publish to Blogger via OAuth (refresh token)
# - Chat-style history (load/delete)

import re
import json
import time
import html
import random
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import streamlit as st

# ---------- Config ----------
st.set_page_config(page_title="Glow AI – Blogger Auto Publisher", layout="wide")

# ---------- Secrets / Keys ----------
REQ_KEYS = [
    "BLOGGER_BLOG_ID", "BLOGGER_CLIENT_ID", "BLOGGER_CLIENT_SECRET", "BLOGGER_REFRESH_TOKEN",
    "GROQ_API_KEY", "PEXELS_API_KEY", "AMAZON_TAG"
]
missing = [k for k in REQ_KEYS if k not in st.secrets]
if missing:
    st.error(f"Missing required secrets: {', '.join(missing)}")
    st.stop()

BLOGGER_BLOG_ID = st.secrets["BLOGGER_BLOG_ID"]
GOOGLE_CLIENT_ID = st.secrets["BLOGGER_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["BLOGGER_CLIENT_SECRET"]
GOOGLE_REFRESH_TOKEN = st.secrets["BLOGGER_REFRESH_TOKEN"]

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
PEXELS_API_KEY = st.secrets["PEXELS_API_KEY"]
AMAZON_TAG = st.secrets["AMAZON_TAG"]

# ---------- Libs that may be optional ----------
# pytrends is optional; app will gracefully fallback if not installed
try:
    from pytrends.request import TrendReq
    _pytrends_available = True
except Exception:
    _pytrends_available = False

# ---------- Session State ----------
if "history" not in st.session_state:
    st.session_state.history: List[Dict] = []  # [{id, title, topic, html, labels, search_desc, created_at}]
if "current_id" not in st.session_state:
    st.session_state.current_id: Optional[str] = None

# ---------- Utilities ----------
def trim_title(s: str, max_len: int = 60) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= max_len else s[:max_len-1].rstrip() + "…"

def clamp_description(s: str, lo: int = 150, hi: int = 160) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > hi:
        return s[:hi-1].rstrip() + "…"
    if len(s) < lo:
        # pad gently (rare)
        return s + " " + ("." * max(0, lo - len(s)))
    return s

def append_amazon_tag(url: str, tag: str) -> str:
    if "amazon." not in url and "amzn.to" not in url:
        return url
    if "tag=" in url:
        return url
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={tag}"

# Map common beauty keywords to real Amazon products (fill with your *real* links).
# You can add/modify anytime—no code changes needed.
AMAZON_PRODUCTS: Dict[str, List[str]] = {
    # cleansers
    "cleanser": [
        f"https://www.amazon.com/dp/B07Z5BZCHB?tag={AMAZON_TAG}",  # CeraVe Hydrating Facial Cleanser
        f"https://www.amazon.com/dp/B01N6E66RN?tag={AMAZON_TAG}",  # Cetaphil Gentle Skin Cleanser
    ],
    # exfoliant / bha / aha
    "bha": [
        f"https://www.amazon.com/dp/B00949CTQQ?tag={AMAZON_TAG}",  # Paula’s Choice 2% BHA
    ],
    "exfoliant": [
        f"https://www.amazon.com/dp/B00949CTQQ?tag={AMAZON_TAG}",
    ],
    # niacinamide
    "niacinamide": [
        f"https://www.amazon.com/dp/B09NQ5L9V5?tag={AMAZON_TAG}",  # The Ordinary Niacinamide
    ],#
