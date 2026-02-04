"""AI Agent for engaging scammers with human-like responses."""

import random
from typing import List, Optional
import google.generativeai as genai
from .config import LLM_PROVIDER, GEMINI_API_KEY, OPENAI_API_KEY
from .models import Message


class HoneypotAgent:
    """AI Agent that engages scammers believably."""
    
    # Persona templates
    PERSONAS = [
        {
            "name": "confused_elderly",
            "description": "An elderly person who is not tech-savvy, easily confused, but trying to be helpful",
            "traits": ["asks for clarification often", "mentions grandchildren", "slow to understand", "trusting"]
        },
        {
            "name": "naive_user", 
            "description": "A young person who is new to online banking, eager to solve problems",
            "traits": ["asks basic questions", "worried about account", "willing to follow instructions", "slightly nervous"]
        },
        {
            "name": "busy_professional",
            "description": "A busy professional who wants quick solutions but is cautious",
            "traits": ["asks for credentials", "wants to verify caller", "limited time", "suspicious but compliant"]
        }
    ]
    
    # Response strategies to extend engagement
    ENGAGEMENT_TACTICS = [
        "ask_clarification",      # "I don't understand, can you explain?"
        "express_concern",        # "Oh no! Is my money safe?"
        "delay_tactic",           # "Let me find my reading glasses..."
        "verify_identity",        # "How do I know you're really from the bank?"
        "request_details",        # "What account are you talking about?"
        "show_compliance",        # "Okay, what do I need to do?"
        "technical_confusion",    # "I don't know how to do that on my phone"
    ]
    
    def __init__(self):
        self._setup_llm()
        self.current_persona = random.choice(self.PERSONAS)
    
    def _setup_llm(self):
        """Initialize LLM for response generation."""
        if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.llm_available = True
        else:
            self.llm_available = False
    
    def _select_tactic(self, message_count: int, scam_type: str) -> str:
        """Select engagement tactic based on conversation progress."""
        if message_count <= 2:
            # Early: confusion and clarification
            return random.choice(["ask_clarification", "express_concern", "request_details"])
        elif message_count <= 5:
            # Mid: verification and delays
            return random.choice(["verify_identity", "delay_tactic", "technical_confusion"])
        else:
            # Late: show compliance to extract more info
            return random.choice(["show_compliance", "request_details", "technical_confusion"])
    
    def _build_prompt(self, scammer_message: str, history: List[Message], 
                      scam_type: str, tactic: str) -> str:
        """Build prompt for LLM response generation."""
        persona = self.current_persona
        
        # Build conversation context
        context = ""
        if history:
            recent = history[-6:]  # Last 6 messages for context
            context = "\n".join([f"{'Caller' if m.sender == 'scammer' else 'You'}: {m.text}" 
                                for m in recent])
        
        prompt = f"""You are role-playing as a potential scam victim to keep the scammer engaged and extract information.

YOUR PERSONA:
- Role: {persona['description']}
- Traits: {', '.join(persona['traits'])}

CRITICAL RULES:
1. NEVER reveal you know this is a scam
2. Be believable as a real human - use natural language, hesitation, typos occasionally
3. Keep responses SHORT (1-2 sentences, max 50 words)
4. Your goal: Keep them talking to extract phone numbers, links, account details, UPI IDs
5. Strategy for this response: {tactic}

SCAM TYPE DETECTED: {scam_type}

{"PREVIOUS CONVERSATION:" + chr(10) + context if context else ""}

SCAMMER'S LATEST MESSAGE: "{scammer_message}"

Generate a single, natural response that:
- Matches your persona
- Uses the {tactic} strategy
- Keeps the scammer engaged
- Sounds like a real confused/naive person

YOUR RESPONSE (just the message, no quotes or labels):"""

        return prompt
    
    async def generate_response(self, scammer_message: str, history: List[Message],
                                scam_type: str, message_count: int) -> tuple[str, str]:
        """
        Generate a human-like response to engage the scammer.
        
        Returns:
            Tuple of (response_text, agent_note)
        """
        tactic = self._select_tactic(message_count, scam_type)
        
        if not self.llm_available:
            # Fallback responses if LLM not available
            return self._get_fallback_response(tactic), f"Used fallback: {tactic}"
        
        prompt = self._build_prompt(scammer_message, history, scam_type, tactic)
        
        try:
            if LLM_PROVIDER == "gemini":
                response = await self.model.generate_content_async(prompt)
                reply = response.text.strip()
            else:
                # OpenAI fallback
                import openai
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100
                )
                reply = response.choices[0].message.content.strip()
            
            # Clean up response
            reply = reply.strip('"\'')
            if len(reply) > 200:
                reply = reply[:200].rsplit(' ', 1)[0] + "..."
            
            agent_note = f"Tactic: {tactic} | Persona: {self.current_persona['name']}"
            return reply, agent_note
            
        except Exception as e:
            print(f"Agent response error: {e}")
            return self._get_fallback_response(tactic), f"Fallback due to error: {str(e)[:50]}"
    
    def _get_fallback_response(self, tactic: str) -> str:
        """Fallback responses when LLM is unavailable."""
        fallbacks = {
            "ask_clarification": [
                "I don't understand, what do you mean?",
                "Can you explain that again please?",
                "What should I do exactly?",
            ],
            "express_concern": [
                "Oh no! Is my account really blocked?",
                "This is worrying me, what happened?",
                "I'm scared, please help me fix this!",
            ],
            "delay_tactic": [
                "Wait, let me put on my glasses...",
                "Hold on, I need to find my phone...",
                "Just a moment, someone's at the door...",
            ],
            "verify_identity": [
                "But how do I know you're really from the bank?",
                "Can you tell me what bank this is about?",
                "What's your employee ID?",
            ],
            "request_details": [
                "Which account are you talking about?",
                "What's the account number you see?",
                "Can you tell me the last transaction?",
            ],
            "show_compliance": [
                "Okay, tell me what I need to do.",
                "I'll do whatever you say, just help me.",
                "What information do you need from me?",
            ],
            "technical_confusion": [
                "I don't know how to do that on my phone...",
                "Where do I find that in my app?",
                "My son usually helps me with this stuff...",
            ],
        }
        
        responses = fallbacks.get(tactic, fallbacks["ask_clarification"])
        return random.choice(responses)
    
    def switch_persona(self):
        """Switch to a different persona (for variety in long conversations)."""
        available = [p for p in self.PERSONAS if p != self.current_persona]
        if available:
            self.current_persona = random.choice(available)


# Global instance
honeypot_agent = HoneypotAgent()
