from plugins.VST import VST
from config import PLUGINS_DIR

graillon2 = VST(PLUGINS_DIR / "Auburn Sounds Graillon 2.vst3")
panagement2 = VST(PLUGINS_DIR / "Auburn Sounds Panagement 2.vst3")
lens = VST(PLUGINS_DIR / "Auburn Sounds Lens.vst3")
couture = VST(PLUGINS_DIR / "Auburn Sounds Couture.vst3")
dragonfly = VST(PLUGINS_DIR / "DragonflyHallReverb.vst3")

VST_LIST = {
    "graillon2": graillon2,
    "panagement2": panagement2,
    "lens": lens,
    "couture": couture,
    "dragonfly": dragonfly,
}
