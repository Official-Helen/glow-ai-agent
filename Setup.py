#!/usr/bin/env python3
"""
Setup script for Glow AI Agent
Handles dependency installation and initial configuration
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("🔧 Installing required packages...")
    
    try:
        # Install basic requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ Basic dependencies installed")
        
        # Try to install Google API packages
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "google-api-python-client", 
                "google-auth-oauthlib",
                "google-auth"
            ])
            print("✅ Google API packages installed")
        except subprocess.CalledProcessError:
            print("⚠️  Google API packages failed to install. Blogger publishing will be limited.")
        
        print("🎉 Setup completed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print("Try installing manually with: pip install -r requirements.txt")

def create_env_template():
    """Create environment variables template"""
    env_template = """# Glow AI Agent Environment Variables
# Copy this to .env and fill in your actual values

# Pexels API (for images)
PEXELS_API_KEY=your_pexels_api_key_here

# Google/Blogger API (for publishing)
BLOGGER_CLIENT_ID=your_google_client_id_here
BLOGGER_CLIENT_SECRET=your_google_client_secret_here
BLOGGER_BLOG_ID=your_blog_id_here

# Optional: Google Trends API
GOOGLE_TRENDS_API_KEY=your_trends_api_key_here
"""
    
    if not os.path.exists('.env.template'):
        with open('.env.template', 'w') as f:
            f.write(env_template)
        print("✅ Created .env.template file")
        print("📝 Please copy .env.template to .env and add your API keys")

def main():
    print("🌟 Glow AI Agent Setup")
    print("=" * 40)
    
    install_requirements()
    create_env_template()
    
    print("\n📋 Next steps:")
    print("1. Get your Pexels API key from: https://www.pexels.com/api/")
    print("2. Set up Google API credentials for Blogger")
    print("3. Copy .env.template to .env and add your keys")
    print("4. Run: python main.py")

if __name__ == "__main__":
    main()
