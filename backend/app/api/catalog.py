from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app import catalog
from app.schemas.catalog import PackPublic, ProgramPublic

router = APIRouter(tags=["catalog"])


@router.get(
    "/programs",
    response_model=list[ProgramPublic],
    summary="List all training programs",
)
def list_programs() -> list[ProgramPublic]:
    return catalog.list_programs()


@router.get(
    "/programs/{program_id}",
    response_model=ProgramPublic,
    summary="Fetch a single program by ID",
)
def get_program(program_id: str) -> ProgramPublic:
    program = catalog.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Program not found."
        )
    return program


@router.get(
    "/packs",
    response_model=list[PackPublic],
    summary="List subscription packs",
)
def list_packs() -> list[PackPublic]:
    return catalog.list_packs()


@router.get(
    "/packs/{pack_id}",
    response_model=PackPublic,
    summary="Fetch a single pack by ID",
)
def get_pack(pack_id: str) -> PackPublic:
    pack = catalog.get_pack(pack_id)
    if not pack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Pack not found."
        )
    return pack
