from pydantic import BaseModel
from typing import List

class GenerateRequest(BaseModel):
    notes: List[str]

class GenerateResponse(BaseModel):
    solo: List[str]
    rhythm: List[List[str]]
