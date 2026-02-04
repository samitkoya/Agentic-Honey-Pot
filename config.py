"""Configuration management for the Agentic Honey-Pot system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Authentication
API_KEY = os.getenv("API_KEY", "default-secret-key")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "openai"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Engagement settings
ENGAGEMENT_THRESHOLD = int(os.getenv("ENGAGEMENT_THRESHOLD", "5"))

# GUVI Callback endpoint
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Scam detection keywords
SCAM_KEYWORDS = [
    "urgent", "verify", "blocked", "suspend", "otp", "click", "link",
    "account", "bank", "upi", "immediately", "action required", "expired",
    "warning", "alert", "security", "unauthorized", "locked", "pending",
    "confirm", "update", "validate", "kyc", "pan", "aadhaar", "deactivate",
    "refund", "lottery", "prize", "winner", "claim", "offer", "limited time"
]

# Scam patterns
SCAM_PATTERNS = {
    "bank_fraud": ["bank account", "blocked", "suspend", "deactivate", "unauthorized transaction"],
    "upi_fraud": ["upi", "upi id", "upi pin", "payment failed", "refund"],
    "phishing": ["click here", "verify now", "update details", "login", "password"],
    "fake_offer": ["winner", "prize", "lottery", "claim", "offer", "cashback", "reward"]
}
