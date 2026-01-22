import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

# Load environment variables
load_dotenv(override=True)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

class EmailService:
    def __init__(self):
        # Determine the path to the templates folder
        self.template_dir = os.path.join(os.getcwd(), 'app', 'templates')
        print(f"   📂 Loading templates from: {self.template_dir}")
        
        # Initialize Jinja2 environment
        try:
            self.env = Environment(loader=FileSystemLoader(self.template_dir))
        except Exception as e:
            print(f"      ❌ Template Error: {e}")
            self.env = None

    def send_digest(self, user_email, user_name, articles, intro_text):
        """
        Sends the personalized digest to the SPECIFIC user_email provided.
        """
        if not self.env:
            print("      ❌ Error: Template environment not initialized.")
            return

        if not articles:
            print(f"      ⚠️ No articles to send for {user_email}. Skipping.")
            return

        try:
            # 1. Setup the Email Connection
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)

            # 2. Create the Email Content
            msg = MIMEMultipart()
            msg['From'] = SMTP_EMAIL
            msg['To'] = user_email  
            msg['Subject'] = f"🚀 Insight Digest: Your Daily Tech Briefing"

            # 3. Render the HTML Template
            try:
                template = self.env.get_template('email_digest.html')
                html_content = template.render(
                    user_name=user_name,
                    user_email=user_email, 
                    intro_text=intro_text,
                    articles=articles
                )
                msg.attach(MIMEText(html_content, 'html'))
            except Exception as template_err:
                print(f"      ❌ Template Rendering Error: {template_err}")
                server.quit()
                return

            # 4. Send the Email
            server.sendmail(SMTP_EMAIL, user_email, msg.as_string())
            server.quit()

            print(f"      ✅ Email successfully sent to: {user_email}")

        except Exception as e:
            print(f"      ❌ Email Error: {e}")

if __name__ == "__main__":
    pass