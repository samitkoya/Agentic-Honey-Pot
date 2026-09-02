import re
from typing import List
from .models import ExtractedIntelligence
from .config import SCAM_KEYWORDS

BANK_ACCOUNT_PATTERN = re.compile(r'\b\d{9,18}\b')
UPI_ID_PATTERN = re.compile(r'[a-zA-Z0-9._-]+@[a-zA-Z0-9]+', re.IGNORECASE)
PHONE_PATTERN = re.compile(r'(?:\+91[\-\s]?)?[789]\d{9}\b')
URL_PATTERN = re.compile(r'https?://[^\s<>"\'{}|\\^`\[\]]+', re.IGNORECASE)
IFSC_PATTERN = re.compile(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', re.IGNORECASE)
NAME_PATTERN = re.compile(r'(?i)(?:name|officer)[\s:]+([A-Za-z\s]{3,30})(?:\n|$)')
ADDRESS_PATTERN = re.compile(r'(?i)address[\s:]+([A-Za-z0-9\s,\.\-]{10,100})(?:\n|$)')


def extract_bank_accounts(text: str) -> List[str]:
    matches = BANK_ACCOUNT_PATTERN.findall(text)
    valid = []
    for m in matches:
        if len(m) >= 10 and not m.startswith('20'):
            # Exclude 10-digit Indian phone numbers
            if len(m) == 10 and m[0] in '6789':
                continue
            valid.append(m)
    return valid


def extract_upi_ids(text: str) -> List[str]:
    return UPI_ID_PATTERN.findall(text)


def extract_phone_numbers(text: str) -> List[str]:
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
    text_lower = text.lower()
    return [kw for kw in SCAM_KEYWORDS if kw in text_lower]


def extract_ifsc_codes(text: str) -> List[str]:
    return [m.upper() for m in IFSC_PATTERN.findall(text)]


def extract_names(text: str) -> List[str]:
    return [m.strip() for m in NAME_PATTERN.findall(text)]


def extract_addresses(text: str) -> List[str]:
    return [m.strip() for m in ADDRESS_PATTERN.findall(text)]


def extract_intelligence(text: str) -> ExtractedIntelligence:
    return ExtractedIntelligence(
        bankAccounts=extract_bank_accounts(text),
        upiIds=extract_upi_ids(text),
        phishingLinks=extract_phishing_links(text),
        phoneNumbers=extract_phone_numbers(text),
        suspiciousKeywords=extract_suspicious_keywords(text),
        ifscCodes=extract_ifsc_codes(text),
        names=extract_names(text),
        addresses=extract_addresses(text)
    )


import json
import google.generativeai as genai

async def extract_intelligence_async(text: str) -> ExtractedIntelligence:
    base_intel = extract_intelligence(text)
    from .config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        return base_intel
        
    prompt = f"""
    Extract the following entities from the provided text. Return ONLY a valid JSON object with these exact keys:
    - "bankAccounts" (list of strings, usually 9-18 digits)
    - "upiIds" (list of strings, e.g. someone@okicici)
    - "phishingLinks" (list of strings, URLs)
    - "phoneNumbers" (list of strings)
    - "ifscCodes" (list of strings)
    - "names" (list of strings, person names or officer names)
    - "addresses" (list of strings, physical locations)
    
    If none found for a category, use an empty list. Do not include markdown formatting, just the raw JSON object.
    
    TEXT: "{text}"
    """
    
    try:
        model = genai.GenerativeModel('gemini-3.5-flash-lite')
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Fallback if the model still wraps in markdown or returns invalid JSON
            cleaned_text = response.text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            data = json.loads(cleaned_text.strip())

        base_intel.bankAccounts = list(set(base_intel.bankAccounts + data.get("bankAccounts", [])))
        base_intel.upiIds = list(set(base_intel.upiIds + data.get("upiIds", [])))
        base_intel.phishingLinks = list(set(base_intel.phishingLinks + data.get("phishingLinks", [])))
        base_intel.phoneNumbers = list(set(base_intel.phoneNumbers + data.get("phoneNumbers", [])))
        base_intel.ifscCodes = list(set(base_intel.ifscCodes + data.get("ifscCodes", [])))
        base_intel.names = list(set(base_intel.names + data.get("names", [])))
        base_intel.addresses = list(set(base_intel.addresses + data.get("addresses", [])))
        
    except Exception as e:
        print(f"Extraction LLM error: {e}")
        
    return base_intel
