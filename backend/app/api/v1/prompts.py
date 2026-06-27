from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.prompts.manager import PromptManager, PromptTemplate
from app.schemas.ai import PromptResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("", response_model=list[PromptResponse])
def list_prompts() -> list[PromptResponse]:
    return [_serialize(prompt) for prompt in PromptManager().list_prompts()]


@router.get("/{name}", response_model=PromptResponse)
def get_prompt(name: str) -> PromptResponse:
    try:
        prompt = PromptManager().get_prompt(name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _serialize(prompt)


def _serialize(prompt: PromptTemplate) -> PromptResponse:
    return PromptResponse(
        name=prompt.name,
        version=prompt.version,
        description=prompt.description,
        variables=prompt.variables,
        body=prompt.body,
    )
