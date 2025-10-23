import requests
import os
from pathlib import Path
from urllib.parse import urlparse
import re
from PIL import Image
import hashlib

class RedditImageDownloader:
    def __init__(self, output_dir="./poc_output/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

    def is_image_url(self, url):
        """Check if URL points to an image file"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            return any(path.endswith(ext) for ext in self.supported_extensions)
        except:
            return False

    def extract_image_urls(self, post):
        """Extract image URLs from a Reddit post"""
        image_urls = []

        # Check if post URL is a direct image
        if hasattr(post, 'url') and self.is_image_url(post.url):
            image_urls.append(post.url)
            return image_urls

        # Handle Reddit galleries
        if hasattr(post, 'is_gallery') and post.is_gallery:
            if hasattr(post, 'media_metadata'):
                for item_id in post.gallery_data['items']:
                    media_id = item_id['media_id']
                    if media_id in post.media_metadata:
                        media_item = post.media_metadata[media_id]
                        if 's' in media_item and 'u' in media_item['s']:
                            # Convert Reddit preview URL to full image URL
                            image_url = media_item['s']['u'].replace('preview.redd.it', 'i.redd.it')
                            image_url = image_url.split('?')[0]  # Remove query parameters
                            image_urls.append(image_url)

        # Handle i.redd.it direct links
        if hasattr(post, 'url') and 'i.redd.it' in post.url:
            image_urls.append(post.url)

        # Handle imgur links (convert to direct image URLs)
        if hasattr(post, 'url') and 'imgur.com' in post.url:
            imgur_url = self.convert_imgur_url(post.url)
            if imgur_url:
                image_urls.append(imgur_url)

        return image_urls

    def convert_imgur_url(self, url):
        """Convert imgur page URL to direct image URL"""
        # Handle various imgur URL formats
        if 'i.imgur.com' in url:
            return url  # Already direct image URL

        # Extract image ID from imgur URLs
        imgur_id_match = re.search(r'imgur\.com/(?:gallery/|a/)?([a-zA-Z0-9]+)', url)
        if imgur_id_match:
            imgur_id = imgur_id_match.group(1)
            # Try common image extensions
            for ext in ['.jpg', '.png', '.gif']:
                direct_url = f"https://i.imgur.com/{imgur_id}{ext}"
                try:
                    response = requests.head(direct_url, timeout=5)
                    if response.status_code == 200:
                        return direct_url
                except:
                    continue
        return None

    def download_image(self, url, post_id):
        """Download single image from URL"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'TShirtPOC/1.0'
            })
            response.raise_for_status()

            # Verify it's actually an image
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                print(f"⚠️  URL {url} is not an image (content-type: {content_type})")
                return None

            # Generate filename with hash to avoid duplicates
            content_hash = hashlib.md5(response.content).hexdigest()[:8]
            extension = self.get_extension_from_url(url) or '.jpg'
            filename = f"{post_id}_{content_hash}{extension}"
            filepath = self.output_dir / filename

            # Check if file already exists
            if filepath.exists():
                print(f"📸 Image already exists: {filename}")
                return str(filepath)

            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)

            # Verify it's a valid image by opening with PIL
            try:
                with Image.open(filepath) as img:
                    # Resize if too large (for LLM processing efficiency)
                    if img.width > 1024 or img.height > 1024:
                        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                        img.save(filepath, optimize=True)

                    print(f"✅ Downloaded image: {filename} ({img.width}x{img.height})")
                    return str(filepath)
            except Exception as e:
                print(f"❌ Invalid image file, removing: {e}")
                filepath.unlink()
                return None

        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            return None

    def get_extension_from_url(self, url):
        """Extract file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in self.supported_extensions:
            if path.endswith(ext):
                return ext
        return None

    def download_post_images(self, post, max_images=1):
        """Download images from a Reddit post (up to max_images)"""
        image_urls = self.extract_image_urls(post)
        downloaded_paths = []

        print(f"🔍 Found {len(image_urls)} image URLs for post {post.id}")

        for i, url in enumerate(image_urls[:max_images]):
            print(f"📥 Downloading image {i+1}/{min(len(image_urls), max_images)}: {url}")
            filepath = self.download_image(url, post.id)
            if filepath:
                downloaded_paths.append(filepath)

        return downloaded_paths

    def cleanup_old_images(self, keep_recent=50):
        """Clean up old downloaded images to save space"""
        try:
            image_files = list(self.output_dir.glob("*"))
            if len(image_files) > keep_recent:
                # Sort by modification time, keep most recent
                image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for old_file in image_files[keep_recent:]:
                    old_file.unlink()
                    print(f"🗑️  Cleaned up old image: {old_file.name}")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")

if __name__ == "__main__":
    # Test the image downloader
    print("🧪 Testing Reddit image downloader...")

    downloader = RedditImageDownloader()

    # Test URLs
    test_urls = [
        "https://i.redd.it/example.jpg",
        "https://i.imgur.com/example.png"
    ]

    print(f"Created image output directory: {downloader.output_dir}")
    print("✅ Image downloader ready for use")