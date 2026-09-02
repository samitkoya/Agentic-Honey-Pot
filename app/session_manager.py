import os
from typing import Dict
from .models import SessionData, Message, ExtractedIntelligence

SESSIONS: Dict[str, SessionData] = {}


def get_session(session_id: str) -> SessionData:
    if session_id not in SESSIONS:
        SESSIONS[session_id] = SessionData(session_id=session_id)
    return SESSIONS[session_id]


def update_session(session_id: str, **kwargs) -> SessionData:
    session = get_session(session_id)
    for key, value in kwargs.items():
        if hasattr(session, key):
            setattr(session, key, value)
    return session


def add_message(session_id: str, message: Message) -> int:
    session = get_session(session_id)
    session.conversation_history.append(message)
    session.message_count = len(session.conversation_history)
    return session.message_count


def add_agent_note(session_id: str, note: str) -> None:
    get_session(session_id).agent_notes.append(note)


def update_intelligence(session_id: str, intelligence: ExtractedIntelligence) -> None:
    existing = get_session(session_id).intelligence
    existing.bankAccounts = list(set(existing.bankAccounts + intelligence.bankAccounts))
    existing.upiIds = list(set(existing.upiIds + intelligence.upiIds))
    existing.phishingLinks = list(set(existing.phishingLinks + intelligence.phishingLinks))
    existing.phoneNumbers = list(set(existing.phoneNumbers + intelligence.phoneNumbers))
    existing.suspiciousKeywords = list(set(existing.suspiciousKeywords + intelligence.suspiciousKeywords))
    existing.ifscCodes = list(set(existing.ifscCodes + intelligence.ifscCodes))
    existing.names = list(set(existing.names + intelligence.names))
    existing.addresses = list(set(existing.addresses + intelligence.addresses))
    save_intelligence_to_file(session_id)


def save_intelligence_to_file(session_id: str, output_dir: str = "intelligence_logs") -> str:
    session = get_session(session_id)
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, f"extracted_intelligence_{session_id}.txt")
    intel = session.intelligence
    
    lines = [
        "==================================================",
        "          AGENTIC HONEY-POT REPORT                ",
        "==================================================",
        f"Session ID     : {session.session_id}",
        f"Scam Detected  : {session.scam_detected}",
        f"Scam Type      : {session.scam_type or 'N/A'}",
        f"Confidence     : {session.confidence:.2f}",
        f"Message Count  : {session.message_count}",
        "--------------------------------------------------",
        "EXTRACTED THREAT INTELLIGENCE:",
        f"  - Bank Accounts      : {', '.join(intel.bankAccounts) if intel.bankAccounts else 'None'}",
        f"  - IFSC Codes         : {', '.join(intel.ifscCodes) if intel.ifscCodes else 'None'}",
        f"  - UPI IDs            : {', '.join(intel.upiIds) if intel.upiIds else 'None'}",
        f"  - Phishing Links     : {', '.join(intel.phishingLinks) if intel.phishingLinks else 'None'}",
        f"  - Phone Numbers      : {', '.join(intel.phoneNumbers) if intel.phoneNumbers else 'None'}",
        f"  - Names              : {', '.join(intel.names) if intel.names else 'None'}",
        f"  - Addresses          : {', '.join(intel.addresses) if intel.addresses else 'None'}",
        f"  - Suspicious Keywords: {', '.join(intel.suspiciousKeywords) if intel.suspiciousKeywords else 'None'}",
        "--------------------------------------------------",
        "CONVERSATION HISTORY:"
    ]
    
    for msg in session.conversation_history:
        lines.append(f"  [{msg.sender.upper()}]: {msg.text}")
        
    lines.append("--------------------------------------------------")
    lines.append("AGENT NOTES:")
    for note in session.agent_notes:
        lines.append(f"  - {note}")
    lines.append("==================================================\n")
    
    content = "\n".join(lines)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    root_filepath = os.path.join(output_dir, "collected_intelligence.txt")
    with open(root_filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
