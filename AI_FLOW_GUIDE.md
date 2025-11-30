# AI-Driven Conversation Flow Guide

## Overview

The system now uses **AI to generate intelligent responses** based on what the clinic says, rather than using a fixed script.

## How It Works

1. **Clinic speaks** → System transcribes what they said
2. **AI analyzes** → Understands the context (are they asking for consent? date of birth? etc.)
3. **AI generates response** → Creates a natural, appropriate reply
4. **System speaks** → Sends the audio back to the clinic

## Configuring the Flow

Edit `conversation_flow.py` to define the expected conversation steps:

```python
CONVERSATION_FLOW = [
    {
        "step": 1,
        "expect": "greeting or asking how they can help",
        "respond_with": "Say that you want to book an appointment",
        "example": "I'd like to book an appointment please"
    },
    {
        "step": 2,
        "expect": "asking for consent or permission to record",
        "respond_with": "Provide consent and agree",
        "example": "Yes, that's fine"
    },
    # Add more steps...
]
```

### Each Step Has:

- **expect**: What context/topic the clinic might ask about
- **respond_with**: General guidance on how to respond
- **example**: An example response (AI will vary the wording naturally)

## Patient Information

Edit the `SYSTEM_PROMPT` in `conversation_flow.py` to change patient details:

```python
SYSTEM_PROMPT = """You are an AI assistant making a phone call to book a medical appointment.

Patient Information to use when asked:
- Name: John Smith
- Date of Birth: January 15, 1990
- Phone: 555-1234
- Reason: Book an appointment
- Preferred time: Next Monday afternoon
"""
```

## Example Scenarios

### Scenario 1: Book Appointment

```python
CONVERSATION_FLOW = [
    {"step": 1, "expect": "greeting", "respond_with": "Say you want to book appointment"},
    {"step": 2, "expect": "asking for name", "respond_with": "Provide name: John Smith"},
    {"step": 3, "expect": "asking for date of birth", "respond_with": "Provide DOB: Jan 15, 1990"},
    {"step": 4, "expect": "asking for preferred time", "respond_with": "Say next Monday afternoon"},
    {"step": 5, "expect": "confirmation", "respond_with": "Confirm and thank them"},
]
```

### Scenario 2: Cancel Appointment

```python
CONVERSATION_FLOW = [
    {"step": 1, "expect": "greeting", "respond_with": "Say you want to cancel appointment"},
    {"step": 2, "expect": "asking for name", "respond_with": "Provide name: Jane Doe"},
    {"step": 3, "expect": "asking for appointment date", "respond_with": "Say Friday at 2 PM"},
    {"step": 4, "expect": "confirmation", "respond_with": "Confirm cancellation"},
]
```

## Advantages

✅ **Natural variation** - AI generates different wording each time
✅ **Context-aware** - Responds appropriately to what's actually said
✅ **Flexible** - Can handle unexpected questions
✅ **Realistic** - Sounds more human than a fixed script

## Testing

1. Edit `conversation_flow.py` with your test scenario
2. Restart the server: `python run.py`
3. Make a call: `python demo_call.py`
4. Watch the logs to see the AI's responses

## Logs Show:

```
[CLINIC AI] Said: Hi, how can I help you today?
[AI] Generating intelligent response...
[US] Saying: I'd like to book an appointment, please.
```

The AI generates natural, contextually appropriate responses!
