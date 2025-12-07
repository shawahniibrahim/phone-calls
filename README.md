# Phone Call Automation Framework

An AI-powered system for automating phone call testing with intelligent, context-aware responses.

## 🎯 What It Does

This framework allows you to:
- **Make automated phone calls** to test AI voice agents
- **Listen and transcribe** what the other party says
- **Respond intelligently** using AI-generated natural language
- **Validate conversations** with automated assertions
- **Run multiple test scenarios** and get pass/fail reports
- **Record conversations** for analysis

## 📝 Simple Overview

**You edit ONE file:** `conversation_flow.py` - Define what to say and what to validate

**You run ONE of two commands:**
- `python demo_call.py` - Make a single test call
- `python run_tests.py` - Run all test flows and get a report

That's it!

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Twilio Account (Account SID, Auth Token, Phone Number)
- OpenAI API Key
- Ngrok Account (for tunneling)

### Installation

1. **Clone the repository and navigate to the directory**

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```ini
   OPENAI_API_KEY=sk-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=+1234567890
   TARGET_PHONE_NUMBER=+1987654321
   NGROK_AUTHTOKEN=...
   SERVER_URL=
   ```

### Running the System

**Step 1: Start the Server** (Terminal 1)
```bash
python run.py
```

This will:
- Start an ngrok tunnel
- Print the public URL
- Start the FastAPI server

**Step 2: Make a Call** (Terminal 2)
```bash
python demo_call.py
```

The system will:
- Call the TARGET_PHONE_NUMBER
- Listen to what they say
- Respond intelligently based on your conversation flow
- Record the full conversation

## 📝 Writing Test Flows

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
    {
        "step": 3,
        "expect": "asking for preferred time",
        "respond_with": "Say you're available next Monday afternoon",
        "example": "Next Monday afternoon works for me"
    },
]
```

### Configure Patient Information

Edit the `SYSTEM_PROMPT` in `conversation_flow.py`:

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

### How It Works

1. **System listens** to what the other party says
2. **Transcribes** the speech using OpenAI Whisper
3. **AI analyzes** the context (what are they asking?)
4. **Generates response** based on your flow guidance
5. **Speaks back** using OpenAI TTS
6. **Repeats** until conversation ends

## 🧪 Example Test Scenarios

### Scenario 1: Book Appointment

```python
CONVERSATION_FLOW = [
    {"step": 1, "expect": "greeting", "respond_with": "Say you want to book appointment"},
    {"step": 2, "expect": "asking for name", "respond_with": "Provide name: John Smith"},
    {"step": 3, "expect": "asking for DOB", "respond_with": "Provide DOB: Jan 15, 1990"},
    {"step": 4, "expect": "asking for time", "respond_with": "Say next Monday afternoon"},
    {"step": 5, "expect": "confirmation", "respond_with": "Confirm and thank them"},
]
```

### Scenario 2: Cancel Appointment

```python
CONVERSATION_FLOW = [
    {"step": 1, "expect": "greeting", "respond_with": "Say you want to cancel"},
    {"step": 2, "expect": "asking for name", "respond_with": "Provide name: Jane Doe"},
    {"step": 3, "expect": "asking for appointment date", "respond_with": "Say Friday 2 PM"},
    {"step": 4, "expect": "confirmation", "respond_with": "Confirm cancellation"},
]
```

### Scenario 3: Ask Questions

```python
CONVERSATION_FLOW = [
    {"step": 1, "expect": "greeting", "respond_with": "Ask about services offered"},
    {"step": 2, "expect": "explaining services", "respond_with": "Ask about insurance"},
    {"step": 3, "expect": "insurance info", "respond_with": "Ask about hours"},
    {"step": 4, "expect": "hours info", "respond_with": "Thank them"},
]
```

## 📊 Understanding the Logs

When running, you'll see:

```
[LISTENING] Waiting for the clinic AI to speak...
[SPEECH DETECTED] Clinic AI speaking (energy: 1234)
[SILENCE DETECTED] 3 seconds of silence/noise detected
[CLINIC AI] Transcribing 48000 bytes...
[CLINIC AI] Said: Hi, how can I help you today?
[AI] Generating intelligent response...
[US] Saying: I'd like to book an appointment, please.
[DEBUG] Sending 96000 bytes of PCM audio to Twilio...
[DEBUG] Sent 600 audio chunks on 'outbound' track to Twilio
[LISTENING] Waiting for clinic AI response...
```

## 📁 Project Structure

```
├── run.py                    # Starts server with ngrok
├── server.py                 # FastAPI server handling calls
├── demo_call.py              # Initiates phone calls
├── call_manager.py           # Twilio API wrapper
├── llm_client.py             # OpenAI API wrapper (Whisper, GPT, TTS)
├── audio_processor.py        # Audio format conversion
├── vad_detector.py           # Voice Activity Detection
├── ai_responder.py           # AI response generation
├── conversation_flow.py      # Test scenario configuration
├── conversation_script.py    # (Legacy) Fixed script approach
└── .env                      # Environment variables
```

## 🎙️ How Voice Activity Detection Works

The system uses energy-based Voice Activity Detection (VAD) to:
- **Detect speech** vs background noise
- **Wait for silence** (3 seconds) before responding
- **Ignore background noise** (office sounds, music, etc.)

You can adjust sensitivity in `server.py`:
```python
vad = VoiceActivityDetector(
    energy_threshold=500,      # Higher = less sensitive
    speech_frames=10,          # Frames to start speech
    silence_frames=30          # Frames to end speech (3 seconds)
)
```

## 🔧 Advanced Configuration

### Adjust Silence Detection

In `server.py`, change the silence detection time:
```python
if (current_time - last_high_energy_time) >= 3.0:  # Change 3.0 to desired seconds
```

### Change AI Voice

In `llm_client.py`, change the TTS voice:
```python
response = await self.client.audio.speech.create(
    model="tts-1",
    voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
    input=text,
    response_format="pcm"
)
```

### Adjust AI Behavior

Edit the `SYSTEM_PROMPT` in `conversation_flow.py` to change how the AI behaves:
```python
SYSTEM_PROMPT = """You are an AI assistant making a phone call.

Guidelines:
- Be polite and professional
- Keep responses brief (1-2 sentences)
- Sound natural and conversational
- Only provide information when asked
"""
```

## 📹 Call Recordings

After each call, the system saves:
- **Full conversation** as `full_call_TIMESTAMP.wav`
- Includes both sides of the conversation
- 8kHz, 16-bit, mono WAV format

## 🐛 Troubleshooting

### No audio being sent
- Check that `stream_sid` is set
- Verify `"track": "outbound"` is in media messages
- Check server logs for "Sent X audio chunks"

### System responds too early
- Increase silence detection time in server.py
- Adjust `energy_threshold` in VAD (higher = less sensitive)

### System doesn't respond
- Check if speech is being detected (look for "SPEECH DETECTED" in logs)
- Lower `energy_threshold` if needed
- Verify OpenAI API key is valid

### Call doesn't connect
- Ensure server is running first
- Check ngrok tunnel is active
- Verify Twilio credentials in .env

## 🎯 Best Practices

1. **Test incrementally** - Start with simple 2-3 step flows
2. **Monitor logs** - Watch what the AI hears and says
3. **Adjust thresholds** - Tune VAD for your environment
4. **Keep responses brief** - Phone conversations work best with short replies
5. **Use natural language** - Write prompts conversationally, not robotically

---

## 🧪 Automated Flow Testing

### What's New: Testing Framework

You can now automatically test conversation flows with assertions and get detailed pass/fail reports.

### Quick Start - Testing

**Option 1: Simple Manual Call**
```bash
python demo_call.py
```

**Option 2: Automated Testing**
```bash
# 1. Start server (Terminal 1)
python run.py

