#!/usr/bin/env python3
"""
Run a single configured flow by flow ID.

Examples:
    python run_flow.py tampa_faq
    python run_flow.py --list
    python run_flow.py tampa_faq --timeout 240
"""

import argparse
import asyncio
import copy
import json
import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

from flow_runner import FlowTestRunner


load_dotenv()


def _load_registry(target_flow_id: str | None = None, verbose: bool = False):
    if target_flow_id:
        os.environ["FLOW_REGISTRY_TARGETS"] = target_flow_id
    else:
        os.environ.pop("FLOW_REGISTRY_TARGETS", None)
    os.environ["FLOW_REGISTRY_VERBOSE"] = "1" if verbose else "0"

    import conversation_flow

    conversation_flow.refresh_registry(
        flow_ids=[target_flow_id] if target_flow_id else None,
        verbose=verbose,
    )
    return conversation_flow


def _find_flow(flow_id: str):
    registry = _load_registry(target_flow_id=flow_id, verbose=False)
    flow = registry.get_flow_by_id(flow_id, verbose=False)
    return copy.deepcopy(flow) if flow else None


def _list_flows():
    registry = _load_registry(verbose=False)
    print("Available flows:")
    for flow in registry.ALL_FLOWS:
        print(
            f"  - {flow.get('flow_id', 'unknown')}: {flow['name']} "
            f"(phone: {flow.get('phone_number') or 'TARGET_PHONE_NUMBER'})"
        )


def _clear_reports():
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print("Reports directory is already clean.")
        return

    for child in reports_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    print("Cleared report artifacts.")


async def _run(flow):
    runner = FlowTestRunner()
    result = await runner.run_flow(flow)
    print("\nRESULT")
    print(
        json.dumps(
            {
                "flow_id": flow.get("flow_id"),
                "flow_name": result.flow_name,
                "success": result.success,
                "steps_completed": result.steps_completed,
                "total_steps": result.total_steps,
                "assertions_passed": result.assertions_passed,
                "assertions_failed": result.assertions_failed,
                "failed_assertions": result.failed_assertions,
                "execution_time": result.execution_time,
                "error": result.error,
                "call_sid": result.call_sid,
                "call_status": result.call_status,
                "timed_out": result.timed_out,
                "conversation_file": result.conversation_file,
                "recording_file": result.recording_file,
                "report_html": result.report_html,
                "report_json": result.report_json,
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Run one configured phone-call flow")
    parser.add_argument("flow_id", nargs="?", help="Flow ID to run, for example: tampa_faq")
    parser.add_argument("--list", action="store_true", help="List available flow IDs")
    parser.add_argument("--timeout", type=int, help="Override flow timeout in seconds")
    parser.add_argument("--phone", help="Override target phone number for this run")
    parser.add_argument(
        "--clear-reports",
        action="store_true",
        help="Delete everything inside the reports directory before running the flow",
    )
    args = parser.parse_args()

    if args.list:
        _list_flows()
        return

    if not args.flow_id:
        parser.print_help()
        print()
        _list_flows()
        sys.exit(1)

    flow = _find_flow(args.flow_id)
    if not flow:
        print(f"Unknown flow_id: {args.flow_id}")
        print()
        _list_flows()
        sys.exit(1)

    if args.clear_reports:
        _clear_reports()

    if args.timeout:
        flow["timeout"] = args.timeout
    if args.phone:
        flow["phone_number"] = args.phone

    print(f"Running flow_id={flow['flow_id']} name={flow['name']}")
    try:
        asyncio.run(_run(flow))
    except KeyboardInterrupt:
        print("\nRun interrupted by user.")


if __name__ == "__main__":
    main()
