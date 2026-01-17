from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create database directory
os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite:///data/release_os.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    als_path = Column(String, unique=True, nullable=True)  # Nullable for manual projects
    audio_path = Column(String)  # Path to uploaded audio file
    bpm = Column(Integer)
    key = Column(String)
    audio_clips_count = Column(Integer, default=0)
    longest_clip_path = Column(String)
    preview_path = Column(String)
    cover_path = Column(String)
    status = Column(String, default="idea")  # idea, exported, packaged, released
    genre = Column(String)
    vibe = Column(String)
    tags = Column(Text)  # Comma-separated tags
    soundcloud_url = Column(String)  # URL of uploaded track on SoundCloud
    soundcloud_uploaded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified = Column(DateTime)


class SoundCloudAuth(Base):
    __tablename__ = "soundcloud_auth"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    user_id = Column(String)  # SoundCloud user ID
    username = Column(String)  # SoundCloud username
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
