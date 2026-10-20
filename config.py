import os

GROQ_API       = os.environ.get("GROQ_API", "")
MODEL          = "llama-3.3-70b-versatile"
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID        = os.environ.get("CHAT_ID", "")
DB_PATH        = "predictions.db"
FF_XML_URL     = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
FRED_API       = os.environ.get("FRED_API", "")
PREDICT_HOURS_BEFORE = 36
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"
