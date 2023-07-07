import os
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "vsts"
EFFECT_DEFINITIONS_DIR = Path(__file__).parent.parent.parent / "shared/effects/chains"

if os.uname().sysname == "Darwin":
    PLUGINS_DIR = Path("/Library/Audio/Plug-Ins/VST3")
elif os.uname().sysname == "Windows":
    PLUGINS_DIR = Path("C:/Program Files/Common Files/VST3")
