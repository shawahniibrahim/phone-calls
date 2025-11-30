import io
import wave
import os
import base64
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
