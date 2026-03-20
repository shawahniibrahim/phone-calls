"""
TEMPLATE: Copy this file to create a new flow

Instructions:
1. Copy this file: cp flows/_template_flow.py flows/your_flow_name.py
2. Update the docstring above
3. Define your FLOW dictionary
4. Write your SYSTEM_PROMPT
5. Set a unique FLOW_ID
6. The flow will be automatically imported!
"""

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
                {"type": "step_reached", "description": "Step 1 completed"},
                {
                    "type": "contains",
                    "value": "keyword",
                    "description": "Keyword mentioned",
                },
            ],
        },
        {
            "step": 2,
            "expect": "next expected response",
            "respond_with": "how to respond",
            "example": "example response",
            "assertions": [
                {"type": "contains", "value": "something", "description": "Validation"}
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

SYSTEM_PROMPT = """You are an AI assistant making a phone call for [PURPOSE].

CRITICAL RULES:
- ONLY answer the EXACT question they asked
- Do NOT volunteer additional information
- Keep responses EXTREMELY brief (1 sentence, 5-7 words max)
- Be polite and natural

Information to use ONLY when specifically asked:
- Name: [NAME]
- Phone: [PHONE]
- Other info: [INFO]

Examples of CORRECT responses:
- They ask "X?" → You say "Y"
"""

# Flow identifier - MUST be unique across all flows
FLOW_ID = "your_unique_flow_id"
