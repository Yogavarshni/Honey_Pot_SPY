from langgraph.graph import StateGraph, END
from state_struct import State
from utils import *
import json

def build_honey_pot():
    builder = StateGraph(State)  
 
    builder.add_node("Intent_Agent", intent_agent)
    builder.add_node("Persona_Agent", persona_agent)
    builder.add_node("Chat_Agent", chat_agent)
    builder.add_node("Extractor_Agent", extractor_agent)
 
    def route_from_intent(state: State):
        if state["scamDetected"]:
            return "scam"
        return "not_scam"

    def route_from_extractor(state: State):
        if state["close_chat"]:
            return "close"
        return "continue"

    builder.set_entry_point("Intent_Agent")
    builder.add_conditional_edges(
        "Intent_Agent",
        route_from_intent,{"scam": "Persona_Agent","not_scam": END}
    )
    builder.add_edge("Persona_Agent", "Chat_Agent")
    builder.add_edge("Chat_Agent", "Extractor_Agent")
    builder.add_conditional_edges(
        "Extractor_Agent", 
        route_from_extractor,{"continue": "Chat_Agent","close": END}
    )
 
    graph = builder.compile()
 
    state: State = {
        "input_message": "",
        "scamDetected": False,
        "persona": "",
        "upiIds": "",
        "phishingLinks": "",
        "phoneNumbers": "",
        "last_response": "",
        "close_chat": False,
    }
 
    return graph, state
 

input_message = input("Message")
if input_message:
    graph, state = build_honey_pot()
    state['input_message'] = input_message
    result = graph.invoke(state)
    payload = {
        "upiIds":result["upiIds"],
        "phoneNumbers": result["phoneNumbers"],
        "phishingLinks": result["phishingLinks"]
    }
    print(json.dumps(payload, indent=2))

