"""
Conversation Flow Registry

This file automatically imports all flows from the flows/ directory.
You don't need to edit this file - just add new flow files to flows/

To add a new flow:
1. Copy flows/_template_flow.py to flows/your_flow_name.py
2. Edit your new flow file
3. It will be automatically imported!
"""

import os
import importlib
from pathlib import Path

# Auto-discover and import all flow files
ALL_FLOWS = []
AVAILABLE_FLOWS = {}
SYSTEM_PROMPTS = {}

# Get the flows directory
flows_dir = Path(__file__).parent / "flows"

# Import all Python files in the flows directory (except __init__.py and templates)
if flows_dir.exists():
    for flow_file in flows_dir.glob("*.py"):
        # Skip __init__.py and template files
        if flow_file.name.startswith("_"):
            continue

        # Import the module
        module_name = flow_file.stem
        try:
            module = importlib.import_module(f"flows.{module_name}")

            # Check if module has required attributes
            if (
                hasattr(module, "FLOW")
                and hasattr(module, "SYSTEM_PROMPT")
                and hasattr(module, "FLOW_ID")
            ):
                flow = module.FLOW
                flow_id = module.FLOW_ID
                system_prompt = module.SYSTEM_PROMPT

                # Add to registries
                ALL_FLOWS.append(flow)
                AVAILABLE_FLOWS[flow_id] = flow["steps"]
                SYSTEM_PROMPTS[flow_id] = system_prompt

                print(f"✓ Loaded flow: {flow['name']} (ID: {flow_id})")
            else:
                print(
                    f"⚠ Skipped {module_name}: Missing FLOW, SYSTEM_PROMPT, or FLOW_ID"
                )
        except Exception as e:
            print(f"✗ Error loading {module_name}: {e}")

# For backward compatibility with server.py
# Use the first flow as default if available
if ALL_FLOWS:
    CONVERSATION_FLOW = ALL_FLOWS[0]["steps"]
    SYSTEM_PROMPT = list(SYSTEM_PROMPTS.values())[0]
else:
    print("⚠ WARNING: No flows found in flows/ directory!")
    CONVERSATION_FLOW = []
    SYSTEM_PROMPT = ""

# Print summary
print(f"\n{'='*60}")
print(f"Conversation Flow Registry Loaded")
print(f"{'='*60}")
print(f"Total flows loaded: {len(ALL_FLOWS)}")
print(f"Available flow IDs: {list(AVAILABLE_FLOWS.keys())}")
print(f"{'='*60}\n")
