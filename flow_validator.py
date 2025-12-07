# Flow Validation System
# Validates if a conversation flow met the expected criteria

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class FlowAssertion:
    """Defines an assertion to validate against the flow"""
    step: int
    assertion_type: str  # "contains", "matches", "not_contains", "step_reached"
    expected_value: Optional[str] = None
    description: str = ""

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
        
        for assertion in assertions:
            passed, message = self._check_assertion(assertion)
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
            transcript=self.conversation_history.copy()
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
        
        # Combine both sides of conversation for checking
        full_text = f"{exchange['clinic_said']} {exchange['we_said']}".lower()
        expected = assertion.expected_value.lower() if assertion.expected_value else ""
        
        if assertion.assertion_type == "contains":
            if expected in full_text:
                return True, f"Step {assertion.step} contains '{assertion.expected_value}'"
            else:
                return False, f"Step {assertion.step} missing '{assertion.expected_value}' - {assertion.description}"
        
        elif assertion.assertion_type == "not_contains":
            if expected not in full_text:
                return True, f"Step {assertion.step} correctly doesn't contain '{assertion.expected_value}'"
            else:
                return False, f"Step {assertion.step} incorrectly contains '{assertion.expected_value}' - {assertion.description}"
        
        elif assertion.assertion_type == "matches":
            # Fuzzy match - check if key words are present
            keywords = expected.split()
            matches = sum(1 for kw in keywords if kw in full_text)
            if matches >= len(keywords) * 0.7:  # 70% of keywords must match
                return True, f"Step {assertion.step} matches pattern"
            else:
                return False, f"Step {assertion.step} doesn't match pattern '{assertion.expected_value}' - {assertion.description}"
        
        return False, f"Unknown assertion type: {assertion.assertion_type}"
    
    def reset(self):
        """Reset the conversation history for a new flow"""
        self.conversation_history.clear()
    
    def export_transcript(self, filename: str):
        """Export the conversation transcript to a JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
