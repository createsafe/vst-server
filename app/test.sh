curl -X 'POST' \
  'http://localhost:8080/apply_effect/test_effect' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/Users/julianvanasse/Development/createsafe/voiceai/ej/audio-api/sound-design/audio/eva-as-grimes.wav;type=audio/x-wav' \
  -F 'effect_json_file=@/Users/julianvanasse/Development/createsafe/voiceai/ej/audio-api/sound-design/elftune.json;type=application/json'