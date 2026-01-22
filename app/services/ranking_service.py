from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models import User, Article

class RankingService:
    def __init__(self):
        self.db = SessionLocal()

    def get_keywords_from_user(self, user):
        """
        Safely extracts keywords whether 'interests' is a String or a Relationship List.
        """
        raw_interests = getattr(user, "interests", None)
        
        if not raw_interests:
            raw_interests = getattr(user, "preferences", None)

        if not raw_interests:
            return []

        keywords = []

      
        if isinstance(raw_interests, str):
            keywords = [k.strip().lower() for k in raw_interests.split(',')]

      
        else:
            try:
                for item in raw_interests:
                    if hasattr(item, 'name'):
                        keywords.append(str(item.name).lower())
                    elif hasattr(item, 'topic'):
                        keywords.append(str(item.topic).lower())
                    elif hasattr(item, 'value'):
                        keywords.append(str(item.value).lower())
                    else:
                        keywords.append(str(item).lower())
            except TypeError:
                pass
        
        return keywords

    def rank_articles(self, user_id, limit=5):
        user = self.db.query(User).filter(User.id == user_id).first()
        
        articles = self.db.query(Article).filter(Article.summary != None).all()

        if not user or not articles:
            return []

        scored_articles = []
        
        user_keywords = self.get_keywords_from_user(user)

        if not user_keywords:
            return []

        for article in articles:
            score = 0
            content_lower = (article.title + " " + (article.summary or "")).lower()
            
            for keyword in user_keywords:
                if keyword in content_lower:
                    score += 1
            
            if score > 0:
                scored_articles.append((article, score))

        scored_articles.sort(key=lambda x: x[1], reverse=True)
        final_list = [item[0] for item in scored_articles]

        return final_list[:limit]

    def run(self):
        print("🚀 Starting Daily Ranking Process (Universal Mode)...")
        
        users = self.db.query(User).all()
        articles = self.db.query(Article).filter(Article.summary != None).all()
        print(f"   📊 Loaded {len(articles)} processed articles available for ranking.\n")

        results = {}

        for user in users:
            safe_name = getattr(user, "name", getattr(user, "username", user.email))
            print(f"   👤 Ranking for: {safe_name}")
            
            top_picks = self.rank_articles(user.id)
            
            if top_picks:
                print(f"      🏆 Found {len(top_picks)} relevant articles.")
                results[user.email] = top_picks
            else:
                print(f"      ⚠️ No matching articles found (or no interests defined).")

        self.db.close()
        print("\n🏁 Ranking Process Complete.")
        return results

if __name__ == "__main__":
    RankingService().run()