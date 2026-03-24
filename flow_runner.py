# Flow Test Runner
# Executes multiple conversation flows sequentially and reports results

import asyncio
import json
import time
from typing import List, Dict, Any
from datetime import datetime
from colorama import init, Fore, Style
from flow_validator import FlowValidator, FlowAssertion, FlowResult
from call_manager import CallManager
import os
from dotenv import load_dotenv
from reporting import write_call_report

# Initialize colorama for colored terminal output
init(autoreset=True)

load_dotenv()
TERMINAL_CALL_STATUSES = {
    "busy",
    "canceled",
    "completed",
    "failed",
    "no-answer",
}

class FlowTestRunner:
    """Runs multiple conversation flows and validates results"""
    
    def __init__(self):
        self.results: List[FlowResult] = []
        self.call_manager = CallManager()

    async def _wait_for_call_completion(
        self,
        call_sid: str,
        conversation_file: str,
        expected_steps: int,
        timeout: int,
        poll_interval: int = 2,
    ) -> tuple[str, bool]:
        """Stop waiting once Twilio reports a terminal state or the transcript reaches the expected steps."""
        deadline = time.time() + timeout
        last_status = "queued"

        while time.time() < deadline:
            try:
                status = self.call_manager.get_call_status(call_sid)
                if status != last_status:
                    print(f"{Fore.BLUE}Call status: {status}")
                    last_status = status
            except Exception as exc:
                print(f"{Fore.YELLOW}Warning: couldn't fetch call status yet: {exc}")

            exchanges = self._load_exchanges(conversation_file)
            max_step_reached = self._max_step_reached(exchanges)
            if max_step_reached >= expected_steps:
                print(f"{Fore.GREEN}✓ Expected step {expected_steps} reached, finishing early")
                await self._wait_for_file_flush(conversation_file)
                last_status = await self._refresh_call_status(call_sid, last_status)
                return last_status, False

            if last_status in TERMINAL_CALL_STATUSES:
                print(f"{Fore.GREEN}✓ Call reached terminal status: {last_status}")
                await self._wait_for_file_flush(conversation_file)
                return last_status, False

            await asyncio.sleep(poll_interval)

        print(f"{Fore.YELLOW}Timeout reached after {timeout}s")
        await self._wait_for_file_flush(conversation_file)
        return last_status, True

    async def _refresh_call_status(
        self,
        call_sid: str,
        current_status: str,
        grace_seconds: int = 8,
        poll_interval: int = 1,
    ) -> str:
        """Give Twilio a brief chance to move from in-progress to a terminal state."""
        status = current_status
        deadline = time.time() + grace_seconds

        while time.time() < deadline and status not in TERMINAL_CALL_STATUSES:
            await asyncio.sleep(poll_interval)
            try:
                latest_status = self.call_manager.get_call_status(call_sid)
                if latest_status != status:
                    print(f"{Fore.BLUE}Final call status: {latest_status}")
                status = latest_status
            except Exception as exc:
                print(f"{Fore.YELLOW}Warning: couldn't refresh final call status: {exc}")

        return status

    async def _wait_for_file_flush(self, conversation_file: str, grace_seconds: int = 5):
        """Give the server a brief chance to write artifacts after the call ends."""
        for _ in range(grace_seconds):
            if os.path.exists(conversation_file):
                return
            await asyncio.sleep(1)

    def _load_exchanges(self, conversation_file: str) -> List[Dict[str, Any]]:
        if not os.path.exists(conversation_file):
            return []
        try:
            with open(conversation_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _max_step_reached(self, exchanges: List[Dict[str, Any]]) -> int:
        if not exchanges:
            return 0
        return max(int(exchange.get("step", 0)) for exchange in exchanges)

    def _recording_path_for_call(self, call_sid: str) -> str | None:
        if not call_sid:
            return None

        matching_files = []
        for recordings_dir in ("reports/recordings", "recordings"):
            if not os.path.isdir(recordings_dir):
                continue
            for filename in os.listdir(recordings_dir):
                if call_sid in filename and filename.endswith(".wav"):
                    matching_files.append(os.path.join(recordings_dir, filename))

        if matching_files:
            return max(matching_files, key=os.path.getmtime)
        return None

    def _build_result(
        self,
        flow_name: str,
        flow_config: Dict[str, Any],
        validator: FlowValidator,
        assertions: List[FlowAssertion],
        expected_steps: int,
        execution_time: float,
        *,
        call_sid: str | None,
        call_status: str | None,
        conversation_file: str | None,
        recording_file: str | None,
        timed_out: bool,
        error: str | None = None,
    ) -> FlowResult:
        result = validator.validate_flow(
            flow_name=flow_name,
            assertions=assertions,
            expected_steps=expected_steps,
            execution_time=execution_time,
        )
        result.call_sid = call_sid
        result.call_status = call_status
        result.conversation_file = conversation_file if conversation_file and os.path.exists(conversation_file) else None
        result.recording_file = recording_file
        result.timed_out = timed_out
        if error:
            result.success = False
            result.error = error
            if not result.failed_assertions:
                result.failed_assertions.append(error)
        return result

    def _collect_step_assertions(self, step: Dict[str, Any]) -> List[FlowAssertion]:
        assertions: List[FlowAssertion] = []

        def extend_assertions(raw_assertions, default_target: str | None = None):
            for assertion_dict in raw_assertions:
                when = assertion_dict.get("when")
                if when is None:
                    when = assertion_dict.get("assert_on", "current_exchange")
                when = str(when)
                exchange_offset = assertion_dict.get("exchange_offset")
                if exchange_offset is None:
                    exchange_offset = 1 if when in {"next", "next_exchange"} else 0
                assertions.append(
                    FlowAssertion(
                        step=step["step"],
                        assertion_type=str(assertion_dict["type"]),
                        expected_value=assertion_dict.get("value"),
                        description=assertion_dict["description"],
                        target=str(assertion_dict.get("target", default_target or "either")),
                        exchange_offset=exchange_offset,
                    )
                )

        extend_assertions(step.get("assertions", []))
        extend_assertions(step.get("clinic_assertions", []), default_target="clinic")
        extend_assertions(step.get("our_assertions", []), default_target="ours")
        return assertions

    def _write_result_artifacts(
        self,
        result: FlowResult,
        flow_config: Dict[str, Any],
        validator: FlowValidator,
        flow_type: str,
    ) -> FlowResult:
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_flow_type = flow_type.replace("/", "_")
        call_token = result.call_sid or "unknown"
        transcript_file = f"reports/transcript_{safe_flow_type}_{call_token}_{timestamp}.json"
        validator.export_transcript(transcript_file)
        result.transcript_file = transcript_file
        print(f"\n{Fore.BLUE}Transcript saved: {transcript_file}")

        report_json, report_html, index_html = write_call_report(result, flow_config)
        result.report_json = report_json
        result.report_html = report_html
        print(f"{Fore.BLUE}Call report saved: {report_html}")
        print(f"{Fore.BLUE}Report index: {index_html}")
        return result
        
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
        flow_type = flow_config.get("flow_id") or flow_config.get("flow_type", "booking")
        timeout = flow_config.get("timeout", 300)  # 5 minutes default
        call_sid = None
        call_status = None
        conversation_file = None
        recording_file = None
        timed_out = False
        
        # Extract assertions from steps
        from flow_validator import FlowAssertion
        steps = flow_config.get("steps", [])
        expected_steps = len(steps)
        assertions = []
        
        for step in steps:
            assertions.extend(self._collect_step_assertions(step))
        
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
            call_sid = self.call_manager.make_call(phone_number, flow_type=flow_type)
            print(f"{Fore.GREEN}✓ Call initiated: {call_sid}")
            conversation_file = f"conversations/conversation_{call_sid}.json"
            
            # Wait for call to complete
            print(f"\n{Fore.YELLOW}Monitoring call progress...")
            call_status, timed_out = await self._wait_for_call_completion(
                call_sid,
                conversation_file,
                expected_steps,
                timeout,
            )
            
            execution_time = time.time() - start_time
            
            # Load conversation exchanges from file
            exchanges = self._load_exchanges(conversation_file)
            if exchanges:
                print(f"\n{Fore.BLUE}Loading conversation data from {conversation_file}...")
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

            recording_file = self._recording_path_for_call(call_sid)
            result = self._build_result(
                flow_name,
                flow_config,
                validator,
                assertions,
                expected_steps,
                execution_time,
                call_sid=call_sid,
                call_status=call_status,
                conversation_file=conversation_file,
                recording_file=recording_file,
                timed_out=timed_out,
            )
            return self._write_result_artifacts(result, flow_config, validator, flow_type)
            
        except Exception as e:
            execution_time = time.time() - start_time
            if conversation_file:
                exchanges = self._load_exchanges(conversation_file)
                for exchange in exchanges:
                    validator.record_exchange(
                        step=exchange["step"],
                        clinic_said=exchange["clinic_said"],
                        we_said=exchange["we_said"],
                    )
            recording_file = self._recording_path_for_call(call_sid or "")
            result = self._build_result(
                flow_name=flow_name,
                flow_config=flow_config,
                validator=validator,
                assertions=assertions,
                expected_steps=expected_steps,
                execution_time=execution_time,
                call_sid=call_sid,
                call_status=call_status,
                conversation_file=conversation_file,
                recording_file=recording_file,
                timed_out=timed_out,
                error=f"Flow execution error: {str(e)}",
            )
            return self._write_result_artifacts(result, flow_config, validator, flow_type)
    
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
        if result.report_html:
            print(f"\n  Report: {result.report_html}")
    
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
