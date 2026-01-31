from typing import TypedDict, Dict, Any
import pandas as pd

class State(TypedDict, total = False):
    input_message: str
    scamDetected: bool
    persona: str
    session_id: str
    totalMessagesExchanged: int
    upiIds: str
    phishingLinks: str
    phoneNumbers: str
    bankAccounts: str
    suspiciousKeywords: Dict[str, Any]
    agentNotes: str
    last_response: str
    close_chat: bool  