"""
TAMPA-MEDICATION-REFILL Flow
Medication refill workflow for the Tampa clinic.
"""

from flow_constants import ACTIONS, ASSERTIONS, ASSERT_ON, TARGETS
from prompt_builder import build_system_prompt


FLOW = {
    "name": "TAMPA-MEDICATION-REFILL",
    "phone_number": "+14632225228",
    "timeout": 240,
    "steps": [
        {
            "step": 1,
            "expect": "language menu, greeting, or prompt to choose a language",
            "respond_with": "Select English only",
            "example": "English",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Language-selection step reached",
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": [
                        "for english",
                        "say english",
                        "english or tell me how i can help",
                    ],
                    "description": "Clinic offered the English language path",
                    "target": TARGETS.CLINIC,
                },
                {
                    "type": ASSERTIONS.CONTAINS,
                    "value": "english",
                    "description": "Caller selected English",
                    "target": TARGETS.OURS,
                },
            ],
        },
        {
            "step": 2,
            "expect": "asking how they can help after the English path is selected",
            "respond_with": "Ask for a medication refill",
            "example": "I need to do a medication refill.",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Medication-refill request step reached",
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["how can i help", "how may i help", "help you today"],
                    "description": "Clinic invited the caller to explain their need",
                    "target": TARGETS.CLINIC,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["medication refill", "refill"],
                    "description": "Caller requested a medication refill",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": [
                        "calling from the following number",
                        "calling from",
                        "following number",
                        "use this number",
                        "best number",
                    ],
                    "description": "Clinic asked whether to use the caller's phone number",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        {
            "step": 3,
            "expect": "asking whether to use the phone number they see on the incoming call",
            "respond_with": "Say to use your phone number",
            "example": "Use 305 204 2944.",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Phone-number confirmation step reached",
                },
                {
                    "type": ASSERTIONS.MATCHES,
                    "value": "305 204 2944",
                    "description": "Caller provided the requested phone number",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["full name", "date of birth", "dob", "birth"],
                    "description": "Clinic moved on to identity verification",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        {
            "step": 4,
            "expect": "asking for full name and date of birth",
            "respond_with": "Provide full name and date of birth",
            "example": "Adam B. June second nineteen ninety six.",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Identity-verification step reached",
                },
                {
                    "type": ASSERTIONS.CONTAINS,
                    "value": "adam b",
                    "description": "Caller provided the full name",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["june", "1996"],
                    "description": "Caller provided the date of birth",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": [
                        "medication name",
                        "dosage",
                        "what medication",
                        "which medication",
                    ],
                    "description": "Clinic moved on to the medication details",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        {
            "step": 5,
            "expect": "asking for the medication name and dosage",
            "respond_with": "Provide the medication name, dosage, and pharmacy instruction all at once",
            "example": "Avastin 5 milligrams, use the same pharmacy on profile.",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Medication-details step reached",
                },
                {
                    "type": ASSERTIONS.MATCHES,
                    "value": "avastin 5mg same pharmacy profile",
                    "description": "Caller provided medication name, dosage, and pharmacy instruction",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": [
                        "anything else",
                        "is there anything else",
                        "let me confirm",
                        "confirming",
                    ],
                    "description": "Clinic acknowledged the refill request and checked whether anything else was needed",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        {
            "step": 6,
            "expect": "confirming the refill details or asking if anything else is needed",
            "respond_with": "Say that is correct and that is all",
            "example": "That's correct, this is it.",
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Final confirmation step reached",
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["that's correct", "thats correct", "this is it"],
                    "description": "Caller confirmed the refill details and said there was nothing else",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": [
                        "refill request",
                        "submitted",
                        "sent",
                        "successfully",
                        "pharmacy",
                        "doctor",
                    ],
                    "description": "Clinic gave a success-style refill confirmation message",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        {
            "step": 7,
            "expect": "giving the final success confirmation for the refill request",
            "respond_with": "Thank them and end the call",
            "example": "Thank you, goodbye.",
            "action": ACTIONS.HANGUP,
            "assertions": [
                {
                    "type": ASSERTIONS.STEP_REACHED,
                    "description": "Success-confirmation step reached",
                },
                {
                    "type": ASSERTIONS.CONTAINS_ANY,
                    "value": ["thank", "goodbye", "bye"],
                    "description": "Caller ended the call politely after the success confirmation",
                    "target": TARGETS.OURS,
                },
            ],
        },
    ],
}

CALLER_FACTS = [
    "Requested language: English",
    "Reason for call: Medication refill",
    'Full name: Adam B. If they ask to confirm the full name again, repeat "Adam B".',
    'Date of birth: June 2, 1996. Say it as: "June second nineteen ninety six".',
    'Phone number: 3052042944. Say it as: "305 204 2944".',
    'Medication request: "Avastin 5mg use the same pharmacy on profile".',
    'Final confirmation phrase: "That\'s correct, this is it."',
]

CUSTOM_INSTRUCTIONS = [
    'If they ask you to choose a language, say only "English."',
    'The first request after they ask how they can help should be "Medication refill."',
    'When they ask whether to use the caller number, say "Use 305 204 2944."',
    "When they ask for your full name and date of birth, provide both together.",
    'If they ask to confirm the full name, repeat "Adam B" once more.',
    'When they ask for the medication name and dosage, say "Avastin 5mg use the same pharmacy on profile" in one response.',
    'If they ask whether anything else is needed, say "That\'s correct, this is it."',
    "After the clinic gives a success confirmation for the refill request, thank them briefly and end the call.",
]

SYSTEM_PROMPT = build_system_prompt(
    objective=(
        "Select English, request a medication refill, verify the callback number, "
        "provide identity details, request Avastin 5mg using the same pharmacy on profile, "
        "and wait for the refill success confirmation."
    ),
    caller_facts=CALLER_FACTS,
    custom_instructions=CUSTOM_INSTRUCTIONS,
)

FLOW_ID = "tampa_medication_refill"
