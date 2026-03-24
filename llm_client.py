import io
import wave
import os
import base64
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribes audio bytes using OpenAI Whisper.
        Wraps raw PCM data in a WAV container before sending to API.
        """
        if not audio_bytes:
            return ""

        # Wrap PCM in WAV container
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)      # Mono
            wav_file.setsampwidth(2)      # 16-bit
            wav_file.setframerate(8000)   # 8kHz (Twilio standard)
            wav_file.writeframes(audio_bytes)
            
        buffer.seek(0)
        buffer.name = "audio.wav" # Filename required by OpenAI API

        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer
        )
        return response.text

    async def generate_response(self, conversation_history: list) -> str:
        """
        Generates a text response based on the conversation history.
        """
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history
        )
        return response.choices[0].message.content

    async def choose_flow_step(
        self,
        *,
        clinic_said: str,
        flow_steps: list[dict],
        next_expected_step: int,
        recent_exchanges: list[dict],
    ) -> dict:
        """
        Uses the model to choose which business flow step best matches the
        clinic's latest utterance.
        """
        steps_summary = []
        for index, step in enumerate(flow_steps, start=1):
            action = f", action={step.get('action')}" if step.get("action") else ""
            steps_summary.append(
                f"{index}. expect={step['expect']} | respond_with={step['respond_with']} | "
                f"example={step['example']}{action}"
            )

        history_summary = []
        for exchange in recent_exchanges[-6:]:
            history_summary.append(
                f"- Step {exchange['step']}: clinic='{exchange['clinic_said']}' | caller='{exchange['we_said']}'"
            )

        prompt = f"""
You are choosing which business flow step the caller should respond with right now.

Important rules:
- Flow steps are business steps, not raw transcript turns.
- The clinic may repeat a question, ask "are you still there", or restate something already asked.
- Do not advance just because the caller already answered once.
- If the clinic repeats a prior request, choose that same step again.
- If the clinic says a generic keepalive without introducing a new request, use the next expected unfinished step.
- You may choose an earlier step than the next expected one if the clinic is clearly repeating or reconfirming old information.
- Choose exactly one step number from the provided list.

Next expected unfinished step: {next_expected_step}

Flow steps:
{chr(10).join(steps_summary)}

Recent exchanges:
{chr(10).join(history_summary) if history_summary else "- None yet"}

Latest clinic utterance:
{clinic_said}

Return JSON only in this shape:
{{"selected_step": 1, "reason": "short reason", "confidence": "low|medium|high"}}
"""

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.choices[0].message.content
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return {
                "selected_step": next_expected_step,
                "reason": "Fallback: step judge returned invalid JSON",
                "confidence": "low",
            }

        selected_step = parsed.get("selected_step", next_expected_step)
        try:
            selected_step = int(selected_step)
        except (TypeError, ValueError):
            selected_step = next_expected_step

        selected_step = max(1, min(selected_step, len(flow_steps)))
        return {
            "selected_step": selected_step,
            "reason": str(parsed.get("reason", "")).strip(),
            "confidence": str(parsed.get("confidence", "")).strip().lower() or "unknown",
        }

    async def validate_response(self, actual_response: str, expected_context: str) -> bool:
        """
        Validates if the actual response matches the expected context.
        Returns True if it matches, False otherwise.
        """
        prompt = f"""
        You are a test automation judge.
        Actual Response: "{actual_response}"
        Expected Context/Rule: "{expected_context}"
        
        Does the Actual Response satisfy the Expected Context? 
        Reply ONLY with 'YES' or 'NO'.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content.strip().upper()
        return "YES" in content

    async def text_to_speech(self, text: str) -> bytes:
        """
        Converts text to speech using OpenAI TTS.
        Returns PCM audio at 8kHz (Twilio compatible).
        """
        from audio_processor import AudioProcessor
        
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="pcm"  # Returns 24kHz 16-bit PCM
        )
        
        # OpenAI returns 24kHz PCM, but Twilio needs 8kHz
        pcm_24khz = response.content
        pcm_8khz = AudioProcessor.resample_pcm(pcm_24khz, 24000, 8000)
        
        return pcm_8khz
