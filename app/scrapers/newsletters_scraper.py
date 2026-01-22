import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.scrapers.utils import get_or_create_source, save_article

try:
    from app.config.news_letters import NEWSLETTERS
except ImportError:
    NEWSLETTERS = []

class NewsletterScraper:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        print(f"      ▶ Scraping {len(NEWSLETTERS)} Newsletters (Filter: <7 days)...")
        count = 0
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        headers = {'User-Agent': 'Mozilla/5.0'}

        for entry in NEWSLETTERS:
            try:
                # 1. SMART URL DETECTION
                # We prioritize the 'rss' key, then 'rss_url', then fallback to 'url'
                if isinstance(entry, dict):
                    rss_link = entry.get('rss') or entry.get('rss_url')
                    web_link = entry.get('url')
                    name = entry.get('name', "Newsletter")
                    
                    if rss_link:
                        url = rss_link
                        is_rss = True
                    else:
                        url = web_link
                        is_rss = False
                else:
                    # Handle if user just put a string in the list
                    url = entry
                    name = "Newsletter"
                    is_rss = "feed" in url or "rss" in url or "substack" in url

                if not url: continue
                
                # Register source (using the name you gave it)
                source = get_or_create_source(self.db, name, url, "newsletter")

                # 2. SCRAPE (RSS vs HTML)
                if is_rss:
                    # --- RSS MODE (Perfect for these 3) ---
                    feed = feedparser.parse(url)
                    for item in feed.entries[:5]:
                        try:
                            # Date Check
                            if hasattr(item, 'published_parsed') and item.published_parsed:
                                pub_date = datetime(*item.published_parsed[:6], tzinfo=timezone.utc)
                                if pub_date < cutoff_date:
                                    continue
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
                            content=f"Newsletter Issue: {item.summary if 'summary' in item else item.title}"
                        )
                        if saved: count += 1
                else:
                    # --- HTML MODE (Fallback) ---
                    resp = requests.get(url, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.content, 'html.parser')
                        # Grab first main link
                        found_link = None
                        for h in soup.find_all(['h1', 'h2'])[:2]:
                            a = h.find('a')
                            if a and a.get('href'):
                                found_link = a
                                break
                        
                        if found_link:
                            full_link = found_link['href'] if found_link['href'].startswith('http') else url.rstrip('/') + found_link['href']
                            saved = save_article(
                                self.db,
                                source_id=source.id,
                                title=found_link.get_text(strip=True),
                                url=full_link,
                                published_at=datetime.now(timezone.utc),
                                content="Read full newsletter at source"
                            )
                            if saved: count += 1

            except Exception as e:
                print(f"      ❌ Error scraping {name}: {e}")

        return count