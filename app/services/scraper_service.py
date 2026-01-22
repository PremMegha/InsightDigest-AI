import sys
import os
from app.database.session import SessionLocal 


sys.path.append(os.getcwd())

from app.scrapers.youtube_scraper import YoutubeScraper
from app.scrapers.blog_scraper import BlogScraper
from app.scrapers.newsletters_scraper import NewsletterScraper

class ScraperService:
    def __init__(self):
        self.db = SessionLocal()
        self.youtube = YoutubeScraper(self.db)
        self.blog = BlogScraper(self.db)
        self.newsletter = NewsletterScraper(self.db)

    def run_pipeline(self):
        print("\n🕷️  Starting Full Scraper Pipeline...")
        
        # 1. YouTube
        print("\n📺 --- 1. YouTube Scraper ---")
        try:
            self.youtube.run() 
        except Exception as e:
            print(f"   ❌ YouTube Error: {e}")

        # 2. Blogs
        print("\n📝 --- 2. Blog Scraper ---")
        try:
            self.blog.run()
        except Exception as e:
            print(f"   ❌ Blog Error: {e}")

        # 3. Newsletters
        print("\n📧 --- 3. Newsletter Scraper ---")
        try:
            self.newsletter.run()
        except Exception as e:
            print(f"   ❌ Newsletter Error: {e}")

        # Close DB when done
        self.db.close()
        print(f"\n✨ Pipeline Complete.")

if __name__ == "__main__":
    ScraperService().run_pipeline()