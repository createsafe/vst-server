from typing import BinaryIO
from pedalboard.io import AudioFile


async def load_audio(file_bytes: BinaryIO, max_duration: int = 300):
    with AudioFile(file_bytes) as audio_file:
        sr = int(audio_file.samplerate)
        y = audio_file.read(sr * max_duration)
        duration = y.shape[1] / sr
        did_truncate = audio_file.frames > sr * max_duration

    return y, sr, duration, did_truncate
