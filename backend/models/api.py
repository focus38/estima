import json
from typing import List, Annotated

from fastapi import Form, HTTPException, Depends
from pydantic import BaseModel, Field, ValidationError


class EstimationRequest(BaseModel):
    roles: List[str] =  Field(description="Название ролей, которые должны участвовать в проекте.", default_factory=list)
    models: List[str] =  Field(description="Модели, которые должны участвовать в оценке проекте.", default_factory=list)

def parse_settings(settings: str = Form(...)) -> EstimationRequest:
    try:
        data = json.loads(settings)
        return EstimationRequest(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid settings: {e}")

EstimationRequestDep = Annotated[EstimationRequest, Depends(parse_settings)]