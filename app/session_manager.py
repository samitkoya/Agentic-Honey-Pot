"""Session management for multi-turn conversations."""

from typing import Dict, Optional
from .models import SessionData, Message, ExtractedIntelligence


class SessionManager:
    """Manages conversation sessions in memory."""
    
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
    
    def get_session(self, session_id: str) -> SessionData:
        """Get or create a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionData(session_id=session_id)
        return self._sessions[session_id]
    
    def update_session(self, session_id: str, **kwargs) -> SessionData:
        """Update session data."""
        session = self.get_session(session_id)
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        return session
    
    def add_message(self, session_id: str, message: Message) -> int:
        """Add a message to session history and return new count."""
        session = self.get_session(session_id)
        session.conversation_history.append(message)
        session.message_count = len(session.conversation_history)
        return session.message_count
    
    def add_agent_note(self, session_id: str, note: str) -> None:
        """Add an agent observation note."""
        session = self.get_session(session_id)
        session.agent_notes.append(note)
    
    def update_intelligence(self, session_id: str, intelligence: ExtractedIntelligence) -> None:
        """Merge new intelligence with existing."""
        session = self.get_session(session_id)
        existing = session.intelligence
        
        # Merge lists without duplicates
        existing.bankAccounts = list(set(existing.bankAccounts + intelligence.bankAccounts))
        existing.upiIds = list(set(existing.upiIds + intelligence.upiIds))
        existing.phishingLinks = list(set(existing.phishingLinks + intelligence.phishingLinks))
        existing.phoneNumbers = list(set(existing.phoneNumbers + intelligence.phoneNumbers))
        existing.suspiciousKeywords = list(set(existing.suspiciousKeywords + intelligence.suspiciousKeywords))
    

# Global session manager instance
session_manager = SessionManager()

