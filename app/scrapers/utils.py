from datetime import datetime
from sqlalchemy.orm import Session 
from app.database.models import Source, Article

def get_or_create_source(db: Session, name: str, base_url: str, scraper_type: str = None) -> Source:
    """
    Checks if a Source exists by its URL. If not, creates it.
    """
    source = db.query(Source).filter(Source.base_url == base_url).first()
    
    if not source:
       
        source = Source(
            name=name, 
            base_url=base_url,
           
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        
    return source

def save_article(db: Session, source_id: int, title: str, url: str, published_at: datetime = None, content: str = None):
    """
    Saves an article if it doesn't already exist.
    """
    # Check for duplicates
    existing = db.query(Article).filter(Article.url == url).first()
    if existing:
        return None  # Skip duplicate

    # Default to now if no date provided
    if not published_at:
        published_at = datetime.now()

    new_article = Article(
        source_id=source_id,
        title=title,
        url=url,
        published_at=published_at,
        raw_content=content
    )
    
    db.add(new_article)
    db.commit()
    print(f"      + Saved: {title[:40]}...")
    return new_article