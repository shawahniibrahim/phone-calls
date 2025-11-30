import os
from dotenv import load_dotenv
from call_manager import CallManager

load_dotenv()

def main():
    """
    Simple script to initiate a phone call.
    The conversation is handled by server.py via WebSocket.
    """
    target_number = os.getenv("TARGET_PHONE_NUMBER")
    if not target_number:
        print("ERROR: TARGET_PHONE_NUMBER not set in .env")
        return
    
    print("=" * 60)
    print("INITIATING PHONE CALL")
    print("=" * 60)
    print(f"\nCalling: {target_number}")
    print("\nMake sure the server is running (python run.py)")
    print("The conversation will be handled automatically by the AI agent.")
    print("\nPress Ctrl+C to exit after the call is initiated.")
    print("=" * 60)
    
    try:
        call_manager = CallManager()
        call_sid = call_manager.make_call(target_number)
        print(f"\n✓ Call initiated successfully!")
        print(f"  Call SID: {call_sid}")
        print(f"\nThe call is now active. Check the server logs to see the conversation.")
        print("The AI will:")
        print("  1. Greet the person who answers")
        print("  2. Listen to their response")
        print("  3. Respond intelligently")
        print("  4. Continue the conversation")
        
    except Exception as e:
        print(f"\n✗ Error initiating call: {e}")

if __name__ == "__main__":
    main()
