"""Pydantic models for request/response validation."""

from typing import List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    """Individual message structure."""
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Union[int, str] = Field(..., description="Epoch timestamp (ms) or ISO-8601 string")


class Metadata(BaseModel):
    """Message metadata."""
    channel: Optional[str] = Field("SMS", description="Communication channel")
    language: Optional[str] = Field("English", description="Language used")
    locale: Optional[str] = Field("IN", description="Country/region")


class HoneypotRequest(BaseModel):
    """Incoming API request structure."""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: Optional[List[Message]] = Field(
        default_factory=list, 
        description="Previous messages in conversation"
    )
    metadata: Optional[Metadata] = Field(
        default_factory=Metadata, 
        description="Message metadata"
    )


class HoneypotResponse(BaseModel):
    """API response structure."""
    status: str = Field(..., description="Response status: 'success' or 'error'")
    reply: str = Field(..., description="Agent's response message")


class ExtractedIntelligence(BaseModel):
    """Extracted intelligence data structure."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class GuviCallbackPayload(BaseModel):
    """GUVI callback payload structure."""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


class SessionData(BaseModel):
    """Session state tracking."""
    session_id: str
    message_count: int = 0
    scam_detected: bool = False
    scam_type: Optional[str] = None
    confidence: float = 0.0
    intelligence: ExtractedIntelligence = Field(default_factory=ExtractedIntelligence)
    conversation_history: List[Message] = Field(default_factory=list)
    callback_sent: bool = False
    agent_notes: List[str] = Field(default_factory=list)
