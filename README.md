🚀 InsightDigest AI: Personalized GenAI Content Aggregator
InsightDigest AI is a professional-grade generative AI application that automates the discovery, summarization, and delivery of technical content. 
It solves "information overload" by scraping multiple sources and using Llama 3.1 to deliver only the most relevant insights directly to a user's inbox.

📖 Project Overview
In an era of endless content, staying updated is difficult. This project provides a "Strict-Mode" digest system. 
It doesn't just collect news—it filters it against specific user interests (like Python, AI, or Web Development) and generates high-quality executive summaries.

Core Features
🕷️ Multi-Platform Scraping: Modular scrapers for YouTube (Channels/Playlists), Technical Blogs (RSS/Atom), and Newsletters.
🧠 Intelligence by Llama 3.1: Summarizes complex technical articles into digestible bullet points using the Groq API.
📊 Strict-Mode Ranking: A custom algorithm that matches content against user-defined interest profiles to eliminate noise.
📧 Professional Delivery: Automated SMTP service that sends personalized, responsive HTML emails.
🐳 Containerized Database: PostgreSQL integration managed via Docker for reliable and scalable data persistence.

🛠️ Technical Stack
Language: Python 3.10+
LLM Engine: Llama 3.1 (via Groq API)
Database: PostgreSQL (with SQLAlchemy ORM)
Infrastructure: Docker & Docker-Compose
Email: SMTP with Jinja2 HTML Templating
Environment: Secure .env credential management

⚙️ Setup & Installation

1. Clone the Repository
git clone https://github.com/PremMegha/InsightDigest-AI.git
cd InsightDigest-AI

2. Configure Environment Variables
Create a .env file in the root directory and add your credentials:


# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=insight_digest

# AI Service
GROQ_API_KEY=your_groq_api_key

# Email Service
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password

3. Install Dependencies
pip install -r requirements.txt

4. Run the Application
python main.py



🏗️ Architecture
->The project is built using a service-oriented architecture to ensure maintainability:
Scraper Service: Fetches raw data and stores it in the Article table.
LLM Service: Identifies un-summarized articles and generates AI summaries.
Ranking Service: Matches summaries against user interest keywords.
Email Service: Renders the Jinja2 template and dispatches the final digest.


🛡️ Security & Privacy
Credential Masking: All API keys and passwords are excluded from Git via .gitignore.
Anonymized Data: User profiles in the demo database use placeholder emails to protect privacy.
Error Handling: Robust try-except blocks ensure the pipeline continues even if one source or API call fails.

👨‍💻 Author
Prem Megha - Computer Engineer & Full-Stack Developer  (https://www.google.com/search?q=https://github.com/PremMegha).
