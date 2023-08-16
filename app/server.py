import json
import os
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, Header, Form
from fastapi.responses import HTMLResponse

from effects.effects import process_audio_with_chain
from plugins.plugins import VST_LIST
from lib import load_audio

app = FastAPI()
PORT = os.environ.get("PORT", 8080)

@app.post("/validate_plugins")
async def validate_plugins():
    pass
        
@app.post("/apply_effect")
async def apply_effect(
    audio_file: UploadFile,
    effects_file: UploadFile
):

    try:
        y, sr, duration, did_truncate = await load_audio(audio_file.file, max_duration=500)
        effect_details = json.load(effects_file.file)
        y_processed = await process_audio_with_chain(y, sr, effect_details)

        return {
            "output_audio": y_processed,
            "sample_rate": sr,
            "duration": duration,
            "did_truncate": did_truncate,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_available_plugins", response_class=HTMLResponse)
async def list_available_plugins():
    vst_list_json = [{"name" : key} for key in VST_LIST.keys()]
    vst_list_json = json.dumps(vst_list_json, indent=4)
    return vst_list_json

@app.get("/list_available_plugins_with_parameters", response_class=HTMLResponse)
async def list_available_plugins_with_parameters():
        plugin_names = [key for key in VST_LIST.keys()]
        txt = ""
        for name in plugin_names:
            txt += await list_plugin_params(name)
        return txt

# List all VST params
@app.get("/list_plugin_params/{plugin_name}", response_class=HTMLResponse)
async def list_plugin_params(plugin_name: str):
    try:
        # params_json = await get_plugin_parameters(plugin)
        plugin = VST_LIST[plugin_name]
        params = plugin.get_params()

        # get params values as strings
        for key, value in params.items():
            params[key] = str(value)

        result = dict()
        result["plugin name"] = plugin_name
        result["parameters"] = params

        # Return a prettified JSON response
        # params = json.dumps(params, indent=4)
        result = json.dumps(result, indent=4)
        prettified_json = "<h1>" + plugin_name + "</h1>" + "<pre>" + result + "</pre>"

        return prettified_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, port=int(PORT), host="0.0.0.0", server_header=False)
