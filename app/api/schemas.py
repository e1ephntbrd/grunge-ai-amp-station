from pydantic import BaseModel, Field
from typing import List, Optional


class NoteInput(BaseModel):
    notes: List[str] = Field(default=["E3", "G3", "A3"])
    temperature: Optional[float] = Field(default=1.0, ge=0.1, le=2.0)
    distortion_gain: Optional[float] = Field(default=18.0, ge=0.0, le=40.0)
    reverb: Optional[float] = Field(default=0.3, ge=0.0, le=1.0)
    tone: Optional[float] = Field(default=3000.0, ge=200.0, le=10000.0)

