import torch
import numpy as np
import json

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models import build_model
from kokoro import generate

app = FastAPI()

# ----------------------
# GLOBAL INIT / MODEL LOADING
# ----------------------
print("Loading model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
try:
    MODEL = build_model("kokoro-v0_19.pth", device)
    VOICE_NAME = "af"
    VOICEPACK = torch.load(f"voices/{VOICE_NAME}.pt", weights_only=True).to(device)
    print("Model loaded.")
except Exception as e:
    print("Error loading model:", e)
    raise

# Helper for PCM conversion
def float_to_pcm16(float_array):
    audio_i16 = np.array(float_array * 32767, dtype=np.int16)
    return audio_i16.tobytes()

# ----------------------
# 1) HTTP Endpoint (Streaming TTS)
# ----------------------
@app.post("/v1/speak_http")
async def speak_http(request: Request):
    """POST JSON: {"text": "..."}  -> returns streaming PCM16 audio."""
    payload = await request.json()
    text = payload.get("text", "")
    print("Request received at /v1/speak_http")
    print(f"Text to TTS: {text}")

    # Split text into segments by period, ignoring empty segments
    segments = [seg.strip() for seg in text.split('.') if seg.strip()]

    def generate_audio():
        for seg in segments:
            audio, _ = generate(MODEL, seg, VOICEPACK, lang=VOICE_NAME[0])
            yield float_to_pcm16(audio)

    # Use StreamingResponse to yield raw audio
    return StreamingResponse(
        generate_audio(),
        media_type="application/octet-stream"
    )

# ----------------------
# 2) WebSocket Endpoint (Streaming TTS)
# ----------------------
@app.websocket("/v1/speak_ws")
async def speak_ws(websocket: WebSocket):
    """
    WebSocket endpoint for streaming TTS.
    Expected JSON messages:
      - {"type": "Speak", "text": "..."}
      - {"type": "Flush"}
      - {"type": "Close"}
    """
    # Accept the WebSocket connection
    await websocket.accept()
    buffer = []

    try:
        while True:
            # Receive a message (text or binary). We'll assume text JSON.
            message = await websocket.receive_text()
            if not message:
                continue

            try:
                data = json.loads(message)
            except ValueError:
                continue  # skip if invalid JSON

            msg_type = data.get("type", "")

            if msg_type == "Speak":
                text = data.get("text", "")
                buffer.append(text)

            elif msg_type == "Flush":
                # Join everything in buffer -> TTS -> send as binary
                if buffer:
                    full_text = " ".join(buffer)
                    buffer.clear()
                    audio, _ = generate(MODEL, full_text, VOICEPACK, lang=VOICE_NAME[0])
                    # Send binary audio (PCM16) back to client
                    await websocket.send_bytes(float_to_pcm16(audio))

            elif msg_type == "Close":
                await websocket.close()
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected.")

    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()


# ----------------------
# 3) Run via Uvicorn
# ----------------------
# If you want to run this file directly:
#   python app.py
# or (for reload) 
#   uvicorn app:app --reload --host 0.0.0.0 --port 8000
# 
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on port 8000...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
