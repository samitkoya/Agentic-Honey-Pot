"""Intelligence extraction from conversations."""

import re
from typing import List, Set
from models import ExtractedIntelligence, Message
from config import SCAM_KEYWORDS


class IntelligenceExtractor:
    """Extracts actionable intelligence from scam conversations."""
    
    # Regex patterns for intelligence extraction
    BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{9,18}\b')
    UPI_ID_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+', re.IGNORECASE)
    PHONE_PATTERN = re.compile(r'(\+91[\-\s]?)?[789]\d{9}\b')
    URL_PATTERN = re.compile(r'https?://[^\s<>"\'{}|\\^`\[\]]+', re.IGNORECASE)
    
    def __init__(self):
        self.scam_keywords = set(kw.lower() for kw in SCAM_KEYWORDS)
    
    def extract_bank_accounts(self, text: str) -> List[str]:
        """Extract potential bank account numbers."""
        matches = self.BANK_ACCOUNT_PATTERN.findall(text)
        # Filter out common non-account numbers (timestamps, etc.)
        return [m for m in matches if len(m) >= 10 and not m.startswith('20')]
    
    def extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs (format: name@bank)."""
        matches = self.UPI_ID_PATTERN.findall(text)
        # Filter out email addresses
        return [m for m in matches if not any(domain in m.lower() for domain in 
                ['gmail', 'yahoo', 'hotmail', 'outlook', 'email'])]
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract Indian phone numbers."""
        matches = self.PHONE_PATTERN.findall(text)
        # Clean and format
        cleaned = []
        for match in matches:
            if isinstance(match, tuple):
                match = ''.join(match)
            clean = re.sub(r'[\s\-]', '', match)
            if not clean.startswith('+91'):
                clean = '+91' + clean[-10:]
            cleaned.append(clean)
        return cleaned
    
    def extract_phishing_links(self, text: str) -> List[str]:
        """Extract suspicious URLs."""
        matches = self.URL_PATTERN.findall(text)
        suspicious = []
        for url in matches:
            # Flag suspicious patterns
            suspicious_indicators = [
                'bit.ly', 'tinyurl', 'goo.gl', 't.co',  # URL shorteners
                'login', 'verify', 'update', 'secure',  # Phishing keywords
                '.xyz', '.tk', '.ml', '.ga', '.cf',  # Suspicious TLDs
                'bank', 'upi', 'payment'  # Financial keywords
            ]
            if any(ind in url.lower() for ind in suspicious_indicators):
                suspicious.append(url)
            elif not any(safe in url.lower() for safe in ['google.com', 'microsoft.com', 'apple.com']):
                suspicious.append(url)
        return suspicious
    
    def extract_suspicious_keywords(self, text: str) -> List[str]:
        """Extract suspicious keywords from text."""
        text_lower = text.lower()
        found = []
        for keyword in self.scam_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found
    
    def extract_from_text(self, text: str) -> ExtractedIntelligence:
        """Extract all intelligence from a single text."""
        return ExtractedIntelligence(
            bankAccounts=self.extract_bank_accounts(text),
            upiIds=self.extract_upi_ids(text),
            phishingLinks=self.extract_phishing_links(text),
            phoneNumbers=self.extract_phone_numbers(text),
            suspiciousKeywords=self.extract_suspicious_keywords(text)
        )
    
    def extract_from_conversation(self, messages: List[Message]) -> ExtractedIntelligence:
        """Extract intelligence from entire conversation history."""
        combined = ExtractedIntelligence()
        
        for message in messages:
            if message.sender == "scammer":
                intel = self.extract_from_text(message.text)
                combined.bankAccounts.extend(intel.bankAccounts)
                combined.upiIds.extend(intel.upiIds)
                combined.phishingLinks.extend(intel.phishingLinks)
                combined.phoneNumbers.extend(intel.phoneNumbers)
                combined.suspiciousKeywords.extend(intel.suspiciousKeywords)
        
        # Remove duplicates
        combined.bankAccounts = list(set(combined.bankAccounts))
        combined.upiIds = list(set(combined.upiIds))
        combined.phishingLinks = list(set(combined.phishingLinks))
        combined.phoneNumbers = list(set(combined.phoneNumbers))
        combined.suspiciousKeywords = list(set(combined.suspiciousKeywords))
        
        return combined


# Global instance
intelligence_extractor = IntelligenceExtractor()
