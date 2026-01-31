from typing import TypedDict, Dict, Any
import pandas as pd

class State(TypedDict, total = False):
    input_message: str
    scamDetected: bool
    persona: str
    upiIds: str
    phishingLinks: str
    phoneNumbers: str
    last_response: str
    close_chat: bool  
    final_payload: Dict[str, Any]
    
