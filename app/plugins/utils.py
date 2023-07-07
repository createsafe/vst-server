import json
import re
from plugins.plugins import VST_LIST


async def get_plugin_parameters(plugin_name: str) -> str:
    """
    List all parameters for a given plugin
    """

    if (vst := VST_LIST.get(plugin_name)) is None:
        raise ValueError(f"Plugin {plugin_name} not found. Valid plugins: {', '.join(VST_LIST.keys())}")

    params = []
    for _, param in vst.plugin.parameters.items():  # type: ignore
        param_str = str(param)
        param_dict = {
            "name": param_str.split(' name="')[1].split('"')[0],
            "raw_value": param_str.split(" raw_value=")[1].split()[0],
            "value": param_str.split(" value=")[1].split()[0],
        }
        params.append(param_dict)

    return json.dumps(params, indent=4)


def is_alphanumeric(input):
    return any(c.isalpha() for c in input) and any(c.isdigit() for c in input)


def is_alphabetic(input):
    return any(c.isalpha() for c in input)


def remove_alphabetic(input: str) -> str:
    return re.sub("[^0-9.]", "", input)


def is_number(input):
    try:
        float(input)
        return True
    except ValueError:
        return False
