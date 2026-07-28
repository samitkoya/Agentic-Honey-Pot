import google.generativeai as genai
from .config import GEMINI_API_KEY


async def detect_scam(text: str, history: list = None) -> tuple[bool, float, str]:
    if not GEMINI_API_KEY:
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
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        response = await model.generate_content_async(prompt)
        result = response.text
        
        is_scam = "yes" in result.lower().split("is_scam:")[1].split("\n")[0].lower()
        confidence_line = result.lower().split("confidence:")[1].split("\n")[0]
        confidence = float(''.join(c for c in confidence_line if c.isdigit() or c == '.') or "0.5")
        scam_type_line = result.lower().split("scam_type:")[1].split("\n")[0]
        scam_type = scam_type_line.strip().replace(" ", "_")
        
        return is_scam, min(confidence, 1.0), scam_type
        
    except Exception as e:
        print(f"Scam detection error: {e}")
        return False, 0.0, "unknown"
