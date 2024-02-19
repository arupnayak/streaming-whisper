import os
from faster_whisper import WhisperModel, decode_audio
from fastapi import FastAPI, Query, File, UploadFile, Form
from starlette.responses import StreamingResponse
import time
import asyncio
from typing import Optional

app = FastAPI()

model_size = "base"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float32")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

async def transcript(
        audio_file_name: str
):
    try:
        start_time = time.time()
        print("Transcribing %s" % audio_file_name)
        segments, info = model.transcribe(audio_file_name, beam_size=5)
        print("Transcription took %.2fs" % (time.time() - start_time))
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            yield segment.text
        # delete audio file
        try:
            os.remove(audio_file_name)
        except:
            print("Error while deleting file")
    except asyncio.CancelledError:
        print("Cancelled")
        return

@app.post("/transcript")
async def transcript_endpoint(audio_file_name: Optional[str] = Form(None),
                              audio_file: UploadFile = File(None)):
    if audio_file:
        audio_file_name = "audio/" + time.strftime("%Y%m%d-%H%M%S") + audio_file.filename
        # save audio_file to disk
        with open(audio_file_name, "wb") as buffer:
            buffer.write(audio_file.file.read())
    return StreamingResponse(transcript(audio_file_name))

async def generator():
    try:
        for i in range(100):
            yield "Hello World"
            print("Hello World")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Cancelled")
        return

@app.post("/")
async def main(file: UploadFile = File(...)):
    return StreamingResponse(generator())
    
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