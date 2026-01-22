import sys
from pathlib import Path
# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.database.session import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database tables created successfully!")
    