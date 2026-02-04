"""GUVI evaluation callback handler."""

import httpx
from typing import Optional
from .models import GuviCallbackPayload, ExtractedIntelligence
from .config import GUVI_CALLBACK_URL


async def send_guvi_callback(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str
) -> tuple[bool, Optional[str]]:
    """
    Send final results to GUVI evaluation endpoint.
    
    Args:
        session_id: Unique session identifier
        scam_detected: Whether scam was confirmed
        total_messages: Total messages exchanged
        intelligence: Extracted intelligence data
        agent_notes: Summary of agent observations
    
    Returns:
        Tuple of (success, error_message)
    """
    payload = GuviCallbackPayload(
        sessionId=session_id,
        scamDetected=scam_detected,
        totalMessagesExchanged=total_messages,
        extractedIntelligence=intelligence,
        agentNotes=agent_notes
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                GUVI_CALLBACK_URL,
                json=payload.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in (200, 201):
                print(f"✓ GUVI callback sent successfully for session {session_id}")
                return True, None
            else:
                error_msg = f"GUVI callback failed: {response.status_code} - {response.text}"
                print(f"✗ {error_msg}")
                return False, error_msg
                
    except httpx.TimeoutException:
        error_msg = "GUVI callback timed out after 10 seconds"
        print(f"✗ {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"GUVI callback error: {str(e)}"
        print(f"✗ {error_msg}")
        return False, error_msg


async def send_callback_with_retry(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: str,
    max_retries: int = 3
) -> tuple[bool, Optional[str]]:
    """Send callback with retry logic."""
    last_error = None
    
    for attempt in range(max_retries):
        success, error = await send_guvi_callback(
            session_id, scam_detected, total_messages, intelligence, agent_notes
        )
        
        if success:
            return True, None
        
        last_error = error
        print(f"Retry {attempt + 1}/{max_retries} for session {session_id}")
    
    return False, last_error
