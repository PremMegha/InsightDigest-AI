import feedparser
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser 
from sqlalchemy.orm import Session
from app.scrapers.utils import get_or_create_source, save_article

try:
    from app.config.youtube_channels import YOUTUBE_CHANNELS
except ImportError:
    YOUTUBE_CHANNELS = []

class YoutubeScraper:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        print(f"      ▶ Scraping {len(YOUTUBE_CHANNELS)} YouTube Channels (Filter: <30 days, No Shorts)...")
        count = 0
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        for url in YOUTUBE_CHANNELS:
            try:
                # 1. Setup Source
                source = get_or_create_source(self.db, "YouTube Channel", url, "rss")
                
                # 2. Get Feed URL
                if "channel/" in url:
                    channel_id = url.split("channel/")[-1]
                    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                else:
                    feed_url = url 

                feed = feedparser.parse(feed_url)
                if hasattr(feed, 'feed') and hasattr(feed.feed, 'title'):
                    source.name = feed.feed.title

                # 3. Process Videos
                for entry in feed.entries:
                    if "#shorts" in entry.title.lower() or "shorts" in entry.link:
                        continue

                    
                    try:
                        if hasattr(entry, 'published_parsed'):
                            published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        else:
                            published_at = datetime.now(timezone.utc)

                        if published_at < cutoff_date:
                            continue
                    except Exception:
                        published_at = datetime.now(timezone.utc)

                
                    saved = save_article(
                        self.db,
                        source_id=source.id,
                        title=entry.title,
                        url=entry.link,
                        published_at=published_at,
                        content=f"Video Summary: {entry.summary if 'summary' in entry else entry.title}"
                    )
                    if saved:
                        count += 1
                        
            except Exception as e:
                print(f"      ❌ Error scraping {url}: {e}")
                
        return count