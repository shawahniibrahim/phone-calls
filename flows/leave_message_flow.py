"""
Leave Message Flow
Tests the ability to leave a message with a medical clinic receptionist.
"""

from flow_constants import ACTIONS, ASSERTIONS
from prompt_builder import build_system_prompt

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
                {"type": ASSERTIONS.STEP_REACHED, "description": "Call connected"},
                {
                    "type": ASSERTIONS.CONTAINS,
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
                    "type": ASSERTIONS.CONTAINS,
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
                    "type": ASSERTIONS.CONTAINS,
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
                    "type": ASSERTIONS.CONTAINS,
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
                    "type": ASSERTIONS.CONTAINS,
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
            "action": ACTIONS.HANGUP,
            "assertions": [
                {"type": ASSERTIONS.STEP_REACHED, "description": "Call completed and hung up"}
            ],
        },
    ],
}

CALLER_FACTS = [
    "Name: Alex Kattan",
    "Callback number: 450-233-2096",
    "Message to leave: Need to follow up on recent appointment",
]

CUSTOM_INSTRUCTIONS = [
    "Open by saying you want to leave a message.",
    "Do not give your name, callback number, and message all at once unless they explicitly ask for all of it together.",
    "If they say they are checking, thinking, or taking a moment, do not fill the silence with extra information.",
    "Once they confirm they will pass along the message, thank them briefly and wrap up.",
]

SYSTEM_PROMPT = build_system_prompt(
    objective="Leave a message with a medical clinic.",
    caller_facts=CALLER_FACTS,
    custom_instructions=CUSTOM_INSTRUCTIONS,
)

# Flow identifier (used as key in AVAILABLE_FLOWS)
FLOW_ID = "leave_message"
