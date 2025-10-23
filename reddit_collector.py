import praw
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from image_handler import RedditImageDownloader

# Load environment variables from parent directory
load_dotenv('../.env')

def get_trending_memes(limit=10, subreddit_name="memes", download_images=True):
    """Get top posts from specified subreddit with basic filtering and optional image download"""

    # Check if credentials are available
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'poc_trend_collector')

    if not client_id or not client_secret:
        print("❌ Reddit API credentials not found in .env file")
        print("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in the .env file")
        return []

    # Initialize image downloader if requested
    image_downloader = RedditImageDownloader() if download_images else None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        subreddit = reddit.subreddit(subreddit_name)
        hot_posts = subreddit.hot(limit=limit)

        viable_trends = []
        for post in hot_posts:
            if post.score > 1000:  # Basic popularity filter
                trend = {
                    "id": post.id,
                    "title": post.title,
                    "score": post.score,
                    "url": post.url,
                    "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                    "text_content": extract_text_from_title(post.title),
                    "images": []
                }

                # Download images if requested
                if download_images and image_downloader:
                    print(f"🖼️  Checking for images in post: {post.title[:50]}...")
                    downloaded_images = image_downloader.download_post_images(post, max_images=1)
                    trend["images"] = downloaded_images
                    if downloaded_images:
                        print(f"✅ Downloaded {len(downloaded_images)} images")
                    else:
                        print("📷 No images found/downloaded")

                viable_trends.append(trend)

        return viable_trends

    except Exception as e:
        print(f"❌ Error fetching Reddit data: {str(e)}")
        return []

def get_user_subreddit_choice():
    """Get subreddit choice from user input"""
    print("\n📋 Subreddit Selection")
    print("Choose a subreddit to collect trending content from:")
    print("1. memes - General memes (default)")
    print("2. dankmemes - Dank memes")
    print("3. wholesomememes - Wholesome memes")
    print("4. ProgrammerHumor - Programming memes")
    print("5. gaming - Gaming content")
    print("6. funny - General funny content")
    print("7. showerthoughts - Shower thoughts")
    print("8. custom - Enter custom subreddit name")

    while True:
        choice = input("\nEnter your choice (1-8) or press Enter for default: ").strip()

        if choice == "" or choice == "1":
            return "memes"
        elif choice == "2":
            return "dankmemes"
        elif choice == "3":
            return "wholesomememes"
        elif choice == "4":
            return "ProgrammerHumor"
        elif choice == "5":
            return "gaming"
        elif choice == "6":
            return "funny"
        elif choice == "7":
            return "showerthoughts"
        elif choice == "8":
            custom = input("Enter custom subreddit name (without r/): ").strip()
            if custom:
                return custom
            else:
                print("❌ Please enter a valid subreddit name")
        else:
            print("❌ Invalid choice. Please enter 1-8 or press Enter for default")

def extract_text_from_title(title):
    """Extract quotable text or concepts for t-shirt design"""
    # Simple keyword extraction - look for quoted text or simple phrases
    if '"' in title:
        return title.split('"')[1]
    elif len(title.split()) <= 4:
        return title
    else:
        return None

if __name__ == "__main__":
    # Test the collector
    print("🧪 Testing Reddit collector...")
    trends = get_trending_memes(limit=5)
    print(f"Found {len(trends)} trends:")
    for trend in trends:
        print(f"  - {trend['title'][:50]}... (Score: {trend['score']})")
        if trend['text_content']:
            print(f"    Text: {trend['text_content']}")