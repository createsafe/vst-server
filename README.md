# VST Server

Host audio VSTs and audio processing on a web server.

## Installation
Install requirements.
```console
pip install -r requirements.txt
```

### Installing `pluginval`
To validate VSTs we use a tool developed by Tracktion called `pluginval`. This is a contraction of plugin validator, and is used to determine if a VST will run on the system of choice.
#### MacOS
```console
curl -L "https://github.com/Tracktion/pluginval/releases/download/latest_release/pluginval_macOS.zip" -o pluginval.zip
unzip pluginval.zip
```
#### Linux
```console
curl -L "https://github.com/Tracktion/pluginval/releases/download/latest_release/pluginval_linux.zip" -o pluginval.zip
unzip pluginval.zip
```

## Start Server
Start the server by running the following command.
```console
python3 app/server.py
```

## Adding audio effects
Audio effects are stored as VSTs and loaded from the `PLUGIN_DIR` defined in `app/config.py`. 