import audioop
import base64

class AudioProcessor:
    @staticmethod
    def mulaw_to_pcm(mulaw_data: bytes) -> bytes:
        """
        Convert 8000Hz Mulaw (Twilio) to 8000Hz PCM (16-bit).
        """
        return audioop.ulaw2lin(mulaw_data, 2)

    @staticmethod
    def pcm_to_mulaw(pcm_data: bytes) -> bytes:
        """
        Convert 8000Hz PCM (16-bit) to 8000Hz Mulaw (Twilio).
        """
        return audioop.lin2ulaw(pcm_data, 2)

    @staticmethod
    def resample_pcm(pcm_data: bytes, in_rate: int, out_rate: int) -> bytes:
        """
        Resample PCM data.
        """
        if in_rate == out_rate:
            return pcm_data
        converted, _ = audioop.ratecv(pcm_data, 2, 1, in_rate, out_rate, None)
        return converted
