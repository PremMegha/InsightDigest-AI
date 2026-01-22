from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models import User, UserInterest

USER_PROFILES = [
    {
        "email": "PROFILE1@gmail.com",
        "interests": ["Python", "Kubernetes", "Backend", "DevOps", "API", "Database"]
    },
    {
        "email": "PROFILE2@gmail.com",
        "interests": ["LLM", "Generative AI", "Computer Vision", "Deep Learning", "Neural Networks", "NVIDIA"]
    },
    {
        "email": "PROFILE3@gmail.com",
        "interests": ["Startup", "Strategy", "Venture Capital", "Product Management", "Leadership", "Tech Trends"]
    }
]

def seed_users():
    print("🌱 Seeding Multiple User Profiles...")
    db: Session = SessionLocal()

    for profile in USER_PROFILES:
        email = profile["email"]
        interests = profile["interests"]
        
        print(f"\n   👤 Processing User: {email}")

        # 1. Create or Get User
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Using dummy hash for now
            user = User(email=email, password_hash="dummy_hash_123")
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"      ✅ Created new user (ID: {user.id})")
        else:
            print(f"      ℹ️ User exists (ID: {user.id})")

        # 2. Reset and Add Interests
        # We delete old interests first to avoid duplicates
        db.query(UserInterest).filter(UserInterest.user_id == user.id).delete()
        
        for topic in interests:
            interest = UserInterest(user_id=user.id, topic=topic)
            db.add(interest)
        
        db.commit()
        print(f"      ✅ Added interests: {', '.join(interests)}")
    
    db.close()
    print("\n🌱 Seeding Complete. Ready for Ranking.")

if __name__ == "__main__":
    seed_users()