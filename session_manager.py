"""Session management for multi-turn conversations."""

from typing import Dict, Optional
from models import SessionData, Message, ExtractedIntelligence


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
    
    def mark_callback_sent(self, session_id: str) -> None:
        """Mark that GUVI callback has been sent."""
        session = self.get_session(session_id)
        session.callback_sent = True
    
    def is_callback_sent(self, session_id: str) -> bool:
        """Check if callback was already sent."""
        session = self.get_session(session_id)
        return session.callback_sent
    
    def get_message_count(self, session_id: str) -> int:
        """Get total messages exchanged."""
        return self.get_session(session_id).message_count
    
    def delete_session(self, session_id: str) -> bool:
        """Remove a session (cleanup)."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def get_agent_notes_summary(self, session_id: str) -> str:
        """Get combined agent notes as a summary."""
        session = self.get_session(session_id)
        if session.agent_notes:
            return " | ".join(session.agent_notes)
        return "No specific notes recorded."


# Global session manager instance
session_manager = SessionManager()
