# How to Run Tests - Step by Step

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure .env file:**
   Make sure you have:
   ```
   OPENAI_API_KEY=sk-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=+1234567890
   TARGET_PHONE_NUMBER=+1987654321
   NGROK_AUTHTOKEN=...
   ```

## Running Tests

### Step 1: Start the Server

Open **Terminal 1** and run:

```bash
python run.py
```

You should see:
```
Public URL: https://abc123.ngrok-free.app
Server running on http://0.0.0.0:8000
```

**Keep this terminal open!** The server needs to stay running.

---

### Step 2: Run Tests

Open **Terminal 2** and run:

```bash
python run_tests.py
```

This will:
1. Load all flows from `conversation_flow.py`
2. Ask you to press Enter to start
3. Make calls for each flow (with 15 second delays between them)
4. Show you real-time progress
5. Display a summary at the end

---

## What You'll See

### During Tests:

```
============================================================
CONVERSATION FLOW TEST SUITE
============================================================

Configured 3 test flows

Make sure:
  1. Server is running (python run.py)
  2. TARGET_PHONE_NUMBER is set in .env
  3. Twilio credentials are configured

============================================================

Press Enter to start tests (or Ctrl+C to cancel)...

============================================================
Running Flow: New Patient Booking
============================================================
Flow Type: booking
Phone: +1234567890
Expected Steps: 12
Timeout: 300s

Initiating call...
✓ Call initiated: CA1234567890abcdef

Monitoring call progress...
```

### After All Tests Complete:

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

Execution Time: 450.5s

Flow Results:
  [PASS] New Patient Booking - 12/12 steps, 145.2s
  [PASS] Cancel Appointment - 7/7 steps, 152.8s
  [FAIL] Ask Questions - 3/5 steps, 152.5s

Failed Flows Detail:

  ✗ Ask Questions
    - Step 4 not reached - Call ended early
    - Step 5 not reached - Call completed

============================================================

Results exported to: flow_test_results_20251203_143022.json

✓ Test suite complete!
```

---

## Output Files

After running tests, you'll find:

1. **Test Results:**
   - `flow_test_results_TIMESTAMP.json` - Complete results

2. **Transcripts:**
   - `transcript_NewPatientBooking_TIMESTAMP.json`
   - `transcript_CancelAppointment_TIMESTAMP.json`
   - `transcript_AskQuestions_TIMESTAMP.json`

3. **Audio Recordings:**
   - `full_call_TIMESTAMP.wav` (for each call)

---

## Quick Test (Single Call)

If you just want to test one call manually:

```bash
# Terminal 1: Start server
python run.py

# Terminal 2: Make one call
python demo_call.py
```

This makes a single call using the default BOOKING_FLOW.

---

## Troubleshooting

### "Server not running"
- Make sure Terminal 1 is still running `python run.py`
- Check that you see "Server running on http://0.0.0.0:8000"

### "Missing environment variables"
- Check your .env file has all required variables
- Make sure .env is in the same directory as run_tests.py

### "Call fails immediately"
- Verify Twilio credentials are correct
- Check TARGET_PHONE_NUMBER is valid
- Make sure you have Twilio credit

### "No assertions passing"
- Check the transcript JSON files to see what was actually said
- Adjust assertions in conversation_flow.py if needed

---

## Tips

1. **Start small:** Test with `demo_call.py` first before running full suite
2. **Watch server logs:** Terminal 1 shows what's happening during calls
3. **Review transcripts:** JSON files show exact conversation
4. **Adjust delays:** Edit `run_tests.py` if 15 seconds between calls isn't enough
5. **One flow at a time:** Comment out flows in `conversation_flow.py` ALL_FLOWS list to test individually

---

## Example: Testing Just One Flow

Edit `conversation_flow.py`:

```python
# Comment out flows you don't want to test
ALL_FLOWS = [
    BOOKING_FLOW,
    # CANCELLATION_FLOW,  # Commented out
    # INQUIRY_FLOW,       # Commented out
]
```

Then run:
```bash
python run_tests.py
```

Only BOOKING_FLOW will run.
