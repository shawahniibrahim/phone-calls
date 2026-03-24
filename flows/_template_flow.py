"""
TEMPLATE: Copy this file to create a new flow

Instructions:
1. Copy this file: cp flows/_template_flow.py flows/your_flow_name.py
2. Update the docstring above
3. Define your FLOW dictionary
4. Define caller facts and any extra instructions
5. Set a unique FLOW_ID
6. The flow will be automatically imported!

Each step represents one exchange:
- `expect`: what the clinic says in that exchange
- `respond_with` / `example`: what our caller says back in that same exchange
- `assertions`: validations for that business step
  - use `target: TARGETS.CLINIC` or `target: TARGETS.OURS` to choose which side to check
  - use `assert_on: ASSERT_ON.NEXT_EXCHANGE` if the assertion should validate the clinic's follow-up answer
"""

from flow_constants import ACTIONS, ASSERTIONS, ASSERT_ON, TARGETS
from prompt_builder import build_system_prompt

FLOW = {
    "name": "Your Flow Name",
    "phone_number": None,  # Will use TARGET_PHONE_NUMBER from .env
    "timeout": 180,  # Timeout in seconds
    "steps": [
        {
            "step": 1,
            "expect": "what you expect the other party to say",
            "respond_with": "instruction for AI on how to respond",
            "example": "example of what the AI should say",
            "assertions": [
                {"type": ASSERTIONS.STEP_REACHED, "description": "Step 1 completed"},
                {
                    "type": ASSERTIONS.CONTAINS,
                    "value": "keyword from the clinic side",
                    "description": "Clinic said the expected thing",
                    "target": TARGETS.CLINIC,
                },
                {
                    "type": ASSERTIONS.CONTAINS,
                    "value": "keyword from our side",
                    "description": "Caller replied as expected",
                    "target": TARGETS.OURS,
                },
            ],
        },
        {
            "step": 2,
            "expect": "the clinic answers the thing you just asked about",
            "respond_with": "ask the next thing",
            "example": "What are your working hours?",
            "assertions": [
                {
                    "type": ASSERTIONS.CONTAINS,
                    "value": "working hours",
                    "description": "Caller asked about working hours",
                    "target": TARGETS.OURS,
                },
                {
                    "type": ASSERTIONS.MATCHES,
                    "value": "monday friday 8 5",
                    "description": "Clinic answered with working hours",
                    "target": TARGETS.CLINIC,
                    "assert_on": ASSERT_ON.NEXT_EXCHANGE,
                },
            ],
        },
        # Add more steps as needed...
        {
            "step": 99,  # Last step
            "expect": "goodbye",
            "respond_with": "Say goodbye",
            "example": "Goodbye",
            "action": ACTIONS.HANGUP,  # This triggers automatic hangup
            "assertions": [{"type": ASSERTIONS.STEP_REACHED, "description": "Call completed"}],
        },
    ],
}

CALLER_FACTS = [
    "Name: [NAME]",
    "Phone: [PHONE]",
    "Other important info: [INFO]",
]

CUSTOM_INSTRUCTIONS = [
    "Open with [OPENING LINE].",
    "Keep the call moving one answer at a time.",
]

SYSTEM_PROMPT = build_system_prompt(
    objective="[PURPOSE OF THE CALL]",
    caller_facts=CALLER_FACTS,
    custom_instructions=CUSTOM_INSTRUCTIONS,
)

# Flow identifier - MUST be unique across all flows
FLOW_ID = "your_unique_flow_id"
