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

from config import EFFECT_DEFINITIONS_DIR


async def load_effect_def(filepath: str | Path) -> dict:
    """
    Load effect definition from json file.
    """
    with open(filepath) as json_str:
        effect_def = json.load(json_str)

    return effect_def


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


async def harmony_test_effect(y: ndarray[Any, dtype[float32]], sr: int) -> Tuple[ndarray[Any, dtype[float32]], int]:
    """
    This example applies one effect to autotune the audio, then busses that to a
    second path and sums the results.
    """

    primary_effect_details_filepath = EFFECT_DEFINITIONS_DIR / "c_maj.json"
    secondary_effect_details_filepath = EFFECT_DEFINITIONS_DIR / "c_maj_harm.json"

    primary_details = await load_effect_def(primary_effect_details_filepath)
    secondary_details = await load_effect_def(secondary_effect_details_filepath)

    # apply first effects chain
    primary_chain = primary_details["effectsChain"]
    y, sr = await apply_chain(y, sr, primary_chain)

    # apply harmonizing effects chain
    secondary_chain = secondary_details["effectsChain"]
    y_harm, sr = await apply_chain(y, sr, secondary_chain)

    y += y_harm

    return y, sr


async def test_effect(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    """
    An example effect chain which pitch shifts the audio up by either one or two octaves,
    depending on user setting — i.e. the simple user settings from Discord.

    Generally the settings would either be booleans or maybe 3 values. Keep UX in mind.

    This also shows how we would chain multiple plugins together.

    This is a temporary way to define and run these chains. Ideally we will define entirely in JSON.

    """

    # get effect details
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "test.json"
    effect_details = await load_effect_def(effect_details_filename)

    # apply effect chain to audio
    chain = effect_details["effectsChain"]
    y, sr = await apply_chain(y, sr, chain)

    return y, sr


async def cybernetic_distortion(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "cybernetic_distortion.json"
    effect_details = await load_effect_def(effect_details_filename)

    # apply effect chain to audio
    chain = effect_details["effectsChain"]
    y, sr = await apply_chain(y, sr, chain)

    return y, sr


async def scifi_vibes(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "scifi_vibes.json"
    effect_details = await load_effect_def(effect_details_filename)

    # apply effect chain to audio
    chain = effect_details["effectsChain"]
    y, sr = await apply_chain(y, sr, chain)

    return y, sr


async def glitch_harmonies(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    main_details_filename = EFFECT_DEFINITIONS_DIR / "glitch_harmonies_main.json"
    parallel_details_filename = EFFECT_DEFINITIONS_DIR / "glitch_harmonies_parallel.json"

    main_details = await load_effect_def(main_details_filename)
    parallel_details = await load_effect_def(parallel_details_filename)

    # apply to dry vocal
    main_chain = main_details["effectsChain"]
    y, sr = await apply_chain(y, sr, main_chain)

    # parallel process
    parallel_chain = parallel_details["effectsChain"]
    y_parallel, _ = await apply_chain(y, sr, parallel_chain)

    # sum
    y += y_parallel

    return y_parallel, sr


async def auto_effect(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    # get effect details
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "auto.json"
    effect_details = await load_effect_def(effect_details_filename)

    chain = effect_details["effectsChain"]
    y, sr = await apply_chain(y, sr, chain)

    return y, sr


async def ethereal_layers(y, sr) -> Tuple[ndarray[Any, dtype[float32]], int]:
    # get effect details
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "ethereal_layers.json"
    effect_details = await load_effect_def(effect_details_filename)

    chain = effect_details["effectsChain"]
    y, sr = await apply_chain(y, sr, chain)

    return y, sr


async def elftune(y, sr, user_setting: str, metadata: dict | None) -> Tuple[ndarray[Any, dtype[float32]], int]:
    # get effect details
    effect_details_filename = EFFECT_DEFINITIONS_DIR / "elftune.json"
    effect_details = await load_effect_def(effect_details_filename)

    chain: list[dict[str, Any]] = effect_details["effectsChain"]

    # Handle user setting, updating the correct parameters for the correct plugin(s) in the chain
    settings_plugin_param_updates_list = None
    if user_setting in effect_details["settings"].keys():
        settings_plugin_param_updates_list = effect_details["settings"][user_setting]

    try:
        if settings_plugin_param_updates_list is not None:
            for plugin in chain:
                for plugin_param_updates in settings_plugin_param_updates_list:
                    if plugin_param_updates["pluginPosition"] == plugin["position"]:
                        plugin["parameters"] += plugin_param_updates["parameterUpdates"]
    except Exception as e:
        raise ValueError(f"Error apply user setting: {user_setting} in elftune: {e}")

    # Handle metadata
    key = metadata["key"] if metadata else None
    mode = metadata["mode"] if metadata else None

    try:
        if key is not None and mode is not None:
            scale_param_updates = get_graillon_params_for_key(key, mode)
            chain[0]["parameters"] += scale_param_updates
        else:
            raise ValueError(f"Key and mode must be provided for elftune effect, got key: {key} and mode: {mode}")
    except Exception as e:
        raise ValueError(f"Error applying metadata in elftune: {e}")

    y, sr = await apply_chain(y, sr, chain)

    return y, sr


# effect chains
EFFECT_LIST = {
    "auto": auto_effect,
    "elftune": elftune,
    "cybernetic_distortion": cybernetic_distortion,
    "scifi_vibes": scifi_vibes,
    "glitch_harmonies": glitch_harmonies,
    "ethereal_layers": ethereal_layers,
    # "harmony_test_effect": harmony_test_effect,
    # "test_effect": test_effect,
}


async def process_audio_with_effect(
    y: ndarray[Any, dtype[float32]],
    sr: int,
    effect_name: str,
    user_setting: str | None = None,
    metadata: dict | None = None,
) -> str:
    """
    Process audio with the given effect chain and parameters

    Args:
        y: The audio to process
        sr: The sample rate of the audio
        effect_name: The name of the effect chain to use
        user_setting: The (optional) user setting for the effect
        metadata: Metadata about the audio (e.g. key, mode)
    """
    # Mono to stereo if necessary
    try:
        y = np.vstack((y, y)) if y.shape[0] != 2 else y
    except Exception as e:
        print(e)
        raise ValueError("Error converting mono to stereo.")

    # Get effect
    if (effect := EFFECT_LIST.get(effect_name)) is None:
        raise ValueError(f"{effect_name} not found.")

    # Process audio with effect
    try:
        if effect_name == "elftune":
            y, sr = await effect(y, sr, user_setting, metadata)
        else:
            y, sr = await effect(y, sr)
    except Exception:
        raise ValueError(f"Failed to process audio with {effect_name}")

    # Return processed audio as base64 string
    try:
        y_bytes = io.BytesIO()
        sf.write(y_bytes, y.T, sr, format="WAV", subtype="PCM_16")
        y_bytes.seek(0)
        base64_encoded_audio = base64.b64encode(y_bytes.getvalue()).decode("utf-8")

        sf.write(f"{effect_name}_output.wav", y.T, sr)

        return base64_encoded_audio
    except Exception:
        raise ValueError("Failed to encode processed audio")


def get_graillon_params_for_key(key: str, mode: str) -> list:
    """
    Converts key and mode strings into a dictionary settings for
    the graillon2 pitch autotuning plugin.

    To be used within apply_chain to modify parameters of graillon2 vst.

    ex: key="C", mode="minor"
    """
    pitches = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    modes = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 9, 10]}

    # reduce pitch class to index
    pitch_index = pitches.index(key)
    # circular shift to put pitch_class in position 0
    pitches = np.roll(pitches, -pitch_index)

    if mode in modes:
        scale_idxs = modes[mode]
        scale = pitches[scale_idxs]

        # generate parameters for graillon2
        parameters = list()
        for pitch in pitches:
            key = "Allow " + pitch
            value = 1.0 if pitch in scale else 0.0
            parameters.append({"name": key,
                               "value": str(value)})
        return parameters
    else:
        raise ValueError(f"Failed to find scale for mode={mode}")
