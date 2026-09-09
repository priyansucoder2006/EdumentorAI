from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.code_execution import (
    CodeExecutionRequest,
    CodeExecutionResponse,
    CodeExecutionResult,
    LanguageItem,
    Judge0HealthResponse
)
from app.services.code_execution.code_service import CodeExecutionService
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code_endpoint(
    req: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Sandboxed compilation and execution of programming source code via self-hosted Judge0.
    """
    service = CodeExecutionService.get_instance()
    result: CodeExecutionResult = await service.execute_code(
        language=req.language,
        source_code=req.source_code,
        stdin=req.stdin
    )

    return CodeExecutionResponse(
        success=result.success,
        result=result,
        message=result.error if not result.success else "Code executed successfully."
    )


@router.get("/languages", response_model=List[LanguageItem])
async def list_languages_endpoint():
    """
    Returns the list of active compiler and runtime environments.
    """
    service = CodeExecutionService.get_instance()
    return await service.get_supported_languages()


@router.get("/health", response_model=Judge0HealthResponse)
async def judge0_health_endpoint():
    """
    Health check verifying Judge0 server connectivity and ready state.
    """
    service = CodeExecutionService.get_instance()
    return await service.health_check()
