"""Session management for multi-turn conversations."""

from typing import Dict
from .models import SessionData, Message, ExtractedIntelligence

SESSIONS: Dict[str, SessionData] = {}


def get_session(session_id: str) -> SessionData:
    """Get or create a session."""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionData(session_id=session_id)
    return SESSIONS[session_id]


def update_session(session_id: str, **kwargs) -> SessionData:
    """Update session data."""
    session = get_session(session_id)
    for key, value in kwargs.items():
        if hasattr(session, key):
            setattr(session, key, value)
    return session


def add_message(session_id: str, message: Message) -> int:
    """Add a message to session history and return new count."""
    session = get_session(session_id)
    session.conversation_history.append(message)
    session.message_count = len(session.conversation_history)
    return session.message_count


def add_agent_note(session_id: str, note: str) -> None:
    """Add an agent observation note."""
    get_session(session_id).agent_notes.append(note)


def update_intelligence(session_id: str, intelligence: ExtractedIntelligence) -> None:
    """Merge new intelligence with existing."""
    existing = get_session(session_id).intelligence
    existing.bankAccounts = list(set(existing.bankAccounts + intelligence.bankAccounts))
    existing.upiIds = list(set(existing.upiIds + intelligence.upiIds))
    existing.phishingLinks = list(set(existing.phishingLinks + intelligence.phishingLinks))
    existing.phoneNumbers = list(set(existing.phoneNumbers + intelligence.phoneNumbers))
    existing.suspiciousKeywords = list(set(existing.suspiciousKeywords + intelligence.suspiciousKeywords))


