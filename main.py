import os
import sys
from app.database.session import SessionLocal
from app.database.models import User, Article
from app.services.scraper_service import ScraperService
from app.services.llm_service import LLMService
from app.services.ranking_service import RankingService
from app.services.email_services import EmailService

def main():
    print("=================================================")
    print("   🚀 INSIGHT DIGEST AI - DAILY AUTOMATION        ")
    print("=================================================\n")

    # ---------------------------------------------------------
    # STEP 1: SCRAPING
    # ---------------------------------------------------------
    print(">>> [1/4] Running Scraper...")
    try:
        scraper = ScraperService()
        scraper.run_pipeline()
    except Exception as e:
        print(f"❌ Scraper Failed: {e}")

    print("\n-------------------------------------------------\n")

    # ---------------------------------------------------------
    # STEP 2: SUMMARIZATION (AI)
    # ---------------------------------------------------------
    print(">>> [2/4] Running AI Summarizer...")
    try:
        llm_service = LLMService()
        llm_service.run()
    except Exception as e:
        print(f"❌ Summarizer Failed: {e}")

    print("\n-------------------------------------------------\n")

    # ---------------------------------------------------------
    # STEP 3 & 4: RANKING & EMAILING (Per User)
    # ---------------------------------------------------------
    print(">>> [3/4] Starting User Delivery Pipeline...")
    
    db = SessionLocal()
    users = db.query(User).all()
    
    ranking_service = RankingService()
    email_service = EmailService()
    
    print(f"   👥 Found {len(users)} users to process.\n")

    for user in users:
        safe_name = getattr(user, "name", getattr(user, "username", user.email.split("@")[0]))
        
        print(f"   👤 Processing: {safe_name} ({user.email})")
        top_articles = ranking_service.rank_articles(user.id, limit=5)

        if not top_articles:
            print("      ⚠️ No relevant articles found. Skipping email.")
            continue
        
        print(f"      🏆 Ranked {len(top_articles)} relevant articles.")
        article_titles = [a.title for a in top_articles]
        
        print("      🧠 Generating executive summary...")
        try:
            intro = llm_service.generate_digest_intro(article_titles, user_name=safe_name)
        except Exception:
            intro = f"Hi {safe_name}, here is your curated tech digest for today."
        print(f"      📤 Sending email to {user.email}...")
        email_service.send_digest(
            user_email=user.email,
            user_name=safe_name,
            articles=top_articles,
            intro_text=intro
        )
        print("      ✅ Done.")
        print("      " + "-"*30)

    db.close()

    print("\n=================================================")
    print("   ✅ DONE! DAILY AUTOMATION COMPLETE.")
    print("=================================================")

if __name__ == "__main__":
    main()