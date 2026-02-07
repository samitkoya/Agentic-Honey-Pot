"""Configuration management for the Agentic Honey-Pot system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Authentication
API_KEY = os.getenv("API_KEY", "default-secret-key")

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Engagement threshold (number of messages before sending callback)
ENGAGEMENT_THRESHOLD = int(os.getenv("ENGAGEMENT_THRESHOLD", "10"))

# Scam detection keywords
SCAM_KEYWORDS = [
    "lottery", "prize", "won", "winner", "claim", "bank", "account", "transfer",
    "otp", "verify", "urgent", "blocked", "suspend", "kyc", "update", "link",
    "click", "upi", "payment", "refund", "cashback", "offer", "scheme",
    "government", "rbi", "sbi", "income tax", "free", "gift", "lucky"
]
