"""Scam detection engine using keyword matching and LLM classification."""

from typing import Tuple, Optional
import google.generativeai as genai
from .config import (
    LLM_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY,
    SCAM_KEYWORDS, SCAM_PATTERNS
)


class ScamDetector:
    """Detects scam intent in messages using hybrid approach."""
    
    def __init__(self):
        self.scam_keywords = set(kw.lower() for kw in SCAM_KEYWORDS)
        self.scam_patterns = SCAM_PATTERNS
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize the LLM based on provider."""
        if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.llm_available = True
        elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            import openai
            openai.api_key = OPENAI_API_KEY
            self.llm_available = True
        else:
            self.llm_available = False
    
    def _keyword_score(self, text: str) -> Tuple[float, list]:
        """Calculate keyword-based scam score."""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.scam_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        if not found_keywords:
            return 0.0, []
        
        # Score based on number of keywords found
        score = min(len(found_keywords) / 5, 1.0)  # Cap at 1.0
        return score, found_keywords
    
    def _pattern_match(self, text: str) -> Tuple[str, float]:
        """Match against known scam patterns."""
        text_lower = text.lower()
        best_match = ("unknown", 0.0)
        
        for scam_type, patterns in self.scam_patterns.items():
            matches = sum(1 for p in patterns if p in text_lower)
            if matches > 0:
                score = matches / len(patterns)
                if score > best_match[1]:
                    best_match = (scam_type, score)
        
        return best_match
    
    async def _llm_classify(self, text: str, history: list = None) -> Tuple[bool, float, str]:
        """Use LLM to classify scam intent."""
        if not self.llm_available:
            return False, 0.0, "unknown"
        
        context = ""
        if history:
            context = "\n".join([f"{m.sender}: {m.text}" for m in history[-5:]])
        
        prompt = f"""Analyze this message for scam/fraud intent. Consider:
- Bank fraud (account blocking threats, unauthorized access claims)
- UPI fraud (payment requests, refund scams)
- Phishing (fake links, credential requests)
- Fake offers (lottery, prizes, too-good-to-be-true deals)

{"Previous conversation:" + context if context else ""}

Current message: "{text}"

Respond in this exact format:
IS_SCAM: [yes/no]
CONFIDENCE: [0.0-1.0]
SCAM_TYPE: [bank_fraud/upi_fraud/phishing/fake_offer/unknown]
REASON: [brief explanation]"""

        try:
            if LLM_PROVIDER == "gemini":
                response = await self.model.generate_content_async(prompt)
                result = response.text
            else:
                # OpenAI implementation
                import openai
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content
            
            # Parse response
            is_scam = "yes" in result.lower().split("is_scam:")[1].split("\n")[0].lower()
            confidence_line = result.lower().split("confidence:")[1].split("\n")[0]
            confidence = float(''.join(c for c in confidence_line if c.isdigit() or c == '.') or "0.5")
            scam_type_line = result.lower().split("scam_type:")[1].split("\n")[0]
            scam_type = scam_type_line.strip().replace(" ", "_")
            
            return is_scam, min(confidence, 1.0), scam_type
            
        except Exception as e:
            print(f"LLM classification error: {e}")
            return False, 0.0, "unknown"
    
    async def detect(self, text: str, history: list = None) -> Tuple[bool, float, str]:
        """
        Main detection method combining keyword and LLM analysis.
        
        Returns:
            Tuple of (is_scam, confidence, scam_type)
        """
        # Step 1: Keyword analysis
        keyword_score, keywords = self._keyword_score(text)
        
        # Step 2: Pattern matching
        pattern_type, pattern_score = self._pattern_match(text)
        
        # Step 3: LLM classification (if available)
        llm_is_scam, llm_confidence, llm_type = False, 0.0, "unknown"
        if self.llm_available and keyword_score > 0.2:
            llm_is_scam, llm_confidence, llm_type = await self._llm_classify(text, history)
        
        # Combine scores
        # Weight: keywords (0.3), patterns (0.2), LLM (0.5)
        if self.llm_available and llm_confidence > 0:
            final_confidence = (keyword_score * 0.3) + (pattern_score * 0.2) + (llm_confidence * 0.5)
            final_type = llm_type if llm_confidence > 0.5 else pattern_type
        else:
            final_confidence = (keyword_score * 0.6) + (pattern_score * 0.4)
            final_type = pattern_type
        
        is_scam = final_confidence >= 0.4  # Threshold for scam detection
        
        return is_scam, final_confidence, final_type


# Global instance
scam_detector = ScamDetector()
