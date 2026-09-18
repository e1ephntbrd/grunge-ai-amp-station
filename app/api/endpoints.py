from fastapi import APIRouter
from app.models.schemas import GenerateRequest, GenerateResponse
from app.services.generator import MusicGeneratorService

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_music(data: GenerateRequest):
    result = MusicGeneratorService.generate_jam(data.notes)
    return result
