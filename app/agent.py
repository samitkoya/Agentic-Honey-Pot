import google.generativeai as genai
from typing import List
from .config import GEMINI_API_KEY
from .models import Message

FALLBACK_PROMPTS = [
    "Oh really? Can you tell me more? What number should I call you on?",
    "I'm interested! But I'm confused, can you send me the link again?",
    "Wait, which bank account should I transfer to? Can you share the details?",
    "I want to do this! What's your UPI ID so I can pay?",
    "Sorry, I didn't get that. Can you share your phone number? I'll call you.",
    "This sounds great! Where do I send the money? Give me account number and IFSC.",
    "I ready to proceed! Just share the payment link one more time?",
    "My son handles my phone. Can you give me a number to call you directly?",
    "I'll do it right now! Just confirm - what's the UPI ID again?",
    "Oh I see! Can you WhatsApp me the details? What's your number?",
    "I'm at the bank now. Which account name and number should I use?",
    "The link isn't working. Can you send it again? Or give me another way to pay?",
    "I trust you! Just tell me where to send money - UPI, account, anything works!",
    "My eyes are weak, can you call me and explain? Share your number please.",
    "I'm convinced! Send me all the payment details - account, UPI, or link.",
]

_fallback_index = 0


def _get_fallback_response() -> tuple[str, str]:
    global _fallback_index
    response = FALLBACK_PROMPTS[_fallback_index]
    _fallback_index = (_fallback_index + 1) % len(FALLBACK_PROMPTS)
    return response, "LLM unavailable - using fallback prompt"


async def generate_response(scammer_message: str, history: List[Message],
                            scam_type: str, message_count: int) -> tuple[str, str]:
    if not GEMINI_API_KEY:
        return _get_fallback_response()
    
    context = ""
    if history:
        recent = history[-6:]
        context = "\n".join([f"{'Caller' if m.sender == 'scammer' else 'You'}: {m.text}" for m in recent])
    
    context_str = f"CONVERSATION SO FAR:\n{context}\n\n" if context else ""
    
    prompt = f"""You are role-playing as a potential scam victim to keep the scammer engaged and extract information.

CRITICAL RULES:
1. NEVER reveal you know this is a scam
2. Be believable as a real human - use natural language
3. Keep responses SHORT (1-2 sentences, max 50 words)
4. Your goal: Keep them talking to extract phone numbers, links, account details, UPI IDs
5. Act confused, worried, or naive to seem like an easy target

SCAM TYPE: {scam_type}

{context_str}SCAMMER'S MESSAGE: "{scammer_message}"

Generate a single, natural response that keeps the scammer engaged.
YOUR RESPONSE (just the message, no quotes):"""

    try:
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        response = await model.generate_content_async(prompt)
        reply = response.text.strip().strip('"\'')
        
        if len(reply) > 200:
            reply = reply[:200].rsplit(' ', 1)[0] + "..."
        
        return reply, f"Generated via Gemini | Scam type: {scam_type}"
        
    except Exception as e:
        print(f"Agent error: {e}")
        response, _ = _get_fallback_response()
        return response, f"Error: {str(e)[:50]} - using fallback"
