import os
from faster_whisper import WhisperModel, decode_audio
from fastapi import FastAPI, Query
from starlette.responses import StreamingResponse
import time

app = FastAPI()

model_size = "base"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float32")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8

async def transcript(
        audio_file_name: str
):
    start_time = time.time()
    segments, info = model.transcribe(audio_file_name, beam_size=5)
    print("Transcription took %.2fs" % (time.time() - start_time))
    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    yield_time = time.time()
    for segment in segments:
        print("Yield took %.2fs" % (time.time() - yield_time))
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        yield segment.text

@app.get("/transcript")
async def transcript_endpoint(audio_file_name: str = Query()):
    # set header to stream the response
    return StreamingResponse( transcript(audio_file_name))

def test_stereo_diarization(data_dir):
    model = WhisperModel("tiny")

    audio_path = os.path.join(data_dir, "audio/HIN_M_DeepakS.mp3")
    left, right = decode_audio(audio_path, split_stereo=True)

    segments, _ = model.transcribe(left)
    transcription = "".join(segment.text for segment in segments).strip()
    assert transcription == (
        "He began a confused complaint against the wizard, "
        "who had vanished behind the curtain on the left."
    )

    segments, _ = model.transcribe(right)
    transcription = "".join(segment.text for segment in segments).strip()
    assert transcription == "The horizon seems extremely distant."