import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser
from sqlalchemy.orm import Session
from app.scrapers.utils import get_or_create_source, save_article

try:
    from app.config.blog_sources import BLOG_SOURCES
except ImportError:
    BLOG_SOURCES = []

class BlogScraper:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        print(f"      ▶ Scraping {len(BLOG_SOURCES)} Blogs (Filter: <7 days)...")
        count = 0
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        headers = {'User-Agent': 'Mozilla/5.0'}

        for entry in BLOG_SOURCES:
            try:
                # Setup
                if isinstance(entry, dict):
                    url = entry.get('rss_url') or entry.get('url')
                    name = entry.get('name', "Tech Blog")
                    is_rss = 'rss' in url or 'feed' in url
                else:
                    url = entry
                    name = "Tech Blog"
                    is_rss = False # Default to HTML if string provided (unless obvious)

                if not url: continue
                source = get_or_create_source(self.db, name, url, "blog")

                if is_rss:
                    # --- RSS STRATEGY (Better for dates) ---
                    feed = feedparser.parse(url)
                    for item in feed.entries[:5]:
                        # DATE CHECK
                        try:
                            if hasattr(item, 'published_parsed') and item.published_parsed:
                                pub_date = datetime(*item.published_parsed[:6], tzinfo=timezone.utc)
                                if pub_date < cutoff_date:
                                    continue # Skip old
                            else:
                                pub_date = datetime.now(timezone.utc)
                        except:
                            pub_date = datetime.now(timezone.utc)

                        saved = save_article(
                            self.db,
                            source_id=source.id,
                            title=item.title,
                            url=item.link,
                            published_at=pub_date,
                            content=f"Summary: {item.summary if 'summary' in item else item.title}"
                        )
                        if saved: count += 1
                else:
                    # --- HTML STRATEGY (Harder to check date, assume strict or grab meta) ---
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, 'html.parser')
                        
                        # Try to find recent articles only
                        # (HTML scraping without dates is risky, we will grab top 3 and assume they are new)
                        for h2 in soup.find_all('h2')[:3]:
                            a = h2.find('a')
                            if a and a.get('href'):
                                full_link = a['href'] if a['href'].startswith('http') else url.rstrip('/') + a['href']
                                
                                # We can't easily verify date on raw HTML without complex parsing
                                # So we save it, assuming the top of the blog is new.
                                saved = save_article(
                                    self.db,
                                    source_id=source.id,
                                    title=a.get_text(strip=True),
                                    url=full_link,
                                    content="Read more at source"
                                )
                                if saved: count += 1

            except Exception as e:
                print(f"      ❌ Error scraping {url}: {e}")

        return count