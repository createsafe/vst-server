import os, glob, subprocess
from plugins.VST import VST
from config import PLUGINS_DIR


def list_vst_files():
    """
    Finds all .vst3 files in PLUGINS_DIR
    """
    result = [y for x in os.walk(PLUGINS_DIR) for y in glob.glob(os.path.join(x[0], '*.vst3'))]
    return result

def validate_vsts(files, timeout_duration=10):
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
    result = dict()
    for file in valid_files:
        key = os.path.basename(file)
        # load vst 
        val = VST(file)
        result[key] = val
    return result
        


VST_LIST = load_vsts(list_vst_files())