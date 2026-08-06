"""
API Router for Agent Process Control.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from jarvis.application.dto import CreateProcessRequest, ProcessResponse
from jarvis.application.use_cases.process_use_cases import (
    CancelAgentProcessUseCase,
    CreateAgentProcessUseCase,
    GetAgentProcessUseCase,
    ListAgentProcessesUseCase,
)
from jarvis.domain.exceptions import ProcessNotFoundError

router = APIRouter(prefix="/api/v1/processes", tags=["Agent Processes"])


@router.post("", response_model=ProcessResponse, status_code=status.HTTP_201_CREATED, summary="Create Agent Process")
async def create_process(req: CreateProcessRequest, request: Request) -> ProcessResponse:
    """Spawns and schedules a new autonomous agent process."""
    scheduler = request.app.state.scheduler
    use_case = CreateAgentProcessUseCase(scheduler=scheduler)
    return await use_case.execute(req)


@router.get("", response_model=List[ProcessResponse], summary="List All Agent Processes")
async def list_processes(request: Request) -> List[ProcessResponse]:
    """Lists all active and historical agent processes."""
    scheduler = request.app.state.scheduler
    use_case = ListAgentProcessesUseCase(scheduler=scheduler)
    return await use_case.execute()


@router.get("/{process_id}", response_model=ProcessResponse, summary="Get Agent Process Details")
async def get_process(process_id: str, request: Request) -> ProcessResponse:
    """Retrieves process state and step trajectory history."""
    scheduler = request.app.state.scheduler
    use_case = GetAgentProcessUseCase(scheduler=scheduler)
    try:
        return await use_case.execute(process_id)
    except ProcessNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{process_id}", status_code=status.HTTP_200_OK, summary="Cancel Agent Process")
async def cancel_process(process_id: str, request: Request):
    """Cancels a queued or running process."""
    scheduler = request.app.state.scheduler
    use_case = CancelAgentProcessUseCase(scheduler=scheduler)
    try:
        await use_case.execute(process_id)
        return {"message": f"Process '{process_id}' has been cancelled successfully."}
    except ProcessNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
