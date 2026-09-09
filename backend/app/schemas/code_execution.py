from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    language: str = Field(..., description="Programming language name or alias, e.g. python, c, cpp, java, javascript, ruby")
    source_code: str = Field(..., alias="sourceCode", description="Source code to compile and execute")
    stdin: Optional[str] = Field(default="", description="Optional standard input stream")

    model_config = {
        "populate_by_name": True
    }


class CodeExecutionResult(BaseModel):
    success: bool
    language: str
    status: str
    stdout: str = ""
    stderr: str = ""
    compile_output: str = ""
    execution_time: Optional[str] = None
    memory: Optional[str] = None
    error: Optional[str] = None
    status_id: Optional[int] = None


class CodeExecutionResponse(BaseModel):
    success: bool
    result: CodeExecutionResult
    message: Optional[str] = None


class LanguageItem(BaseModel):
    id: int
    name: str
    is_archived: Optional[bool] = False


class Judge0HealthResponse(BaseModel):
    status: str
    judge0_url: str
    languages_count: int
    version: Optional[str] = None
    message: str
