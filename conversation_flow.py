"""
Conversation Flow Registry

This file automatically imports all flows from the flows/ directory,
including flows nested inside clinic-specific subdirectories.

To add a new flow:
1. Copy flows/_template_flow.py to a new file inside flows/
   or a nested clinic folder such as flows/tampa/
2. Edit your new flow file
3. It will be automatically imported!
"""

import importlib
import os
import re
from pathlib import Path
from typing import Iterable

ALL_FLOWS = []
AVAILABLE_FLOWS = {}
SYSTEM_PROMPTS = {}

flows_dir = Path(__file__).parent / "flows"
FLOW_ID_PATTERN = re.compile(r"^\s*FLOW_ID\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)

CONVERSATION_FLOW = []
SYSTEM_PROMPT = ""


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _iter_flow_files() -> list[Path]:
    if not flows_dir.exists():
        return []

    flow_files = []
    for flow_file in sorted(flows_dir.rglob("*.py")):
        relative_parts = flow_file.relative_to(flows_dir).with_suffix("").parts
        if any(part.startswith("_") for part in relative_parts):
            continue
        flow_files.append(flow_file)
    return flow_files


def _module_name_for_file(flow_file: Path) -> str:
    relative_parts = flow_file.relative_to(flows_dir).with_suffix("").parts
    return ".".join(("flows", *relative_parts))


def _extract_flow_id(flow_file: Path) -> str | None:
    try:
        contents = flow_file.read_text(encoding="utf-8")
    except OSError:
        return None

    match = FLOW_ID_PATTERN.search(contents)
    return match.group(1) if match else None


def _resolve_flow_files(flow_ids: Iterable[str] | None) -> tuple[list[Path], list[str]]:
    flow_files = _iter_flow_files()
    if not flow_ids:
        return flow_files, []

    requested = [flow_id for flow_id in flow_ids if flow_id]
    selected_files: list[Path] = []
    unresolved = []

    for requested_id in requested:
        matched_file = next(
            (flow_file for flow_file in flow_files if _extract_flow_id(flow_file) == requested_id),
            None,
        )
        if matched_file:
            selected_files.append(matched_file)
        else:
            unresolved.append(requested_id)

    return selected_files, unresolved


def load_registry(flow_ids: Iterable[str] | None = None, verbose: bool | None = None):
    verbose = _env_flag("FLOW_REGISTRY_VERBOSE", True) if verbose is None else verbose
    selected_files, unresolved = _resolve_flow_files(flow_ids)

    all_flows = []
    available_flows = {}
    system_prompts = {}

    for flow_file in selected_files:
        module_name = _module_name_for_file(flow_file)
        try:
            module = importlib.import_module(module_name)
            if (
                hasattr(module, "FLOW")
                and hasattr(module, "SYSTEM_PROMPT")
                and hasattr(module, "FLOW_ID")
            ):
                flow = dict(module.FLOW)
                flow_id = module.FLOW_ID
                flow["flow_id"] = flow_id

                all_flows.append(flow)
                available_flows[flow_id] = flow["steps"]
                system_prompts[flow_id] = module.SYSTEM_PROMPT

                if verbose:
                    print(f"✓ Loaded flow: {flow['name']} (ID: {flow_id})")
            elif verbose:
                print(f"⚠ Skipped {module_name}: Missing FLOW, SYSTEM_PROMPT, or FLOW_ID")
        except Exception as exc:
            if verbose:
                print(f"✗ Error loading {module_name}: {exc}")

    if verbose and unresolved:
        print(f"⚠ Requested flow IDs not found: {unresolved}")

    if verbose:
        print(f"\n{'='*60}")
        print("Conversation Flow Registry Loaded")
        print(f"{'='*60}")
        print(f"Total flows loaded: {len(all_flows)}")
        print(f"Available flow IDs: {list(available_flows.keys())}")
        print(f"{'='*60}\n")

    return all_flows, available_flows, system_prompts


def refresh_registry(flow_ids: Iterable[str] | None = None, verbose: bool | None = None):
    global ALL_FLOWS, AVAILABLE_FLOWS, SYSTEM_PROMPTS, CONVERSATION_FLOW, SYSTEM_PROMPT

    ALL_FLOWS, AVAILABLE_FLOWS, SYSTEM_PROMPTS = load_registry(flow_ids=flow_ids, verbose=verbose)
    if ALL_FLOWS:
        CONVERSATION_FLOW = ALL_FLOWS[0]["steps"]
        SYSTEM_PROMPT = list(SYSTEM_PROMPTS.values())[0]
    else:
        CONVERSATION_FLOW = []
        SYSTEM_PROMPT = ""

    return ALL_FLOWS


def get_flow_by_id(flow_id: str, verbose: bool | None = None):
    flows, _, _ = load_registry(flow_ids=[flow_id], verbose=verbose)
    return flows[0] if flows else None


requested_flow_ids = [
    item.strip()
    for item in os.getenv("FLOW_REGISTRY_TARGETS", "").split(",")
    if item.strip()
]

refresh_registry(flow_ids=requested_flow_ids or None, verbose=_env_flag("FLOW_REGISTRY_VERBOSE", True))
