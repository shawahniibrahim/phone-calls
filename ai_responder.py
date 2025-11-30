from llm_client import LLMClient
from conversation_flow import CONVERSATION_FLOW, SYSTEM_PROMPT

class AIResponder:
    """
    Generates intelligent responses based on what the clinic AI says.
    Uses the conversation flow as guidance but allows natural variation.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.current_step = 0
    
    async def generate_response(self, clinic_said: str) -> str:
        """
        Generate an appropriate response based on what the clinic said.
        
        Args:
            clinic_said: What the clinic AI just said
            
        Returns:
            str: What we should say back
        """
        # Add what the clinic said to history
        self.conversation_history.append({
            "role": "user",
            "content": f"Clinic receptionist: {clinic_said}"
        })
        
        # Get the current step guidance (if available)
        guidance = ""
        if self.current_step < len(CONVERSATION_FLOW):
            step = CONVERSATION_FLOW[self.current_step]
            guidance = f"\n\nCurrent step guidance:\n- They might be: {step['expect']}\n- You should: {step['respond_with']}\n- Example: {step['example']}"
        
        # Create the prompt for generating response
        prompt = f"""Based on what the clinic receptionist just said, generate a brief, natural response.

{guidance}

Remember:
- Keep it conversational and natural (don't use the exact example wording)
- Be brief (1-2 sentences max)
- Only provide information if they ask for it
- Be polite and friendly

Generate ONLY your response, nothing else."""

        self.conversation_history.append({
            "role": "system",
            "content": prompt
        })
        
        # Generate response using GPT
        response = await self.llm_client.generate_response(self.conversation_history)
        
        # Add our response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Move to next step
        self.current_step += 1
        
        return response
    
    def reset(self):
        """Reset the conversation state."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.current_step = 0