# 2. Run tests (Terminal 2)
python run_tests.py
```

### Creating Test Flows

**Everything is in one file:** `conversation_flow.py`

Each flow contains:
- Conversation steps (what to say)
- Assertions (what to validate)

```python
BOOKING_FLOW = {
    "name": "New Patient Booking",
    "phone_number": None,  # Uses TARGET_PHONE_NUMBER from .env
    "timeout": 300,
    "steps": [
        {
            "step": 1,
            "expect": "greeting or asking how they can help",
            "respond_with": "Say that you want to book an appointment",
            "example": "I'd like to book an appointment please",
            "assertions": [
                {"type": "step_reached", "description": "Call connected"}
            ]
        },
        {
            "step": 4,
            "expect": "asking for date of birth",
            "respond_with": "Provide a date of birth: January 15, 1990",
            "example": "January 15, 1990",
            "assertions": [
                {"type": "contains", "value": "january 15", "description": "DOB provided"}
            ]
        },
        # ... more steps
    ]
}
```

**To add a new flow:** Edit `conversation_flow.py` and add it to `ALL_FLOWS` list.

### Assertion Types

| Type | Purpose | Example |
|------|---------|---------|
| `step_reached` | Verify step completed | Check call reached step 12 |
| `contains` | Check for specific text | Verify "january 15" was said |
| `not_contains` | Ensure text NOT present | Ensure name not said too early |
| `matches` | Fuzzy keyword match | Check "headache vomit" mentioned |

### Test Output

```
============================================================
TEST SUMMARY
============================================================

Overall Results:
  Total Flows: 3
  Passed: 2
  Failed: 1
  Success Rate: 66.7%

Assertions:
  Total: 15
  Passed: 13
  Failed: 2

Flow Results:
  [PASS] Happy Path - New Patient Booking - 12/12 steps, 145.2s
  [PASS] Edge Case - Quick Responses - 12/12 steps, 152.8s
  [FAIL] Validation - All Required Info - 10/12 steps, 152.5s
