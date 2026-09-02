from typing import List, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Union[int, str] = Field(..., description="Epoch timestamp (ms) or ISO-8601 string")


class HoneypotRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: Optional[List[Message]] = Field(
        default_factory=list, 
        description="Previous messages in conversation"
    )
    metadata: Optional[dict] = Field(
        default=None, 
        description="Message metadata"
    )


class HoneypotResponse(BaseModel):
    status: str = Field(..., description="Response status: 'success' or 'error'")
    reply: str = Field(..., description="Agent's response message")


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)
    ifscCodes: List[str] = Field(default_factory=list)
    names: List[str] = Field(default_factory=list)
    addresses: List[str] = Field(default_factory=list)


class SessionData(BaseModel):
    session_id: str
    message_count: int = 0
    scam_detected: bool = False
    scam_type: Optional[str] = None
    confidence: float = 0.0
    intelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)
    conversation_history: List[Message] = Field(default_factory=list)
    callback_sent: bool = False
    agent_notes: List[str] = Field(default_factory=list)
