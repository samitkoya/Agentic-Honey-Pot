"""Intelligence extraction from conversations."""

import re
from typing import List
from .models import ExtractedIntelligence
from .config import SCAM_KEYWORDS

BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{9,18}\b')
UPI_ID_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(\+91[\-\s]?)?[789]\d{9}\b')
URL_PATTERN = re.compile(r'https?://[^\s<>"\'{}|\\^`\[\]]+', re.IGNORECASE)
EXCLUDED_DOMAINS = {'gmail', 'yahoo', 'hotmail', 'outlook', 'email'}


def extract_bank_accounts(text: str) -> List[str]:
    """Extract potential bank account numbers."""
    matches = BANK_ACCOUNT_PATTERN.findall(text)
    return [m for m in matches if len(m) >= 10 and not m.startswith('20')]


def extract_upi_ids(text: str) -> List[str]:
    """Extract UPI IDs (format: name@bank)."""
    matches = UPI_ID_PATTERN.findall(text)
    return [m for m in matches if not any(domain in m.lower() for domain in EXCLUDED_DOMAINS)]


def extract_phone_numbers(text: str) -> List[str]:
    """Extract Indian phone numbers."""
    matches = PHONE_PATTERN.findall(text)
    cleaned = []
    for match in matches:
        m = ''.join(match) if isinstance(match, tuple) else match
        clean = re.sub(r'[\s\-]', '', m)
        if not clean.startswith('+91'):
            clean = '+91' + clean[-10:]
        cleaned.append(clean)
    return cleaned


def extract_phishing_links(text: str) -> List[str]:
    """Extract suspicious URLs."""
    matches = URL_PATTERN.findall(text)
    suspicious = []
    indicators = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'login', 'verify', 'update', 'secure', '.xyz', '.tk', '.ml', '.ga', '.cf', 'bank', 'upi', 'payment']
    safe_domains = ['google.com', 'microsoft.com', 'apple.com']
    for url in matches:
        url_lower = url.lower()
        if any(ind in url_lower for ind in indicators) or not any(s in url_lower for s in safe_domains):
            suspicious.append(url)
    return suspicious


def extract_suspicious_keywords(text: str) -> List[str]:
    """Extract suspicious keywords from text."""
    text_lower = text.lower()
    return [kw for kw in SCAM_KEYWORDS if kw in text_lower]


def extract_intelligence(text: str) -> ExtractedIntelligence:
    """Extract all intelligence from text."""
    return ExtractedIntelligence(
        bankAccounts=extract_bank_accounts(text),
        upiIds=extract_upi_ids(text),
        phishingLinks=extract_phishing_links(text),
        phoneNumbers=extract_phone_numbers(text),
        suspiciousKeywords=extract_suspicious_keywords(text)
    )

