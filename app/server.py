import json
import os
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, Header, Form
from fastapi.responses import HTMLResponse

from effects.effects import process_audio_with_effect
from plugins.utils import get_plugin_parameters
from lib import load_audio

app = FastAPI()

PORT = os.environ.get("PORT", 8080)


class EffectSetting(BaseModel):
    name: str
    value: str


@app.post("/apply_effect/{effect_name}")
async def apply_effect(
    effect_name: str,
    file: UploadFile = File(...),
    Authorization: str = Header(None),
    user_setting: str = Form(None),
    metadata: str = Form(),
):
    # token = Authorization.split(" ")[-1]
    # verify_token(token)

    metadata_dict = json.loads(metadata) if metadata else {}

    try:
        y, sr, duration, did_truncate = await load_audio(file.file, max_duration=500)
        y_processed = await process_audio_with_effect(y, sr, effect_name, user_setting, metadata_dict)

        return {
            "output_audio": y_processed,
            "sample_rate": sr,
            "duration": duration,
            "did_truncate": did_truncate,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Super temporary auth
def verify_token(token: str):
    if not token == os.environ.get("AUTH_TOKEN", "gr!m3s-fHsB-adVOf-grTK"):
        raise HTTPException(status_code=401)


# List all VST params
@app.get("/list_plugin_params/{plugin}", response_class=HTMLResponse)
async def list_plugin_params(plugin: str):
    try:
        params_json = await get_plugin_parameters(plugin)
        params = json.loads(params_json)

        # Return a prettified JSON response
        prettified_json = "<pre>" + json.dumps(params, indent=4) + "</pre>"

        return prettified_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, port=int(PORT), host="0.0.0.0", server_header=False)
