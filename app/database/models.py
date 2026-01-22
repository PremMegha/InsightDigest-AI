from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, date  

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    interests = relationship("UserInterest", back_populates="user")

class UserInterest(Base):
    __tablename__ = "user_interests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    
    user = relationship("User", back_populates="interests")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String)
    rss_feed_url = Column(String)
    reliability_score = Column(Float, default=5.0)
    
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    title = Column(String, nullable=False, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    published_at = Column(DateTime, nullable=False)
    raw_content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="articles")

class Digest(Base):
    __tablename__ = "digests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    article_id = Column(Integer, ForeignKey("articles.id"))
    rank = Column(Integer)
    digest_date = Column(Date, default=date.today)

   
    article = relationship("Article")