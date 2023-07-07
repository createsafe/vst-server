# # TODO (?) Replace TypeScript worker & Python REST API with a simple Python worker
# # https://docs.bullmq.io/python/introduction

# import os
# from dotenv import load_dotenv
# from bullmq import Worker

# from .plugins import process_audio_with_plugin
# from .utils import load_audio

# load_dotenv()

# REDIS_URL = os.getenv("REDIS_URL", None)


# async def audio_effects_processor(job):
#     # Process job from bullmq
#     y, sr = load_audio(job.data["audio"], max_duration=300)
#     process_audio_with_plugin(job.data["plugin"], job.data["params"], y, sr)


# worker = Worker(
#     # name="audio-effects",
#     name="placeholder",
#     processor=audio_effects_processor,
#     opts={"connection": REDIS_URL},
# )
