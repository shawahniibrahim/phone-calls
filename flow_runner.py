# Flow Test Runner
# Executes multiple conversation flows sequentially and reports results

import asyncio
import time
import json
from typing import List, Dict, Any
from datetime import datetime
from colorama import init, Fore, Style
from flow_validator import FlowValidator, FlowAssertion, FlowResult
from call_manager import CallManager
import os
from dotenv import load_dotenv

# Initialize colorama for colored terminal output
init(autoreset=True)

load_dotenv()

class FlowTestRunner:
    """Runs multiple conversation flows and validates results"""
    
    def __init__(self):
        self.results: List[FlowResult] = []
        self.call_manager = CallManager()
        
    async def run_flow(self, flow_config: Dict[str, Any]) -> FlowResult:
        """
        Run a single flow test
        
        Args:
            flow_config: Dictionary containing:
                - name: Flow name
                - phone_number: Number to call
                - flow_type: Type of flow (booking, cancellation, inquiry)
                - assertions: List of FlowAssertion objects
                - expected_steps: Number of expected steps
                - timeout: Max execution time in seconds
                
        Returns:
            FlowResult object
        """
        flow_name = flow_config["name"]
        phone_number = flow_config.get("phone_number", os.getenv("TARGET_PHONE_NUMBER"))
        flow_type = flow_config.get("flow_type", "booking")
        timeout = flow_config.get("timeout", 300)  # 5 minutes default
        
        # Extract assertions from steps
        from flow_validator import FlowAssertion
        steps = flow_config.get("steps", [])
        expected_steps = len(steps)
        assertions = []
        
        for step in steps:
            for assertion_dict in step.get("assertions", []):
                assertions.append(FlowAssertion(
                    step=step["step"],
                    assertion_type=assertion_dict["type"],
                    expected_value=assertion_dict.get("value"),
                    description=assertion_dict["description"]
                ))
        
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.CYAN}Running Flow: {flow_name}")
        print(f"{Fore.CYAN}{'=' * 60}")
        print(f"Flow Type: {flow_type}")
        print(f"Phone: {phone_number}")
        print(f"Expected Steps: {expected_steps}")
        print(f"Timeout: {timeout}s")
        
        validator = FlowValidator()
        start_time = time.time()
        
        try:
            # Initiate the call
            print(f"\n{Fore.YELLOW}Initiating call...")
            call_sid = self.call_manager.make_call(phone_number)
            print(f"{Fore.GREEN}✓ Call initiated: {call_sid}")
            
            # Wait for call to complete
            print(f"\n{Fore.YELLOW}Monitoring call progress...")
            await asyncio.sleep(timeout)
            
            execution_time = time.time() - start_time
            
            # Load conversation exchanges from file
            conversation_file = f"conversations/conversation_{call_sid}.json"
            if os.path.exists(conversation_file):
                print(f"\n{Fore.BLUE}Loading conversation data from {conversation_file}...")
                with open(conversation_file, 'r') as f:
                    exchanges = json.load(f)
                
                # Populate validator with exchanges
                for exchange in exchanges:
                    validator.record_exchange(
                        step=exchange["step"],
                        clinic_said=exchange["clinic_said"],
                        we_said=exchange["we_said"]
                    )
                print(f"{Fore.GREEN}✓ Loaded {len(exchanges)} conversation exchanges")
            else:
                print(f"\n{Fore.RED}⚠ No conversation data found at {conversation_file}")
            
            # Validate the flow
            result = validator.validate_flow(
                flow_name=flow_name,
                assertions=assertions,
                expected_steps=expected_steps,
                execution_time=execution_time
            )
            
            # Create reports directory
            os.makedirs("reports", exist_ok=True)
            
            # Export transcript
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_file = f"reports/transcript_{flow_name}_{timestamp}.json"
            validator.export_transcript(transcript_file)
            print(f"\n{Fore.BLUE}Transcript saved: {transcript_file}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return FlowResult(
                flow_name=flow_name,
                success=False,
                steps_completed=0,
                total_steps=expected_steps,
                assertions_passed=0,
                assertions_failed=len(assertions),
                failed_assertions=[f"Flow execution error: {str(e)}"],
                execution_time=execution_time,
                transcript=[],
                error=str(e)
            )
    
    async def run_flows(self, flow_configs: List[Dict[str, Any]], 
                       delay_between_flows: int = 10):
        """
        Run multiple flows sequentially
        
        Args:
            flow_configs: List of flow configuration dictionaries
            delay_between_flows: Seconds to wait between flows
        """
        print(f"\n{Fore.MAGENTA}{'=' * 60}")
        print(f"{Fore.MAGENTA}FLOW TEST SUITE")
        print(f"{Fore.MAGENTA}{'=' * 60}")
        print(f"Total Flows: {len(flow_configs)}")
        print(f"Delay Between Flows: {delay_between_flows}s")
        
        for i, flow_config in enumerate(flow_configs, 1):
            print(f"\n{Fore.CYAN}[{i}/{len(flow_configs)}] Starting flow...")
            
            result = await self.run_flow(flow_config)
            self.results.append(result)
            
            # Print immediate result
            self._print_flow_result(result)
            
            # Wait before next flow (except for last one)
            if i < len(flow_configs):
                print(f"\n{Fore.YELLOW}Waiting {delay_between_flows}s before next flow...")
                await asyncio.sleep(delay_between_flows)
        
        # Print summary
        self.print_summary()
    
    def _print_flow_result(self, result: FlowResult):
        """Print result of a single flow"""
        status_color = Fore.GREEN if result.success else Fore.RED
        status_symbol = "✓" if result.success else "✗"
        
        print(f"\n{status_color}{status_symbol} Flow: {result.flow_name}")
        print(f"  Status: {'PASSED' if result.success else 'FAILED'}")
        print(f"  Steps: {result.steps_completed}/{result.total_steps}")
        print(f"  Assertions: {result.assertions_passed} passed, {result.assertions_failed} failed")
        print(f"  Time: {result.execution_time:.1f}s")
        
        if result.failed_assertions:
            print(f"\n  {Fore.RED}Failed Assertions:")
            for assertion in result.failed_assertions:
                print(f"    - {assertion}")
        
        if result.error:
            print(f"\n  {Fore.RED}Error: {result.error}")
    
    def print_summary(self):
        """Print summary of all flow results"""
        print(f"\n\n{Fore.MAGENTA}{'=' * 60}")
        print(f"{Fore.MAGENTA}TEST SUMMARY")
        print(f"{Fore.MAGENTA}{'=' * 60}")
        
        total_flows = len(self.results)
        passed_flows = sum(1 for r in self.results if r.success)
        failed_flows = total_flows - passed_flows
        
        total_assertions = sum(r.assertions_passed + r.assertions_failed for r in self.results)
        passed_assertions = sum(r.assertions_passed for r in self.results)
        failed_assertions = sum(r.assertions_failed for r in self.results)
        
        total_time = sum(r.execution_time for r in self.results)
        
        # Overall stats
        print(f"\n{Fore.CYAN}Overall Results:")
        print(f"  Total Flows: {total_flows}")
        print(f"  {Fore.GREEN}Passed: {passed_flows}")
        print(f"  {Fore.RED}Failed: {failed_flows}")
        print(f"  Success Rate: {(passed_flows/total_flows*100):.1f}%")
        print(f"\n{Fore.CYAN}Assertions:")
        print(f"  Total: {total_assertions}")
        print(f"  {Fore.GREEN}Passed: {passed_assertions}")
        print(f"  {Fore.RED}Failed: {failed_assertions}")
        print(f"\n{Fore.CYAN}Execution Time: {total_time:.1f}s")
        
        # Individual flow results
        print(f"\n{Fore.CYAN}Flow Results:")
        for result in self.results:
            status_color = Fore.GREEN if result.success else Fore.RED
            status = "PASS" if result.success else "FAIL"
            print(f"  {status_color}[{status}] {result.flow_name} - "
                  f"{result.steps_completed}/{result.total_steps} steps, "
                  f"{result.execution_time:.1f}s")
        
        # Failed flows detail
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            print(f"\n{Fore.RED}Failed Flows Detail:")
            for result in failed_results:
                print(f"\n  {Fore.RED}✗ {result.flow_name}")
                for assertion in result.failed_assertions:
                    print(f"    - {assertion}")
        
        print(f"\n{Fore.MAGENTA}{'=' * 60}\n")
    
    def export_results(self, filename: str = None):
        """Export all results to a JSON file"""
        # Create reports directory
        os.makedirs("reports", exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/flow_test_results_{timestamp}.json"
        
        import json
        from dataclasses import asdict
        
        results_dict = [asdict(r) for r in self.results]
        
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_flows": len(self.results),
                "passed": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "results": results_dict
            }, f, indent=2)
        
        print(f"{Fore.BLUE}Results exported to: {filename}")


# Example usage
if __name__ == "__main__":
    # Define test flows
    test_flows = [
        {
            "name": "Happy Path - New Patient Booking",
            "phone_number": os.getenv("TARGET_PHONE_NUMBER"),
            "expected_steps": 12,
            "timeout": 300,
            "assertions": [
                FlowAssertion(
                    step=1,
                    assertion_type="step_reached",
                    description="Call connected and greeting received"
                ),
                FlowAssertion(
                    step=4,
                    assertion_type="contains",
                    expected_value="january 15",
                    description="Date of birth provided"
                ),
                FlowAssertion(
                    step=6,
                    assertion_type="contains",
                    expected_value="alex kattan",
                    description="Name provided"
                ),
                FlowAssertion(
                    step=10,
                    assertion_type="contains",
                    expected_value="appointment",
                    description="Appointment confirmed"
                ),
                FlowAssertion(
                    step=12,
                    assertion_type="step_reached",
                    description="Call completed successfully"
                ),
            ]
        },
    ]
    
    # Run the tests
    runner = FlowTestRunner()
    asyncio.run(runner.run_flows(test_flows, delay_between_flows=10))
    runner.export_results()
