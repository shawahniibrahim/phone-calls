import audioop

class VoiceActivityDetector:
    """
    Simple Voice Activity Detector based on audio energy levels.
    Helps distinguish speech from background noise.
    """
    
    def __init__(self, energy_threshold=500, speech_frames=10, silence_frames=20):
        """
        Args:
            energy_threshold: Minimum RMS energy to consider as speech
            speech_frames: Number of consecutive speech frames to start speech
            silence_frames: Number of consecutive silence frames to end speech
        """
        self.energy_threshold = energy_threshold
        self.speech_frames_required = speech_frames
        self.silence_frames_required = silence_frames
        
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        self.is_speaking = False
        
    def get_audio_energy(self, audio_chunk: bytes) -> int:
        """
        Calculate RMS (Root Mean Square) energy of audio chunk.
        Higher values = louder audio.
        """
        if len(audio_chunk) == 0:
            return 0
        return audioop.rms(audio_chunk, 2)  # 2 = 16-bit samples
    
    def process_frame(self, audio_chunk: bytes) -> dict:
        """
        Process an audio frame and return speech detection status.
        
        Returns:
            dict with:
                - 'is_speech': bool - Is this frame speech?
                - 'speech_started': bool - Did speech just start?
                - 'speech_ended': bool - Did speech just end?
                - 'energy': int - Audio energy level
        """
        energy = self.get_audio_energy(audio_chunk)
        is_speech_frame = energy > self.energy_threshold
        
        speech_started = False
        speech_ended = False
        
        if is_speech_frame:
            self.speech_frame_count += 1
            self.silence_frame_count = 0
            
            # Start speech if we have enough consecutive speech frames
            if not self.is_speaking and self.speech_frame_count >= self.speech_frames_required:
                self.is_speaking = True
                speech_started = True
                
        else:
            self.silence_frame_count += 1
            self.speech_frame_count = 0
            
            # End speech if we have enough consecutive silence frames
            if self.is_speaking and self.silence_frame_count >= self.silence_frames_required:
                self.is_speaking = False
                speech_ended = True
        
        return {
            'is_speech': is_speech_frame,
            'speech_started': speech_started,
            'speech_ended': speech_ended,
            'is_speaking': self.is_speaking,
            'energy': energy
        }
    
    def reset(self):
        """Reset the detector state."""
        self.speech_frame_count = 0
        self.silence_frame_count = 0
        self.is_speaking = False
