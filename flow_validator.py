# Flow Validation System
# Validates if a conversation flow met the expected criteria

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class FlowAssertion:
    """Defines an assertion to validate against the flow"""
    step: int
    assertion_type: str  # "contains", "contains_any", "matches", "not_contains", "step_reached"
    expected_value: Optional[Any] = None
    description: str = ""
    target: str = "either"

@dataclass
class FlowResult:
    """Result of a single flow execution"""
    flow_name: str
    success: bool
    steps_completed: int
    total_steps: int
    assertions_passed: int
    assertions_failed: int
    failed_assertions: List[str]
    execution_time: float
    transcript: List[Dict[str, Any]]
    assertion_results: List[Dict[str, Any]] = field(default_factory=list)
    call_sid: Optional[str] = None
    call_status: Optional[str] = None
    conversation_file: Optional[str] = None
    transcript_file: Optional[str] = None
    recording_file: Optional[str] = None
    report_json: Optional[str] = None
    report_html: Optional[str] = None
    timed_out: bool = False
    error: Optional[str] = None

class FlowValidator:
    """Validates conversation flows against expected criteria"""
    
    def __init__(self):
        self.conversation_history = []
        
    def record_exchange(self, step: int, clinic_said: str, we_said: str):
        """Record a conversation exchange"""
        self.conversation_history.append({
            "step": step,
            "clinic_said": clinic_said,
            "we_said": we_said,
            "timestamp": datetime.now().isoformat()
        })
    
    def validate_flow(self, flow_name: str, assertions: List[FlowAssertion], 
                     expected_steps: int, execution_time: float) -> FlowResult:
        """
        Validate the flow against assertions
        
        Args:
            flow_name: Name of the flow being validated
            assertions: List of assertions to check
            expected_steps: Total number of expected steps
            execution_time: Time taken to execute the flow
            
        Returns:
            FlowResult with validation results
        """
        steps_completed = len(self.conversation_history)
        assertions_passed = 0
        assertions_failed = 0
        failed_assertions = []
        assertion_results = []
        
        for assertion in assertions:
            passed, message = self._check_assertion(assertion)
            assertion_results.append({
                "step": assertion.step,
                "type": assertion.assertion_type,
                "target": assertion.target,
                "expected_value": assertion.expected_value,
                "description": assertion.description,
                "passed": passed,
                "message": message,
            })
            if passed:
                assertions_passed += 1
            else:
                assertions_failed += 1
                failed_assertions.append(message)
        
        # Overall success: all assertions passed and reached expected steps
        success = (assertions_failed == 0 and steps_completed >= expected_steps)
        
        return FlowResult(
            flow_name=flow_name,
            success=success,
            steps_completed=steps_completed,
            total_steps=expected_steps,
            assertions_passed=assertions_passed,
            assertions_failed=assertions_failed,
            failed_assertions=failed_assertions,
            execution_time=execution_time,
            transcript=self.conversation_history.copy(),
            assertion_results=assertion_results,
        )
    
    def _check_assertion(self, assertion: FlowAssertion) -> tuple[bool, str]:
        """Check a single assertion"""
        
        if assertion.assertion_type == "step_reached":
            # Check if we reached a specific step
            reached = any(ex["step"] >= assertion.step for ex in self.conversation_history)
            if reached:
                return True, f"Step {assertion.step} reached"
            else:
                return False, f"Step {assertion.step} not reached - {assertion.description}"
        
        # Find the exchange for this step
        exchange = next((ex for ex in self.conversation_history if ex["step"] == assertion.step), None)
        
        if not exchange:
            return False, f"Step {assertion.step} not found - {assertion.description}"
        
        text = self._get_assertion_text(exchange, assertion.target)
        expected = (
            assertion.expected_value.lower()
            if isinstance(assertion.expected_value, str)
            else assertion.expected_value
        )
        
        if assertion.assertion_type == "contains":
            if expected and expected in text:
                return True, f"Step {assertion.step} contains '{assertion.expected_value}'"
            else:
                return False, f"Step {assertion.step} missing '{assertion.expected_value}' - {assertion.description}"

        elif assertion.assertion_type == "contains_any":
            candidates = self._normalize_expected_values(assertion.expected_value)
            matched = next((candidate for candidate in candidates if candidate in text), None)
            if matched:
                return True, f"Step {assertion.step} contains one of {candidates} (matched '{matched}')"
            return False, f"Step {assertion.step} missing all of {candidates} - {assertion.description}"
        
        elif assertion.assertion_type == "not_contains":
            if not expected or expected not in text:
                return True, f"Step {assertion.step} correctly doesn't contain '{assertion.expected_value}'"
            else:
                return False, f"Step {assertion.step} incorrectly contains '{assertion.expected_value}' - {assertion.description}"
        
        elif assertion.assertion_type == "matches":
            # Fuzzy match - check if key words are present
            keywords = self._normalize_expected_values(assertion.expected_value)
            if not keywords:
                return False, f"Step {assertion.step} has no pattern to match - {assertion.description}"
            matches = sum(1 for kw in keywords if kw in text)
            if matches >= len(keywords) * 0.7:  # 70% of keywords must match
                return True, f"Step {assertion.step} matches pattern"
            else:
                return False, f"Step {assertion.step} doesn't match pattern '{assertion.expected_value}' - {assertion.description}"
        
        return False, f"Unknown assertion type: {assertion.assertion_type}"

    def _get_assertion_text(self, exchange: Dict[str, Any], target: str) -> str:
        clinic_text = exchange["clinic_said"].lower()
        our_text = exchange["we_said"].lower()
        if target == "clinic":
            return clinic_text
        if target in {"ours", "assistant", "caller"}:
            return our_text
        return f"{clinic_text} {our_text}".strip()

    def _normalize_expected_values(self, expected_value: Any) -> List[str]:
        if expected_value is None:
            return []
        if isinstance(expected_value, list):
            return [str(item).lower() for item in expected_value if str(item).strip()]
        if isinstance(expected_value, str):
            if "|" in expected_value:
                return [item.strip().lower() for item in expected_value.split("|") if item.strip()]
            return [item.strip().lower() for item in expected_value.split() if item.strip()]
        return [str(expected_value).lower()]
    
    def reset(self):
        """Reset the conversation history for a new flow"""
        self.conversation_history.clear()
    
    def export_transcript(self, filename: str):
        """Export the conversation transcript to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
