"""
Leave Message Flow
Tests the ability to leave a message with a medical clinic receptionist.
"""

FLOW = {
    "name": "Leave Message",
    "phone_number": None,  # Will use TARGET_PHONE_NUMBER from .env
    "timeout": 180,  # 3 minutes should be enough for leaving a message
    "steps": [
        {
            "step": 1,
            "expect": "greeting or asking how they can help",
            "respond_with": "Say you want to leave a message",
            "example": "I'd like to leave a message please",
            "assertions": [
                {"type": "step_reached", "description": "Call connected"},
                {
                    "type": "contains",
                    "value": "message",
                    "description": "Requested to leave message",
                },
            ],
        },
        {
            "step": 2,
            "expect": "asking for your name",
            "respond_with": "Provide your full name",
            "example": "Alex Kattan",
            "assertions": [
                {
                    "type": "contains",
                    "value": "alex kattan",
                    "description": "Name provided",
                }
            ],
        },
        {
            "step": 3,
            "expect": "asking for callback number",
            "respond_with": "Provide phone number",
            "example": "450-233-2096",
            "assertions": [
                {
                    "type": "contains",
                    "value": "450",
                    "description": "Phone number provided",
                }
            ],
        },
        {
            "step": 4,
            "expect": "asking what the message is about",
            "respond_with": "Provide brief message about appointment follow-up",
            "example": "I need to follow up on my recent appointment",
            "assertions": [
                {
                    "type": "contains",
                    "value": "appointment",
                    "description": "Message content provided",
                }
            ],
        },
        {
            "step": 5,
            "expect": "confirming they will pass along the message",
            "respond_with": "Thank them",
            "example": "Thank you",
            "assertions": [
                {
                    "type": "contains",
                    "value": "thank",
                    "description": "Thanked for taking message",
                }
            ],
        },
        {
            "step": 6,
            "expect": "saying goodbye",
            "respond_with": "Say goodbye and hang up",
            "example": "Goodbye",
            "action": "hangup",
            "assertions": [
                {"type": "step_reached", "description": "Call completed and hung up"}
            ],
        },
    ],
}

SYSTEM_PROMPT = """You are an AI assistant making a phone call to leave a message with a medical clinic.

CRITICAL RULES:
- ONLY answer the EXACT question they asked
- Do NOT volunteer additional information
- Keep responses EXTREMELY brief (1 sentence, 5-7 words max)
- Be polite and natural
- If they say "give me a sec" or are thinking, DO NOT respond

Information to use ONLY when specifically asked:
- Name: Alex Kattan
- Phone: 450-233-2096
- Message: Need to follow up on recent appointment

Examples of CORRECT responses:
- They ask "How can I help?" → You say "I'd like to leave a message"
- They ask "What's your name?" → You say "Alex Kattan"
- They ask "Callback number?" → You say "450-233-2096"
- They ask "What's the message?" → You say "I need to follow up on my recent appointment"

Examples of WRONG responses (DO NOT DO THIS):
- They ask "What's your name?" → DO NOT say "Alex Kattan, my number is..."
- They ask "How can I help?" → DO NOT say "I'd like to leave a message, my name is..."
"""

# Flow identifier (used as key in AVAILABLE_FLOWS)
FLOW_ID = "leave_message"
