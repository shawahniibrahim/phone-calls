# Quick Start Guide

## Setup (One Time)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify your `.env` file has all credentials:**
   - ✓ OPENAI_API_KEY
   - ✓ TWILIO_ACCOUNT_SID
   - ✓ TWILIO_AUTH_TOKEN
   - ✓ TWILIO_PHONE_NUMBER
   - ✓ TARGET_PHONE_NUMBER
   - ✓ NGROK_AUTHTOKEN

## Running the System

### Step 1: Start the Server

Open a terminal and run:

```bash
python run.py
```

This will:
- Start ngrok tunnel
- Print the public URL (e.g., `https://abc123.ngrok-free.app`)
- Start the FastAPI server

**Keep this terminal open!** The server needs to stay running.

### Step 2: Make a Call

Open a **second terminal** and run:

```bash
python demo_call.py
```

This will initiate a call to the TARGET_PHONE_NUMBER.

### Step 3: Watch the Conversation

Watch the server terminal (Terminal 1) to see the real-time conversation:

```
[CLINIC AI] Said: Hi, how can I help you today?
[AI] Generating intelligent response...
[US] Saying: I'd like to book an appointment, please.
```

## What Happens During the Call

1. **System listens** to what the other party says
2. **Transcribes** their speech using AI
3. **Generates intelligent response** based on context
4. **Speaks back** naturally
5. **Repeats** until conversation ends

## Customizing Your Test

### AI-Driven Approach (Recommended)

Edit `conversation_flow.py` to define your test scenario:

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
        "expect": "asking for date of birth",
        "respond_with": "Provide date of birth: January 15, 1990",
        "example": "January 15, 1990"
    },
]
```

### Configure Patient Info

Edit the `SYSTEM_PROMPT` in `conversation_flow.py`:

```python
Patient Information to use when asked:
- Name: John Smith
- Date of Birth: January 15, 1990
- Phone: 555-1234
```

## Call Recordings

After each call, find the recording:
- File: `full_call_TIMESTAMP.wav`
- Includes both sides of the conversation
- Listen to verify the test worked correctly

## Troubleshooting

- **"Missing Twilio credentials"**: Check your `.env` file
- **"NGROK_AUTHTOKEN not set"**: Add your ngrok token to `.env`
- **Call doesn't connect**: Make sure `run.py` is running first
- **No audio**: Check server logs for "Sent X audio chunks"
- **Responds too early**: Increase silence detection time in server.py

## Next Steps

- Read `README.md` for detailed documentation
- Read `AI_FLOW_GUIDE.md` for advanced flow configuration
- Experiment with different test scenarios

## Files Overview

- `run.py` - Starts the server with ngrok
- `server.py` - Handles the call and AI conversation
- `demo_call.py` - Initiates the call
- `conversation_flow.py` - **Edit this for your test scenarios**
- `ai_responder.py` - AI response generation logic
- `llm_client.py` - OpenAI API wrapper
- `audio_processor.py` - Audio format conversion
- `vad_detector.py` - Voice activity detection
