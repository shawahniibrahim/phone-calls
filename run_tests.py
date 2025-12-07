#!/usr/bin/env python3
"""
Test Runner - Loads flows from conversation_flow.py and runs them
Edit conversation_flow.py to add/modify flows and assertions
"""

import asyncio
import os
from dotenv import load_dotenv
from flow_runner import FlowTestRunner
from conversation_flow import ALL_FLOWS

load_dotenv()

# Load flows from conversation_flow.py
# Each flow already has its assertions defined
TEST_FLOWS = []
for flow in ALL_FLOWS:
    # Set phone number from env if not specified
    if not flow.get("phone_number"):
        flow["phone_number"] = os.getenv("TARGET_PHONE_NUMBER")
    TEST_FLOWS.append(flow)


async def main():
    """Run all test flows"""
    print("\n" + "=" * 60)
    print("CONVERSATION FLOW TEST SUITE")
    print("=" * 60)
    print(f"\nConfigured {len(TEST_FLOWS)} test flows")
    print("\nMake sure:")
    print("  1. Server is running (python run.py)")
    print("  2. TARGET_PHONE_NUMBER is set in .env")
    print("  3. Twilio credentials are configured")
    print("\n" + "=" * 60)
    
    input("\nPress Enter to start tests (or Ctrl+C to cancel)...")
    
    runner = FlowTestRunner()
    
    # Run all flows with 15 second delay between them
    await runner.run_flows(TEST_FLOWS, delay_between_flows=15)
    
    # Export results
    runner.export_results()
    
    print("\n✓ Test suite complete!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest suite cancelled by user")
    except Exception as e:
        print(f"\n\nError running test suite: {e}")
        import traceback
        traceback.print_exc()
