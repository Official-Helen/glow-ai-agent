#!/usr/bin/env python3 """ Glow AI Agent - Complete Beauty & Fashion Blog Content Creator Automatically generates SEO-optimized blog posts for "Glow With Helen" """

import os import sys import requests import json import random import time import webbrowser from datetime import datetime, timedelta from typing import List, Dict, Tuple, Optional, Union import re from dataclasses import dataclass import pickle import logging from urllib.parse import urlparse, parse_qs

Import validation and graceful degradation for optional dependencies

OPTIONAL_IMPORTS = {}

try: from googleapiclient.discovery import build from google.oauth2.credentials import Credentials from google_auth_oauthlib.flow import Flow from google.auth.transport.requests import Request from google.oauth2 import service_account OPTIONAL_IMPORTS['google_apis'] = True except ImportError as e: print(f"⚠️  Google API libraries not installed: {e}") print("Install with: pip install google-api-python-client google-auth-oauthlib") OPTIONAL_IMPORTS['google_apis'] = False

try: import pytrends from pytrends.request import TrendReq OPTIONAL_IMPORTS['pytrends'] = True except ImportError: print("⚠️  PyTrends not installed. Using fallback trend data.") print("Install with: pip install pytrends") OPTIONAL_IMPORTS['pytrends'] = False

try: from bs4 import BeautifulSoup OPTIONAL_IMPORTS['beautifulsoup'] = True except ImportError: print("⚠️  BeautifulSoup not installed. Web scraping limited.") print("Install with: pip install beautifulsoup4") OPTIONAL_IMPORTS['beautifulsoup'] = False

try: import schedule OPTIONAL_IMPORTS['schedule'] = True except ImportError: print("⚠️  Schedule library not installed. No automated scheduling.") print("Install with: pip install schedule") OPTIONAL_IMPORTS['schedule'] = False

Set up logging

logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[ logging.FileHandler('glow_ai.log'), logging.StreamHandler(sys.stdout) ] ) logger = logging.getLogger(name)

Configuration

@dataclass class Config: PEXELS_API_KEY: str = os.getenv('PEXELS_API_KEY', '') GOOGLE_TRENDS_API_KEY: str = os.getenv('GOOGLE_TRENDS_API_KEY', '') BLOGGER_CLIENT_ID: str = os.getenv('BLOGGER_CLIENT_ID', '') BLOGGER_CLIENT_SECRET: str = os.getenv('BLOGGER_CLIENT_SECRET', '') BLOGGER_BLOG_ID: str = os.getenv('BLOGGER_BLOG_ID', '') AMAZON_AFFILIATE_TAG: str = "helenbeautysh-20" BLOG_NAME: str = "Glow With Helen" AUTHOR_NAME: str = "Helen" MAX_POSTS_PER_DAY: int = 3 MIN_KEYWORD_INTEREST: int = 70 MAX_RETRIES: int = 3 REQUEST_TIMEOUT: int = 30 MIN_CONTENT_LENGTH: int = 1500 MAX_TITLE_LENGTH: int = 60 META_DESC_LENGTH: int = 155

def validate(self) -> List[str]:
    issues = []
    if not self.PEXELS_API_KEY:
        issues.append("PEXELS_API_KEY not set - images will use placeholders")
    if not self.BLOGGER_CLIENT_ID or not self.BLOGGER_CLIENT_SECRET:
        issues.append("Blogger credentials not set - publishing disabled")
    if not self.BLOGGER_BLOG_ID:
        issues.append("BLOGGER_BLOG_ID not set - publishing disabled")
    return issues

(All classes: TrendAnalyzer, ProductDatabase, ImageManager, ContentGenerator etc. remain here exactly as before)

The only fix applied is to the dangling f-string error.

<h3>❌ Mistake #3: Wrong Product Selection</h3>
    <p>Not all products are created equal, and what works for your favorite influencer might not work for your skin. That's why I'm so careful about my recommendations. {self.product_db.create_affiliate_link(products[2])} is one of my top picks because it's gentle, effective, and actually delivers results without overwhelming your skin.</p>

(Rest of script continues unchanged — including publishing, scheduling, and main execution logic)

