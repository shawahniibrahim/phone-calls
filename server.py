import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request, Response
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


@app.post("/voice")
async def handle_voice_webhook(request: Request):
    """
    Twilio hits this endpoint when the call connects.
    We return TwiML to tell Twilio to connect to our Media Stream.
    """
    server_url = os.getenv("SERVER_URL")
    if not server_url:
        return Response(content="SERVER_URL not set", status_code=500)

    # Get form data from Twilio
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "")

    # Extract the host from the SERVER_URL (remove https://)
    host = server_url.replace("https://", "").replace("http://", "")

    response = VoiceResponse()
    connect = Connect()
    # Pass call_sid as parameter to WebSocket
    connect.stream(url=f"wss://{host}/media-stream?call_sid={call_sid}")
    response.append(connect)

    return Response(content=str(response), media_type="application/xml")


from audio_processor import AudioProcessor
from llm_client import LLMClient
from ai_responder import AIResponder
from vad_detector import VoiceActivityDetector
from conversation_flow import CONVERSATION_FLOW
import wave
from datetime import datetime


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()

    # Get call_sid from query parameters
    call_sid = websocket.query_params.get("call_sid", "unknown")

    print("=" * 60)
    print("Media Stream Connected - Call Started")
    print("=" * 60)
    print(f"Call SID: {call_sid}")
    print("\n[LISTENING] Waiting for the clinic AI to speak...")

    llm_client = LLMClient()
    # TODO: Get flow_type from call parameters in future
    ai_responder = AIResponder(flow_type="leave_message")  # Match conversation_flow.py
    vad = VoiceActivityDetector(
        energy_threshold=500,  # Adjust this if needed (higher = less sensitive)
        speech_frames=10,  # 10 frames (~1 second) to start speech
        silence_frames=30,  # 30 frames (~3 seconds) to end speech
    )

    incoming_audio_buffer = bytearray()
    full_call_recording = bytearray()  # Records both sides
    stream_sid = None
    conversation_turn = 0
    conversation_exchanges = []  # Store conversation for validation
    audio_chunks_received = 0
    speech_segments = []
    current_segment = bytearray()
    last_high_energy_time = None
    currently_speaking = False
    waiting_for_response = False  # Flag to prevent speaking until we hear back

    import time

    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                data = json.loads(message)

                if data["event"] == "start":
                    stream_sid = data["start"]["streamSid"]
                    print(f"Stream started: {stream_sid}")

                elif data["event"] == "media":
                    # Receive incoming audio from the clinic AI
                    payload = data["media"]["payload"]
                    chunk = base64.b64decode(payload)
                    pcm_chunk = AudioProcessor.mulaw_to_pcm(chunk)

                    # Add to recording buffers
                    incoming_audio_buffer.extend(pcm_chunk)
                    full_call_recording.extend(pcm_chunk)
                    audio_chunks_received += 1

                    # Calculate audio energy
                    energy = vad.get_audio_energy(pcm_chunk)
                    current_time = time.time()

                    # Track when we last heard high energy (speech)
                    if energy > vad.energy_threshold:
                        last_high_energy_time = current_time
                        if not currently_speaking:
                            currently_speaking = True
                            waiting_for_response = (
                                False  # They're speaking, so we can respond after
                            )
                            print(
                                f"\n[SPEECH DETECTED] Clinic AI speaking (energy: {energy})"
                            )
                        current_segment.extend(pcm_chunk)
                    else:
                        # Low energy - could be silence or background noise
                        if currently_speaking:
                            current_segment.extend(
                                pcm_chunk
                            )  # Keep collecting for a bit

                            # Check if 2.5 seconds have passed since last high energy
                            if (
                                last_high_energy_time
                                and (current_time - last_high_energy_time) >= 2.5
                            ):
                                print(
                                    f"[SILENCE DETECTED] 2.5 seconds of silence/noise detected"
                                )
                                currently_speaking = False

                                # Process the speech segment only if we're not waiting for a response
                                if (
                                    len(current_segment) > 16000
                                    and not waiting_for_response
                                ):  # At least 1 second
                                    print(
                                        f"\n[CLINIC AI] Transcribing {len(current_segment)} bytes..."
                                    )
                                    clinic_text = await llm_client.transcribe_audio(
                                        bytes(current_segment)
                                    )
                                    print(f"[CLINIC AI] Said: {clinic_text}")

                                    # Check if conversation is ending
                                    if any(
                                        word in clinic_text.lower()
                                        for word in [
                                            "goodbye",
                                            "bye",
                                            "have a great day",
                                            "take care",
                                        ]
                                    ):
                                        print(
                                            f"\n[CONVERSATION ENDING] Detected goodbye, will end after response"
                                        )

                                    # Generate intelligent response based on what they said
                                    print(f"\n[AI] Generating intelligent response...")
                                    our_response = await ai_responder.generate_response(
                                        clinic_text
                                    )
                                    print(f"[US] Saying: {our_response}")

                                    # Record this exchange for validation
                                    conversation_exchanges.append(
                                        {
                                            "step": conversation_turn + 1,
                                            "clinic_said": clinic_text,
                                            "we_said": our_response,
                                            "timestamp": datetime.now().isoformat(),
                                        }
                                    )

                                    # Convert to audio and send
                                    response_audio = await llm_client.text_to_speech(
                                        our_response
                                    )

                                    # Add our audio to the full recording too
                                    full_call_recording.extend(response_audio)

                                    await send_audio_to_twilio(
                                        websocket, response_audio, stream_sid
                                    )

                                    # Check if we should end the call
                                    if any(
                                        word in our_response.lower()
                                        for word in ["goodbye", "bye", "take care"]
                                    ):
                                        print(
                                            f"\n[ENDING CALL] We said goodbye, ending call..."
                                        )
                                        # Send hangup command to Twilio
                                        await hangup_call(websocket, stream_sid)
                                        break

                                    # Check if we've reached the hangup step in the flow
                                    if conversation_turn < len(CONVERSATION_FLOW):
                                        current_flow_step = CONVERSATION_FLOW[
                                            conversation_turn
                                        ]
                                        if current_flow_step.get("action") == "hangup":
                                            print(
                                                f"\n[FLOW COMPLETE] Reached hangup step, ending call..."
                                            )
                                            await hangup_call(websocket, stream_sid)
                                            break

                                    # Now we're waiting for them to respond
                                    waiting_for_response = True
                                    print(
                                        "[LISTENING] Waiting for clinic AI response..."
                                    )
                                    conversation_turn += 1
                                elif waiting_for_response:
                                    print(
                                        f"[SKIPPED] Not responding - waiting for clinic AI to speak first"
                                    )

                                current_segment.clear()
                                last_high_energy_time = None

                    # Print progress every 100 chunks
                    if audio_chunks_received % 100 == 0:
                        status = "SPEAKING" if currently_speaking else "SILENCE/NOISE"
                        print(
                            f"[DEBUG] Chunks: {audio_chunks_received}, Energy: {energy}, Status: {status}"
                        )

                elif data["event"] == "stop":
                    print("Stream stopped by Twilio")
                    break

            except asyncio.TimeoutError:
                # Just continue waiting for more audio
                continue

    except websockets.exceptions.ConnectionClosed:
        print("\n" + "=" * 60)
        print("Connection closed - Call Ended")
        print("=" * 60)
    except Exception as e:
        print(f"\nError in media stream: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Create output directories if they don't exist
        os.makedirs("recordings", exist_ok=True)
        os.makedirs("conversations", exist_ok=True)

        # Save the full call recording (both sides)
        if len(full_call_recording) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/full_call_{timestamp}.wav"

            print(f"\n[SAVING] Full call recording to {filename}...")
            with wave.open(filename, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(8000)  # 8kHz
                wav_file.writeframes(bytes(full_call_recording))

            print(f"[SAVED] {len(full_call_recording)} bytes saved to {filename}")
            print(f"[INFO] Duration: ~{len(full_call_recording) / 16000:.1f} seconds")
            print(f"[INFO] This recording includes BOTH sides of the conversation")

        # Save conversation exchanges for validation (use call_sid for consistency)
        if call_sid and len(conversation_exchanges) > 0:
            exchanges_filename = f"conversations/conversation_{call_sid}.json"
            print(f"\n[SAVING] Conversation exchanges to {exchanges_filename}...")
            with open(exchanges_filename, "w") as f:
                json.dump(conversation_exchanges, f, indent=2)
            print(
                f"[SAVED] {len(conversation_exchanges)} exchanges saved for validation"
            )


async def send_audio_to_twilio(websocket: WebSocket, pcm_audio: bytes, stream_sid: str):
    """
    Sends PCM audio to Twilio by converting to mulaw and chunking.
    Audio is sent on the 'outbound' track so it goes TO the call.
    """
    print(f"[DEBUG] Sending {len(pcm_audio)} bytes of PCM audio to Twilio...")

    # Convert PCM to Mulaw
    mulaw_audio = AudioProcessor.pcm_to_mulaw(pcm_audio)
    print(f"[DEBUG] Converted to {len(mulaw_audio)} bytes of mulaw")

    # Twilio expects chunks of 20ms (160 bytes of mulaw at 8kHz)
    chunk_size = 160
    chunks_sent = 0

    for i in range(0, len(mulaw_audio), chunk_size):
        chunk = mulaw_audio[i : i + chunk_size]
        payload = base64.b64encode(chunk).decode("utf-8")

        media_message = {
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "track": "outbound",  # CRITICAL: Send audio TO the call (not FROM)
                "payload": payload,
            },
        }
        await websocket.send_text(json.dumps(media_message))
        chunks_sent += 1

        # Small delay to simulate real-time playback
        await asyncio.sleep(0.02)  # 20ms

    print(f"[DEBUG] Sent {chunks_sent} audio chunks on 'outbound' track to Twilio")

    # Send a mark event to confirm audio was sent
    mark_message = {
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {"name": "audio_complete"},
    }
    await websocket.send_text(json.dumps(mark_message))
    print(f"[DEBUG] Audio transmission complete")


async def hangup_call(websocket: WebSocket, stream_sid: str):
    """
    Sends a stop event to Twilio to hang up the call gracefully.
    """
    print(f"[HANGUP] Sending stop event to end call...")

    stop_message = {"event": "stop", "streamSid": stream_sid}

    try:
        await websocket.send_text(json.dumps(stop_message))
        print(f"[HANGUP] Stop event sent successfully")
        await asyncio.sleep(0.5)  # Give time for the message to be processed
    except Exception as e:
        print(f"[HANGUP] Error sending stop event: {e}")
