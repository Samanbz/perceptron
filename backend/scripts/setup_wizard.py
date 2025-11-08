"""
Interactive setup wizard for social media data collection.

This script guides you through setting up credentials and testing
all available social media platforms.
"""

import os
import sys
from pathlib import Path

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠  {text}{Colors.END}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def check_dependencies():
    """Check if required packages are installed."""
    print_header("CHECKING DEPENDENCIES")
    
    packages = {
        "praw": "Reddit API",
        "ntscraper": "Twitter scraping",
        "googleapiclient": "YouTube Data API",
        "newsapi": "NewsAPI",
    }
    
    missing = []
    
    for package, description in packages.items():
        try:
            __import__(package)
            print_success(f"{description} ({package}) - Installed")
        except ImportError:
            print_error(f"{description} ({package}) - Not installed")
            missing.append(package)
    
    if missing:
        print_warning(f"\nMissing packages: {', '.join(missing)}")
        print_info("Install with: pip install praw ntscraper google-api-python-client newsapi-python")
        return False
    
    print_success("\nAll dependencies installed!")
    return True


def setup_reddit():
    """Interactive Reddit setup."""
    print_header("REDDIT SETUP")
    
    print("Reddit API is FREE and easy to set up!")
    print("\nFollow these steps:")
    print("1. Go to: https://www.reddit.com/prefs/apps")
    print("2. Click 'Create App' or 'Create Another App'")
    print("3. Select 'script' type")
    print("4. Fill in:")
    print("   - Name: Perceptron Intelligence")
    print("   - Redirect URI: http://localhost:8080")
    print("5. Click 'Create app'\n")
    
    input("Press Enter when you have your credentials ready...")
    
    print("\nEnter your Reddit credentials:")
    client_id = input("Client ID (under app name): ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if client_id and client_secret:
        # Set environment variables
        os.environ["REDDIT_CLIENT_ID"] = client_id
        os.environ["REDDIT_CLIENT_SECRET"] = client_secret
        
        print_success("\nReddit credentials saved for this session!")
        print_info("To make permanent, add to .env file:")
        print(f"  REDDIT_CLIENT_ID={client_id}")
        print(f"  REDDIT_CLIENT_SECRET={client_secret}")
        
        return True
    else:
        print_warning("Skipped Reddit setup")
        return False


def setup_twitter():
    """Twitter setup (no credentials needed)."""
    print_header("TWITTER SETUP")
    
    print_success("Twitter works WITHOUT credentials!")
    print_info("Uses public Nitter instances (free)")
    print("\nNo setup required - ready to use!")
    
    print("\nOptional: For production reliability, consider Twitter Official API")
    print("  Cost: $100/month for Basic tier")
    print("  Get at: https://developer.twitter.com/")
    
    return True


def setup_youtube():
    """Interactive YouTube setup."""
    print_header("YOUTUBE SETUP (OPTIONAL)")
    
    print("YouTube Data API - Free tier available!")
    print("Free tier: 10,000 units/day (~100 searches/day)")
    print("\nSteps to get API key:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable 'YouTube Data API v3'")
    print("4. Create credentials → API Key")
    print("5. Copy your API key\n")
    
    setup = input("Do you want to set up YouTube now? (y/n): ").lower()
    
    if setup == 'y':
        api_key = input("Enter your YouTube API key: ").strip()
        
        if api_key:
            os.environ["YOUTUBE_API_KEY"] = api_key
            print_success("\nYouTube API key saved for this session!")
            print_info("To make permanent, add to .env file:")
            print(f"  YOUTUBE_API_KEY={api_key}")
            return True
    
    print_warning("Skipped YouTube setup")
    return False


def setup_newsapi():
    """Interactive NewsAPI setup."""
    print_header("NEWSAPI SETUP (OPTIONAL)")
    
    print("NewsAPI - Free tier available!")
    print("Free tier: 100 requests/day")
    print("Access to 80,000+ news sources")
    print("\nSteps to get API key:")
    print("1. Go to: https://newsapi.org/register")
    print("2. Sign up for free account")
    print("3. Copy your API key\n")
    
    setup = input("Do you want to set up NewsAPI now? (y/n): ").lower()
    
    if setup == 'y':
        api_key = input("Enter your NewsAPI key: ").strip()
        
        if api_key:
            os.environ["NEWSAPI_KEY"] = api_key
            print_success("\nNewsAPI key saved for this session!")
            print_info("To make permanent, add to .env file:")
            print(f"  NEWSAPI_KEY={api_key}")
            return True
    
    print_warning("Skipped NewsAPI setup")
    return False


def create_env_file():
    """Create .env file with configured credentials."""
    print_header("CREATING .ENV FILE")
    
    env_path = Path(__file__).parent.parent / ".env"
    
    if env_path.exists():
        overwrite = input(f"\n.env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print_warning("Keeping existing .env file")
            return
    
    env_content = []
    
    # Add existing credentials
    if os.getenv("REDDIT_CLIENT_ID"):
        env_content.append(f"REDDIT_CLIENT_ID={os.getenv('REDDIT_CLIENT_ID')}")
        env_content.append(f"REDDIT_CLIENT_SECRET={os.getenv('REDDIT_CLIENT_SECRET')}")
        env_content.append("REDDIT_USER_AGENT=Perceptron Intelligence Aggregator v1.0")
        env_content.append("")
    
    if os.getenv("YOUTUBE_API_KEY"):
        env_content.append(f"YOUTUBE_API_KEY={os.getenv('YOUTUBE_API_KEY')}")
        env_content.append("")
    
    if os.getenv("NEWSAPI_KEY"):
        env_content.append(f"NEWSAPI_KEY={os.getenv('NEWSAPI_KEY')}")
        env_content.append("")
    
    # Add feature flags
    env_content.extend([
        "# Feature flags",
        "ENABLE_REDDIT=true",
        "ENABLE_TWITTER=true",
        f"ENABLE_YOUTUBE={'true' if os.getenv('YOUTUBE_API_KEY') else 'false'}",
        f"ENABLE_NEWSAPI={'true' if os.getenv('NEWSAPI_KEY') else 'false'}",
    ])
    
    if env_content:
        with open(env_path, 'w') as f:
            f.write("\n".join(env_content))
        
        print_success(f"\n.env file created: {env_path}")
    else:
        print_warning("No credentials to save")


def show_summary():
    """Show setup summary."""
    print_header("SETUP SUMMARY")
    
    platforms = {
        "Reddit": bool(os.getenv("REDDIT_CLIENT_ID")),
        "Twitter": True,  # Always available
        "YouTube": bool(os.getenv("YOUTUBE_API_KEY")),
        "NewsAPI": bool(os.getenv("NEWSAPI_KEY")),
    }
    
    print("Platform Status:")
    for platform, enabled in platforms.items():
        if enabled:
            print_success(f"{platform:15} - Ready")
        else:
            print_warning(f"{platform:15} - Not configured")
    
    enabled_count = sum(platforms.values())
    print(f"\n{Colors.BOLD}Total platforms ready: {enabled_count}/4{Colors.END}")
    
    print("\n" + "="*70)
    print(f"{Colors.BOLD}NEXT STEPS:{Colors.END}")
    print("="*70)
    
    print("\n1. Test your setup:")
    print(f"   {Colors.CYAN}python scripts/test_social_media.py{Colors.END}")
    
    print("\n2. Start collecting data:")
    print(f"   {Colors.CYAN}python scripts/fetch_social_media.py{Colors.END}")
    
    print("\n3. View documentation:")
    print(f"   {Colors.CYAN}docs/SOCIAL_MEDIA_GUIDE.md{Colors.END}")
    print(f"   {Colors.CYAN}docs/SOCIAL_MEDIA_SUMMARY.md{Colors.END}")
    
    print("\n4. Configure sources:")
    print(f"   Edit {Colors.CYAN}config.json{Colors.END} to customize subreddits, keywords, etc.")
    
    print("\n5. Automate collection:")
    print(f"   Add to {Colors.CYAN}scheduler.py{Colors.END} for periodic fetching")
    
    print(f"\n{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}Setup complete! You're ready to collect social media data.{Colors.END}")
    print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")


def main():
    """Run the setup wizard."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║     PERCEPTRON SOCIAL MEDIA SETUP WIZARD                         ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    print("This wizard will help you set up data collection from:")
    print("  • Reddit (recommended - free & easy)")
    print("  • Twitter/X (free - no credentials needed)")
    print("  • YouTube (optional - free tier available)")
    print("  • NewsAPI (optional - free tier available)")
    
    input("\nPress Enter to continue...")
    
    # Check dependencies
    if not check_dependencies():
        print_error("\nPlease install missing dependencies first!")
        return 1
    
    # Setup each platform
    reddit_ready = setup_reddit()
    twitter_ready = setup_twitter()
    youtube_ready = setup_youtube()
    newsapi_ready = setup_newsapi()
    
    # Create .env file
    if reddit_ready or youtube_ready or newsapi_ready:
        create_env_file()
    
    # Show summary
    show_summary()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
