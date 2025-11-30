# Phone Call Automation Framework

An AI-powered system for automating phone call testing with intelligent, context-aware responses.

## 🎯 What It Does

This framework allows you to:
- **Make automated phone calls** to test AI voice agents
- **Listen and transcribe** what the other party says
- **Respond intelligently** using AI-generated natural language
- **Record conversations** for analysis
- **Define test flows** with flexible, context-based prompts

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

## 📚 Additional Resources

- [Twilio Media Streams Documentation](https://www.twilio.com/docs/voice/twiml/stream)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [OpenAI TTS API](https://platform.openai.com/docs/guides/text-to-speech)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

[Your License Here]
