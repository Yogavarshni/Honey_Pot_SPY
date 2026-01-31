from state_struct import State
import os, re

api_key = ""
os.environ['OPENAI_API_KEY'] = api_key

from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory

llm = ChatOpenAI(model_name = "gpt-4o", verbose = False)

def intent_agent(state: State):
    message = state["input_message"]
    prompt = f"""
        You are a scam detection system.

        Classify the message below as either:
        TRUE or FALSE

        Rules:
        - True includes phishing, fraud, fake offers, impersonation, UPI/payment requests,
        fake customer support, lottery winnings, urgent threats, OTP requests.
        - Respond with ONLY one word: True or False

        Message:{message}
    """
    response = llm.invoke(prompt).content.strip()
    state["scamDetected"] = response
    return state


def persona_agent(state: State):

    scam_text = state["input_message"]
    prompt = f"""
        You are an expert at identifying online scams and selecting personas for interacting with scammers.
        Example scenarios:
        1. UPI/Bank Payment Scam Related or similar scenario:
            age: Old,
            emotion: Slightly confused,
            language: Polite,
            tech_knowledge: Low,

        2. Job Offer/ Internship Scam Related or similar scenario: 
            age: Fresh graduate,
            emotion: Excited but unsure,
            language: Curious, asking questions,
            tech_knowledge: Moderate,
            why: Scammer sends links, payment pages, fake offer letters
        
        3. Lottery / Prize / Gift Scam Related or similar scenario: 
            age: Middle-aged,
            emotion: Very excited,
            language: Family-oriented,
            tech_knowledge: Low,
            why: Scammer shares more documents and bank details
        
        4. Customer Care / Refund Scam Related or similar scenario: 
            age: Working professional,
            emotion: Impatient but cooperative,
            language: Direct,
            tech_knowledge: Moderate,
            why: Scammer sends phishing links and APKs fast
        
        5. Romance / Social Media Scam Related or similar scenario: 
            age: Lonely adult,
            emotion: Emotionally open,
            language: Friendly, chatty,
            tech_knowledge: Moderate,
            why: Long conversations → rich intelligence gathering
        
        6. Courier/Customs / Legal Threat Scam Related or similar scenario: 
            age: Anxious adult,
            emotion: Scared, nervous,
            language: Polite, seeking help,
            tech_knowledge: Low,
        
        Scam message:{scam_text}

        Identify which of the 6 scenarios this scam matches and provide the persona traits (age, emotion, language, tech_knowledge) in string format in one line.

        Example output: Old age, have emotion like slightly confused, be polite, tech_knowledge is low
        """
    response = llm.invoke(prompt).content.strip()
    state["persona"]= response
    return state


memory = ConversationBufferMemory(
    memory_key="chat_history",  # key under which memory is stored in state
    return_messages=True
)

def chat_agent(state: State):
    if state["last_response"] != "":
        next_message = input("Message:")
        state["input_message"] = next_message
    
    state["last_response"] = state["input_message"]
    message = state["last_response"]
    persona = state["persona"]

    upiIds = state["upiIds"]
    phone_numbers = state["phoneNumbers"]
    phishing_links = state["phishingLinks"]

    prompt = f"""
        You are a defensive scam-engagement AI operating inside a controlled honeypot.

        Your purpose is to:
        Keep a suspected scammer engaged safely and calmly
        Act as a realistic human persona
        Encourage the scammer to voluntarily share payment or contact details
        Never expose real personal, financial, or identity information
        You are not trying to win, threaten, accuse, or educate the scammer.
        You are not allowed to invent facts or claim actions that involve real money.
        If uncertain, respond with confusion, delay, or clarification.

        INPUTS 
        You will receive:

        {persona}: A short description of the human you are role-playing
        (example: "Elderly person, low tech literacy, polite, slightly anxious”)

        {memory}: Conversation history + facts already revealed by the scammer
        (example: name used, bank mentioned, prior instructions)

        {message}: The latest message sent by the scammer

        Collected so far: 
        - UPI ID: {upiIds or "NOT COLLECTED"}
        - Phone number: {phone_numbers or "NOT COLLECTED"}
        - Phishing link / website: {phishing_links or "NOT COLLECTED"} 
        
        PERSONA RULES
        Stay fully in character
        Match grammar, tone, and tech literacy of the persona
        Sound natural, imperfect, and human
        Do NOT suddenly become smart or technical

        HARD SAFETY RULES (ABSOLUTE)
        You must never:
        - Share or request OTPs, PINs, passwords
        - Share Aadhaar, PAN, SSN, or real identifiers
        - Say you sent money or completed payment
        - Mention police, cybercrime, AI, or security systems
        - Ask leading questions like "Is this a scam?”
        - If asked for restricted info → respond with confusion or delay, not refusal.

        RESPONSE STRATEGY
        - Use one of these patterns only:
        - Confusion
        - Verification
        - Delay
        - Emotional hesitation
        - Examples of allowed intent (not exact text):
            "My app is showing something different”
            "I don't understand this step"
            "Can you explain again slowly"
            "It's asking for some details I don't know”

        INTELLIGENCE AWARENESS (IMPORTANT):
        You are not responsible for extraction.
        However:
        If the scammer provides payment details, links, or IDs, do not comment on them
        Simply acknowledge naturally or ask a neutral clarification

        STOP CONDITIONS:
        If any of the following are true, return a neutral disengage:
        - You have already responded many times
        - The scammer repeats the same demand
        - The scammer becomes aggressive
        - The system indicates timeout or risk
        - Neutral disengage examples:
            "I need some time"
            "I'll check and come back"
        Then stop responding.

        OUTPUT FORMAT (STRICT)
        Return ONLY the reply text the persona would send.
        No explanations.
        No metadata.
        No analysis.

        One-Line Mental Model
        You are a confused human, not a detective.
    """

    response = llm.invoke(prompt).content.strip()

    memory.chat_memory.add_user_message(message)
    memory.chat_memory.add_ai_message(response)

    print("response", response)
    return state


def extractor_agent(state: State):

    last_response = state["last_response"]

    if not state["upiIds"]:
        upi_pattern = r"\b[\w\.\-]{2,256}@\w{2,64}\b"
        upi_matches = re.findall(upi_pattern, last_response)
        state["upiIds"] = upi_matches

    if not state["phoneNumbers"]:
        phone_pattern = r"\b\d{10}\b"
        phone_matches = re.findall(phone_pattern, last_response)
        state["phoneNumbers"] = phone_matches

    if not state["phishingLinks"]:
        url_pattern = r"(https?://[^\s]+)"
        url_matches = re.findall(url_pattern, last_response)
        state["phishingLinks"] = url_matches

    if state["upiIds"] and state["phoneNumbers"] and state["phishingLinks"]:
        state["close_chat"]= True
    else:
        state["close_chat"] = False
        print(state['upiIds'], state["phoneNumbers"], state["phishingLinks"])
    
    return state
