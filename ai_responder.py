from llm_client import LLMClient
from conversation_flow import AVAILABLE_FLOWS, SYSTEM_PROMPTS, CONVERSATION_FLOW, SYSTEM_PROMPT


class AIResponder:
    """
    Generates intelligent responses based on what the clinic AI says.
    Uses LLM judgment to choose the best business flow step on each turn
    instead of blindly advancing after every reply.
    """

    def __init__(self, flow_type: str = "booking"):
        self.llm_client = LLMClient()
        self.flow_type = flow_type
        self.flow = AVAILABLE_FLOWS.get(flow_type, CONVERSATION_FLOW)
        self.system_prompt = SYSTEM_PROMPTS.get(flow_type, SYSTEM_PROMPT)
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        self.exchange_history = []
        self.next_expected_step_index = 0
        self.last_selected_step_index = 0
        self.last_step_reason = ""
        self.last_step_confidence = ""

    def _next_expected_step_number(self) -> int:
        if not self.flow:
            return 1
        return min(self.next_expected_step_index + 1, len(self.flow))

    async def _select_step(self, clinic_said: str) -> int:
        if not self.flow:
            self.last_step_reason = "Fallback: no flow loaded"
            self.last_step_confidence = "low"
            return 0

        selection = await self.llm_client.choose_flow_step(
            clinic_said=clinic_said,
            flow_steps=self.flow,
            next_expected_step=self._next_expected_step_number(),
            recent_exchanges=self.exchange_history,
        )
        self.last_step_reason = selection.get("reason", "")
        self.last_step_confidence = selection.get("confidence", "")
        return max(0, min(selection["selected_step"] - 1, len(self.flow) - 1))

    async def generate_response(self, clinic_said: str) -> str:
        """
        Generate an appropriate response based on what the clinic said.
        """
        selected_step_index = await self._select_step(clinic_said)
        self.last_selected_step_index = selected_step_index
        step = self.flow[selected_step_index] if selected_step_index < len(self.flow) else None

        self.conversation_history.append(
            {"role": "user", "content": f"Clinic receptionist: {clinic_said}"}
        )

        guidance = ""
        if step:
            guidance = (
                f"\n\nCurrent business step: {selected_step_index + 1}\n"
                f"- They might be: {step['expect']}\n"
                f"- You should: {step['respond_with']}\n"
                f"- Example: {step['example']}"
            )

        prompt = f"""Based on what the clinic receptionist just said, generate a brief, natural response.

{guidance}

Judgment note:
- The selected business step is {selected_step_index + 1}.
- If the clinic is repeating itself or asking whether you're still there, briefly acknowledge that and still answer for the selected business step.

Remember:
- Keep it conversational and natural (don't use the exact example wording)
- Be brief (1-2 sentences max)
- Only provide information if they ask for it
- Be polite and friendly

Generate ONLY your response, nothing else."""

        response = await self.llm_client.generate_response(
            self.conversation_history + [{"role": "system", "content": prompt}]
        )

        self.conversation_history.append({"role": "assistant", "content": response})
        self.exchange_history.append(
            {
                "step": selected_step_index + 1,
                "clinic_said": clinic_said,
                "we_said": response,
            }
        )
        self.next_expected_step_index = max(
            self.next_expected_step_index,
            min(selected_step_index + 1, len(self.flow)),
        )

        return response

    @property
    def last_step_number(self) -> int:
        return self.last_selected_step_index + 1

    @property
    def last_flow_step(self):
        if not self.flow:
            return None
        if 0 <= self.last_selected_step_index < len(self.flow):
            return self.flow[self.last_selected_step_index]
        return None

    def reset(self):
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        self.exchange_history = []
        self.next_expected_step_index = 0
        self.last_selected_step_index = 0
        self.last_step_reason = ""
        self.last_step_confidence = ""