```

### Output Files

After running tests:
- `flow_test_results_TIMESTAMP.json` - Complete test results
- `transcript_FLOWNAME_TIMESTAMP.json` - Conversation transcripts
- `full_call_TIMESTAMP.wav` - Audio recordings

### Automatic Hangup

The conversation flow now includes automatic call termination at step 12:

```python
{
    "step": 12,
    "expect": "Saying goodbye or ending the call",
    "respond_with": "Say goodbye and hang up",
    "example": "Goodbye, have a great day",
    "action": "hangup"  # Triggers automatic hangup
}
```

The call will automatically hang up when:
- Reaching step 12 (hangup action)
- Detecting goodbye phrases ("goodbye", "bye", "take care")

### Key Files

| File | Purpose | Edit? |
|------|---------|-------|
| `conversation_flow.py` | Define flows and assertions | ✅ YES |
| `demo_call.py` | Make a single manual call | ✅ YES (optional) |
| `run_tests.py` | Run all tests | ❌ NO |
| `flow_runner.py` | Test execution engine | ❌ NO |
| `flow_validator.py` | Validation logic | ❌ NO |

### Available Flow Types

You can now test different conversation scenarios:

| Flow Type | Purpose | Steps | File |
|-----------|---------|-------|------|
| `booking` | Book new appointment | 12 steps | Default in `conversation_flow.py` |
| `cancellation` | Cancel existing appointment | 7 steps | `CANCELLATION_FLOW` |
| `inquiry` | Ask questions about clinic | 5 steps | `INQUIRY_FLOW` |

**To add more flows:** Edit `conversation_flow.py` and add new flow definitions.

### When to Use What

| Use Case | Command | Purpose |
|----------|---------|---------|
| Quick manual test | `python demo_call.py` | Make one call, watch it live |
| Automated testing | `python run_tests.py` | Run all flows, get pass/fail report |

### Multiple Calls in One Test Run

The system runs all flows defined in `conversation_flow.py`:
1. **New Patient Booking** - Full booking flow (12 steps)
2. **Cancel Appointment** - Cancel existing appointment (7 steps)
3. **Ask Questions** - Inquiry about services (5 steps)

All tests run sequentially with 15-second delays between them.

**To add more flows:** Edit `conversation_flow.py` and add to `ALL_FLOWS` list.

### Example Test Scenarios

**Basic Validation:**
```python
FlowAssertion(step=1, assertion_type="step_reached", 
              description="Call started")
FlowAssertion(step=12, assertion_type="step_reached", 
              description="Call completed")
```

**Data Validation:**
```python
FlowAssertion(step=4, assertion_type="contains", 
              expected_value="january 15", 
              description="DOB provided")
FlowAssertion(step=6, assertion_type="contains", 
              expected_value="alex kattan", 
              description="Name provided")
```

**Behavior Validation:**
```python
FlowAssertion(step=1, assertion_type="not_contains", 
              expected_value="alex kattan", 
              description="Didn't volunteer name too early")
```

### Architecture Overview

**How a Test Flow Works:**

```
1. Test Runner (test_flows_example.py)
   └─▶ Initiates call via Call Manager
       └─▶ Twilio connects to your phone number
           └─▶ WebSocket opens to Server

2. During Conversation:
   Server receives audio
   ├─▶ Transcribe speech (OpenAI Whisper)
   ├─▶ Generate response (OpenAI GPT)
   ├─▶ Convert to speech (OpenAI TTS)
   ├─▶ Send audio back via Twilio
   └─▶ Record exchange (Flow Validator)

3. After Call Ends:
   Flow Validator
   ├─▶ Check all assertions
   ├─▶ Generate pass/fail result
   ├─▶ Export transcript JSON
   └─▶ Export audio WAV

4. Test Runner
   └─▶ Print summary of all flows
```

**Conversation Flow with Hangup:**

```
Step 1-11: Normal conversation
    │
    ├─▶ Greeting
    ├─▶ Patient info collection
    ├─▶ Appointment booking
    └─▶ Confirmation
    │
Step 12: Goodbye + Hangup
    │
    └─▶ Detect "goodbye" phrase
        └─▶ Send Twilio stop event
            └─▶ Call terminates gracefully
```

### Troubleshooting Tests

**Tests fail immediately:**
- Check server is running (`python run.py`)
- Verify .env has all required variables
- Check Twilio credentials are correct

**Assertions failing:**
- Review `transcript_*.json` files
- Check if expected text matches actual conversation
- Use `matches` instead of `contains` for flexibility

**Call doesn't hang up:**
- Verify step 12 has `"action": "hangup"`
- Check server logs for hangup event

---

## 📚 Additional Resources

- [Twilio Media Streams Documentation](https://www.twilio.com/docs/voice/twiml/stream)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

[Your License Here]
