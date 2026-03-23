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
- `clinic_assertions`: validations against `clinic_said`
- `our_assertions`: validations against `we_said`
- `assertions`: general validations like `step_reached`
"""

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
            "clinic_assertions": [
                {
                    "type": "contains",
                    "value": "keyword from the clinic side",
                    "description": "Clinic said the expected thing",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains",
                    "value": "keyword from our side",
                    "description": "Caller replied as expected",
                },
            ],
            "assertions": [
                {"type": "step_reached", "description": "Step 1 exchange completed"},
            ],
        },
        {
            "step": 2,
            "expect": "next expected response",
            "respond_with": "how to respond",
            "example": "example response",
            "clinic_assertions": [
                {
                    "type": "contains",
                    "value": "something from the clinic",
                    "description": "Clinic-side validation",
                },
            ],
            "our_assertions": [
                {
                    "type": "contains",
                    "value": "something from us",
                    "description": "Caller-side validation",
                },
            ],
        },
        # Add more steps as needed...
        {
            "step": 99,  # Last step
            "expect": "goodbye",
            "respond_with": "Say goodbye",
            "example": "Goodbye",
            "action": "hangup",  # This triggers automatic hangup
            "assertions": [{"type": "step_reached", "description": "Call completed"}],
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
