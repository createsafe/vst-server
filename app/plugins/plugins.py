import os, glob, subprocess
from plugins.VST import VST
from config import PLUGINS_DIR

# graillon2 = VST(PLUGINS_DIR / "Auburn Sounds Graillon 2.vst3")
# panagement2 = VST(PLUGINS_DIR / "Auburn Sounds Panagement 2.vst3")
# lens = VST(PLUGINS_DIR / "Auburn Sounds Lens.vst3")
# couture = VST(PLUGINS_DIR / "Auburn Sounds Couture.vst3")
# dragonfly = VST(PLUGINS_DIR / "DragonflyHallReverb.vst3")

# VST_LIST = {
#     "graillon2": graillon2,
#     "panagement2": panagement2,
#     "lens": lens,
#     "couture": couture,
#     "dragonfly": dragonfly,
# }


def list_vst_files():
    """
    Finds all .vst3 files in PLUGINS_DIR
    """
    result = [y for x in os.walk(PLUGINS_DIR) for y in glob.glob(os.path.join(x[0], '*.vst3'))]
    return result

def validate_vsts(files, timeout_duration=15):
    """
    Validates all plugins using `pluginval` application.
    """
    valid_files = list()
    for file in files:
        validator = subprocess.Popen(["./pluginval.app/Contents/MacOS/pluginval", 
                      "--validate-in-process", 
                      "--verbose"
                      "--strictness-level", "5",
                      "--validate",
                      f"{file}"])
        try:
            validator.wait(timeout=timeout_duration)
            if validator.returncode == 0:
                valid_files.append(file)
            else:
                print("This plugin ain't worth the toilet-paper it's smeared on.")
        except subprocess.TimeoutExpired:
            print(f"{file} is invalid.")
            validator.kill()

    return valid_files

def load_vsts(valid_files):
    vst_files = list_vst_files()
    result = dict()
    for file in vst_files:
        key = os.path.basename(file)
        # load vst 
        val = VST(file)
        result[key] = val
        


VST_LIST = load_vsts(
    validate_vsts(
        list_vst_files()
    )
)