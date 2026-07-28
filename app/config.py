import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY", "default-secret-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SCAM_KEYWORDS = {
    "lottery", "prize", "won", "winner", "claim", "bank", "account", "transfer",
    "otp", "verify", "urgent", "blocked", "suspend", "kyc", "update", "link",
    "click", "upi", "payment", "refund", "cashback", "offer", "scheme",
    "government", "rbi", "sbi", "income tax", "free", "gift", "lucky"
}
