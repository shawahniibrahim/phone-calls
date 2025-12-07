# Files Explained - Simple Guide

## Files You'll Use

### 1. `conversation_flow.py` ⭐ MAIN FILE
**What:** Define your conversation flows and test assertions
**Edit:** YES - This is where you do all your work
**Example:**
```python
BOOKING_FLOW = {
    "name": "Book Appointment",
    "steps": [
        {
            "step": 1,
            "expect": "greeting",
            "respond_with": "Say you want to book",
            "example": "I'd like to book an appointment",
            "assertions": [
                {"type": "step_reached", "description": "Call connected"}
            ]
        },
    ]
}
```

### 2. `demo_call.py`
**What:** Make a single phone call manually
**Edit:** Optional (change phone number if needed)
**Use when:** You want to test one call and watch it live
**Run:** `python demo_call.py`

### 3. `run_tests.py`
**What:** Runs all flows from conversation_flow.py automatically
**Edit:** NO - Just run it
**Use when:** You want to test multiple flows and get a report
**Run:** `python run_tests.py`

---

## Files You Don't Touch (Internal)

### `flow_runner.py`
**What:** Engine that executes tests
**Purpose:** Takes flows from conversation_flow.py and runs them
**Edit:** NO

### `flow_validator.py`
**What:** Validation logic
**Purpose:** Checks if assertions passed or failed
**Edit:** NO

### `server.py`
**What:** Handles the actual phone call
**Purpose:** Receives audio, transcribes, generates responses
**Edit:** Only if you need to change how calls work

### `llm_client.py`
**What:** Talks to OpenAI API
**Purpose:** Transcription, text generation, text-to-speech
**Edit:** NO

### `call_manager.py`
**What:** Talks to Twilio API
**Purpose:** Initiates phone calls
**Edit:** NO

### `ai_responder.py`
**What:** Generates intelligent responses
**Purpose:** Uses conversation flow to create natural replies
**Edit:** NO

### `audio_processor.py`
**What:** Audio format conversion
**Purpose:** Converts between PCM and mulaw formats
**Edit:** NO

### `vad_detector.py`
**What:** Voice activity detection
**Purpose:** Detects when someone is speaking vs silence
**Edit:** NO

---

## Typical Workflow

### For Manual Testing:
1. Edit `conversation_flow.py` (define what to say)
2. Run `python run.py` (start server)
3. Run `python demo_call.py` (make call)
4. Watch the logs

### For Automated Testing:
1. Edit `conversation_flow.py` (define flows + assertions)
2. Run `python run.py` (start server)
3. Run `python run_tests.py` (run all tests)
4. Review the summary report

---

## Quick Reference

| Want to... | Edit this file |
|------------|----------------|
| Add a new conversation flow | `conversation_flow.py` |
| Change what the AI says | `conversation_flow.py` |
| Add test assertions | `conversation_flow.py` |
| Make a quick test call | Just run `demo_call.py` |
| Run all tests | Just run `run_tests.py` |
| Change patient info | `conversation_flow.py` (SYSTEM_PROMPT) |

---

## Summary

**You only need to edit ONE file:** `conversation_flow.py`

Everything else either:
- Runs automatically (`run_tests.py`, `demo_call.py`)
- Is internal plumbing (all other .py files)
