import json
import base64
import io
import soundfile as sf
import numpy as np
from pathlib import Path
from typing import Any, Tuple
from numpy import dtype, float32, ndarray

from plugins.plugins import VST_LIST
from plugins.utils import remove_alphabetic, is_alphanumeric


async def apply_chain(
    y: ndarray[Any, dtype[float32]],
    sr: int,
    chain: list,
) -> Tuple[ndarray[Any, dtype[float32]], int]:
    # iterate over effects in chain and apply to audio
    for vst_details in chain:
        vst_name = vst_details["plugin"]
        vst = VST_LIST[vst_name]

        daw_params = vst_details["parameters"]

        daw_params = {param["name"]: param["value"] for param in daw_params}

        default_params = vst.default_params
        daw2python_keys = {default_params[key]._AudioProcessorParameter__parameter_name: key for key in default_params}

        # pack preset params
        params = default_params
        for daw_key in daw_params:
            if daw_key in daw2python_keys:
                python_key = daw2python_keys[daw_key]
                value = daw_params[daw_key]

                # check if string contains both digits and alphabetics
                if is_alphanumeric(value):
                    # try removing extraneous alphabetic characters
                    value = remove_alphabetic(value)

                # numbers converted to float before being converted to bool or int
                if value.replace(".", "").isnumeric():
                    value = float(value)

                value = params[python_key].type(value)

                print(f"{daw_key}: {value}")
                setattr(vst.plugin, python_key, value)

        y = await vst.process_audio(y, sr, params)

    return y, sr


async def process_audio_with_effect_chain(
    y: ndarray[Any, dtype[float32]],
    sr: int,
    chain: dict
) -> str:
    """
    Process audio with the given effect chain and parameters

    Args:
        y: The audio to process
        sr: The sample rate of the audio
        chain: The dictionary describing the VSTs used and the parameters to be applied.
    """
    # Mono to stereo if necessary
    try:
        y = np.vstack((y, y)) if y.shape[0] != 2 else y
    except Exception as e:
        print(e)
        raise ValueError("Error converting mono to stereo.")

    try: 
        y_output, sr = await apply_chain(y, sr, chain)
    except Exception:
        raise ValueError(f"Failed to apply effects chain")

    # Return processed audio as base64 string
    try:
        y_bytes = io.BytesIO()
        sf.write(y_bytes, y_output.T, sr, format="WAV", subtype="PCM_16")
        y_bytes.seek(0)
        base64_encoded_audio = base64.b64encode(y_bytes.getvalue()).decode("utf-8")

        return base64_encoded_audio
    except Exception:
        raise ValueError("Failed to encode processed audio")
