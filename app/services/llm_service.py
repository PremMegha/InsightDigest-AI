import time
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models import Article
from groq import Groq 

# Force Load Env
load_dotenv(override=True) 
api_key = os.getenv("GROQ_API_KEY")

class LLMService:
    def __init__(self):
        self.db = SessionLocal()
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None

    def generate_summary(self, content: str) -> str:
        """Generates a summary for a single article."""
        if not self.client:
            return None

        prompt = f"""
        You are an expert tech editor. Summarize the following text into a concise, 
        insightful paragraph (3-4 sentences). Focus on the "Why it matters" and key technical details.
        
        TEXT:
        {content[:15000]} 
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"      ⚠️ Groq Error: {e}")
            return None

    def create_fallback_summary(self, content: str) -> str:
        """Creates a simple preview if AI fails."""
        if not content:
            return "No preview available."
        preview = content[:350].replace("\n", " ").strip()
        return f"{preview}..."

  
    def generate_digest_intro(self, article_titles: list, user_name: str = "Reader") -> str:
        """
        Generates a short, punchy 2-sentence intro for the email.
        Now uses the user's name for personalization!
        """
        if not self.client or not article_titles:
            return f"Hi {user_name}, here is your daily tech digest, curated just for you."

        titles_text = ", ".join(article_titles[:3])
        
       
        prompt = f"""
        Write a friendly, exciting 1-sentence introduction for a daily tech newsletter for a user named "{user_name}".
        Mention that today's issue covers topics like: {titles_text}.
        Keep it professional but energetic. Do not use quotes.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception:
            return f"Hi {user_name}, here are the top trending tech stories curated for you today."

    def run(self):
        print("🧠 LLM Service (Groq/Llama-3.1): Finding un-summarized articles...")
        
        articles = self.db.query(Article).filter(Article.summary == None).all()
        print(f"   ▶ Found {len(articles)} articles to process.")
        
        if not articles:
            return

        for i, article in enumerate(articles, 1):
            print(f"   🧠 [{i}/{len(articles)}] Processing: {article.title[:40]}...")

            attempts = 0
            max_retries = 3
            success = False

            while attempts < max_retries and not success:
                try:
                    summary = self.generate_summary(article.raw_content or article.title)
                    
                    if summary:
                        article.summary = summary
                        if hasattr(article, 'processed_at'):
                             article.processed_at = datetime.utcnow()
                        elif hasattr(article, 'process'):
                             article.process = True
                        
                        self.db.commit()
                        success = True
                        time.sleep(2)
                    else:
                        break 

                except Exception as e:
                    if "429" in str(e): # Rate Limit
                        print("      ⚠️ Rate Limit Hit. Cooling down for 30s...")
                        time.sleep(30) 
                        attempts += 1
                    else:
                        print(f"      ❌ Error: {e}")
                        break 
            
            
            if not success:
                 print("      ⚠️ AI Failed. Generating fallback preview...")
                 fallback = self.create_fallback_summary(article.raw_content or article.title)
                 article.summary = fallback
                 if hasattr(article, 'processed_at'):
                        article.processed_at = datetime.utcnow()
                 elif hasattr(article, 'process'):
                        article.process = True
                 self.db.commit()

        self.db.close()
        print("✅ LLM Processing Complete.")

if __name__ == "__main__":
    LLMService().run()