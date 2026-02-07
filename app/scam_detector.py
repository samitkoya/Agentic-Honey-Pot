"""Scam detection using Gemini LLM."""

import google.generativeai as genai
from .config import GEMINI_API_KEY


class ScamDetector:
    """Detects scam intent using Gemini LLM."""
    
    def __init__(self):
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize Gemini LLM."""
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.llm_available = True
        else:
            self.llm_available = False
    
    async def detect(self, text: str, history: list = None) -> tuple[bool, float, str]:
        """
        Detect if message is a scam using Gemini.
        
        Returns:
            Tuple of (is_scam, confidence, scam_type)
        """
        if not self.llm_available:
            return False, 0.0, "unknown"
        
        context = ""
        if history:
            context = "\n".join([f"{m.sender}: {m.text}" for m in history[-5:]])
        
        prompt = f"""Analyze this message for scam/fraud intent.

{f"Previous conversation:\n{context}" if context else ""}

Current message: "{text}"

Respond in this exact format:
IS_SCAM: [yes/no]
CONFIDENCE: [0.0-1.0]
SCAM_TYPE: [bank_fraud/upi_fraud/phishing/fake_offer/unknown]"""

        try:
            response = await self.model.generate_content_async(prompt)
            result = response.text
            
            # Parse response
            is_scam = "yes" in result.lower().split("is_scam:")[1].split("\n")[0].lower()
            confidence_line = result.lower().split("confidence:")[1].split("\n")[0]
            confidence = float(''.join(c for c in confidence_line if c.isdigit() or c == '.') or "0.5")
            scam_type_line = result.lower().split("scam_type:")[1].split("\n")[0]
            scam_type = scam_type_line.strip().replace(" ", "_")
            
            return is_scam, min(confidence, 1.0), scam_type
            
        except Exception as e:
            print(f"Scam detection error: {e}")
            return False, 0.0, "unknown"


# Global instance
scam_detector = ScamDetector()
