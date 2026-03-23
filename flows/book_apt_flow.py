"""
Book Appointment Flow
Tests the ability to book a new medical appointment.
"""

from prompt_builder import build_system_prompt

FLOW = {
    "name": "Book Appointment",
    "phone_number": None,  # Will use TARGET_PHONE_NUMBER from .env
    "timeout": 300,  # 5 minutes for booking process
    "steps": [
        {
            "step": 1,
            "expect": "greeting or asking how they can help",
            "respond_with": "Say you want to book an appointment",
            "example": "I'd like to book an appointment",
            "assertions": [
                {"type": "step_reached", "description": "Call connected"},
                {
                    "type": "contains",
                    "value": "appointment",
                    "description": "Mentioned appointment",
                },
            ],
        },
        {
            "step": 2,
            "expect": "asking for your name",
            "respond_with": "Provide your full name",
            "example": "John Smith",
            "assertions": [
                {
                    "type": "contains",
                    "value": "john smith",
                    "description": "Name provided",
                }
            ],
        },
        {
            "step": 3,
            "expect": "asking for date of birth",
            "respond_with": "Provide date of birth",
            "example": "January 15, 1990",
            "assertions": [
                {
                    "type": "contains",
                    "value": "january 15",
                    "description": "DOB provided",
                }
            ],
        },
        {
            "step": 4,
            "expect": "asking for preferred date or time",
            "respond_with": "Provide preferred time",
            "example": "Next Monday afternoon",
            "assertions": [
                {
                    "type": "contains",
                    "value": "monday",
                    "description": "Time preference provided",
                }
            ],
        },
        {
            "step": 5,
            "expect": "confirming the appointment",
            "respond_with": "Confirm the appointment",
            "example": "Yes, that works for me",
            "assertions": [
                {
                    "type": "contains",
                    "value": "yes",
                    "description": "Appointment confirmed",
                }
            ],
        },
        {
            "step": 6,
            "expect": "saying goodbye",
            "respond_with": "Thank them and say goodbye",
            "example": "Thank you, goodbye",
            "action": "hangup",
            "assertions": [{"type": "step_reached", "description": "Call completed"}],
        },
    ],
}

CALLER_FACTS = [
    "Name: John Smith",
    "Date of birth: January 15, 1990",
    "Phone: 555-1234",
    "Preferred time: Next Monday afternoon",
    "Reason for visit if asked: Regular checkup",
]

CUSTOM_INSTRUCTIONS = [
    "Open by saying you want to book an appointment.",
    "Provide one piece of information at a time instead of bundling name, date of birth, and timing together.",
    "If they ask when you want to come in, say Next Monday afternoon.",
    "If they offer a suitable appointment, confirm it briefly and politely.",
]

SYSTEM_PROMPT = build_system_prompt(
    objective="Book a medical appointment.",
    caller_facts=CALLER_FACTS,
    custom_instructions=CUSTOM_INSTRUCTIONS,
)

# Flow identifier (used as key in AVAILABLE_FLOWS)
FLOW_ID = "book_appointment"
