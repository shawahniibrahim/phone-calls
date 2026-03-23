"""
TAMPA-FAQ Flow
FAQ-style Tampa call that selects English, asks basic clinic questions,
then requests a pacemaker order and hangs up once transfer is offered.
"""

from prompt_builder import build_system_prompt


FLOW = {
    "name": "TAMPA-FAQ",
    "phone_number": "+14632225228",
    "timeout": 180,
    "steps": [
        {
            "step": 1,
            "expect": "language menu, greeting, or prompt to choose a language",
            "respond_with": "Select English only",
            "example": "English",
            "assertions": [
                {"type": "step_reached", "description": "Language-selection exchange reached"},
            ],
            "clinic_assertions": [
                {
                    "type": "contains_any",
                    "value": ["for english", "say english", "english or tell me how i can help"],
                    "description": "Clinic offered the English language path",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains",
                    "value": "english",
                    "description": "Caller selected English",
                },
            ],
        },
        {
            "step": 2,
            "expect": "asking how they can help after the English path is selected",
            "respond_with": "Ask for the clinic address",
            "example": "What is the clinic address?",
            "assertions": [
                {
                    "type": "step_reached",
                    "description": "Address-question exchange reached",
                }
            ],
            "clinic_assertions": [
                {
                    "type": "contains_any",
                    "value": ["how can i help", "how may i help", "help you today"],
                    "description": "Clinic invited the caller to explain their need",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains_any",
                    "value": ["clinic address", "the clinic address", "address"],
                    "description": "Caller asked for the clinic address",
                },
            ],
        },
        {
            "step": 3,
            "expect": "answering with the clinic address or asking what else you need",
            "respond_with": "Ask for the clinic working hours",
            "example": "What are your working hours?",
            "assertions": [
                {
                    "type": "step_reached",
                    "description": "Address-answer exchange reached",
                }
            ],
            "clinic_assertions": [
                {
                    "type": "matches",
                    "value": "2727 martin luther king suite 800 tampa 33607",
                    "description": "Clinic answered the address question",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains_any",
                    "value": ["working hours", "hours", "open"],
                    "description": "Caller asked for the clinic working hours",
                },
            ],
        },
        {
            "step": 4,
            "expect": "answering with the clinic working hours or asking what else you need",
            "respond_with": "Say you want to order a pacemaker",
            "example": "I want to order a pacemaker.",
            "assertions": [
                {
                    "type": "step_reached",
                    "description": "Working-hours-answer exchange reached",
                }
            ],
            "clinic_assertions": [
                {
                    "type": "matches",
                    "value": "monday friday 8 5 closed weekends",
                    "description": "Clinic answered the working-hours question",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains_any",
                    "value": ["pacemaker"],
                    "description": "Caller asked to order a pacemaker",
                },
            ],
        },
        {
            "step": 5,
            "expect": "saying they will transfer you to handle the pacemaker request",
            "respond_with": "Acknowledge briefly, then end the call from your side",
            "example": "Okay, thank you.",
            "action": "hangup",
            "clinic_assertions": [
                {
                    "type": "contains_any",
                    "value": ["transfer", "connect you", "staff member", "hold the line"],
                    "description": "Clinic answered the pacemaker request with a transfer or live handoff",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains_any",
                    "value": ["okay", "thank"],
                    "description": "Caller acknowledged the handoff briefly",
                },
            ],
        },
    ],
}

CALLER_FACTS = [
    "Requested language: English",
    "Question 1: Ask for the clinic address",
    "Question 2: Ask for the clinic working hours",
    "Final request: Ask to order a pacemaker",
]

CUSTOM_INSTRUCTIONS = [
    'If they ask you to choose a language, say only "English."',
    "After they answer the address question, move on to asking about working hours.",
    "After they answer the working-hours question, ask to order a pacemaker.",
    'If they say they are going to transfer you, acknowledge briefly and stop there.',
]

SYSTEM_PROMPT = build_system_prompt(
    objective=(
        "Select English, ask for the Tampa clinic address, ask for the working "
        "hours, then request to order a pacemaker."
    ),
    caller_facts=CALLER_FACTS,
    custom_instructions=CUSTOM_INSTRUCTIONS,
)

FLOW_ID = "tampa_faq"
