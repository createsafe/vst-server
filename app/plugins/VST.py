from pathlib import Path
from types import MappingProxyType
from typing import Any
from numpy import dtype, float32, ndarray
from pedalboard import load_plugin, VST3Plugin

from plugins.utils import remove_alphabetic, is_alphanumeric

def _condition_value(value):
    """
    Check for trailing units and convert to float if possible.
    """

    # check if string contains both digits and alphabetics
    if is_alphanumeric(value):
        # try removing extraneous alphabetic characters
        value = remove_alphabetic(value)

    # numbers converted to float before being converted to bool or int
    if value.replace(".", "").isnumeric():
        value = float(value)

    return value

class VST:
    """
    A wrapper for loading VST3 plugins and processing audio with them using the pedalboard library
    """

    plugin: VST3Plugin
    default_params: dict[str, Any]
    param_map: dict[str, str]

    def __init__(
        self,
        path: str | Path
    ):
        plugin = load_plugin(str(path))
        assert isinstance(plugin, VST3Plugin)
        self.plugin = plugin
        self.param_map = {param.name: key for key, param in plugin.parameters.items()}  # type: ignore
        # Set default parameters (immutable)
        self.default_params = MappingProxyType({key: getattr(plugin, key) for key in plugin.parameters.keys()})  # type: ignore

        # Set default parameters
        self.default_params = plugin.parameters.copy()  # type: ignore
        self.name2parameter_map = {self.default_params[key]._AudioProcessorParameter__parameter_name: key for key in self.default_params}

    def set_params(self, params: dict[str, Any]) -> None:
        """
        Set the parameters of the plugin.
        params: {"Parameter Name": "value", ...}
        """
        for name in params:
            if name in self.name2parameter_map:
                internal_key = self.name2parameter_map[name]
                value = params[name]

                value = _condition_value(value)

                # cast to parameter type
                value = self.default_params[internal_key].type(value)

                # set plugin attribute using reflexion
                try:
                    setattr(self.plugin, internal_key, value)
                except Exception:
                    print(f"WARNING: could not set parameter \"{internal_key}\" to value \"{value}\".")

    def reset_params(self) -> None:
        """
        Reset the parameters of the plugin to their default values
        """
        key, val = None, None
        try:
            for key, val in self.default_params.items():
                setattr(self.plugin, key, val)
        except Exception:
            print(f"Warning: Could not reset parameter {key} to value {val} in plugin {self.plugin.name}")

    def set_param(self, key: str, val: Any):
        """
        Set a single parameter of the plugin, ensuring it uses the correct parameter name
        """
        # Get the python name of the parameter if we're using the raw name
        self.set_params({key, val})

    async def process_audio(
        self,
        y: ndarray[Any, dtype[float32]],
        sr: int,
        params: dict[str, Any] | None = None,
    ) -> ndarray[Any, dtype[float32]]:
        """
        Process audio with the plugin

        Args:
            y: The audio to process
            sr: The sample rate of the audio

        Raises:
            ValueError: If the plugin fails to process the audio

        Returns:
            The processed audio as a numpy array
        """
        try:
            # Process audio
            y_processed = self.plugin.process(input_array=y, sample_rate=sr, reset=True)  # type: ignore
        except Exception as e:
            raise ValueError("Plugin failed to process audio:", e)
        finally:
            self.reset_params()

        # Return processed audio
        return y_processed
