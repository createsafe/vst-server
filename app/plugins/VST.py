from pathlib import Path
from typing import Any
from numpy import dtype, float32, ndarray
from pedalboard import load_plugin, VST3Plugin, AudioProcessorParameter


class VST:
    """
    A wrapper for loading VST3 plugins and processing audio with them using the pedalboard library
    """

    plugin: VST3Plugin
    default_params: dict[str, AudioProcessorParameter]

    def __init__(
        self,
        path: str | Path,
        params: dict[str, AudioProcessorParameter | Any] | None = None,
    ):
        plugin = load_plugin(str(path))
        assert isinstance(plugin, VST3Plugin)
        self.plugin = plugin

        # Set default parameters
        self.default_params = plugin.parameters.copy()  # type: ignore

        # Add our own default parameters
        if params is not None:
            self.default_params.update(params)

    def set_params(self, params: dict[str, AudioProcessorParameter | Any]) -> None:
        """
        Set the parameters of the plugin
        """
        self.plugin.parameters.update(params)  # type: ignore

    def reset_params(self) -> None:
        """
        Reset the parameters of the plugin to their default values
        """
        self.plugin.parameters.update(self.default_params)  # type: ignore

    async def process_audio(
        self,
        y: ndarray[Any, dtype[float32]],
        sr: int,
        params: dict[str, AudioProcessorParameter | Any] | None = None,
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
            if params is not None:
                self.set_params(params)
            y_processed = self.plugin.process(input_array=y, sample_rate=sr, reset=False)  # type: ignore
        except RuntimeError as e:
            raise ValueError("Plugin failed to process audio:", e)
        finally:
            self.reset_params()

        # Return processed audio
        return y_processed
