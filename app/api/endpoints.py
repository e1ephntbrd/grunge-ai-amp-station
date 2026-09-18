import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.api.schemas import NoteInput
from app.services.generator import MusicGeneratorService
from app.config import CHUNK_SIZE


router = APIRouter()

def audio_chunk_generator(audio_bytes: bytes, chunk_size: int = CHUNK_SIZE):
    stream = io.BytesIO(audio_bytes)
    while chunk := stream.read(chunk_size):
        yield chunk


@router.post("/generate-audio-stream")
async def generate_audio_stream(data: NoteInput):
    if not data.notes:
        raise HTTPException(status_code=400, detail="Оберіть хоча б одну ноту.")

    notes_tuple = tuple(sorted(data.notes))

    wav_bytes = MusicGeneratorService.generate_audio_bytes(
        notes_tuple,
        data.temperature,
        data.distortion_gain,
        data.reverb,
        data.tone
    )

    return StreamingResponse(
        audio_chunk_generator(wav_bytes),
        media_type="audio/wav",
        headers={"Content-Disposition": "inline; filename=grunge_jam.wav"}
    )

