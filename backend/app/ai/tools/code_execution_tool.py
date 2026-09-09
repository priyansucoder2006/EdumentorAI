from typing import Optional, Dict, Any
from app.services.code_execution.code_service import CodeExecutionService
from app.core.logging import logger


async def execute_code(
    language: str,
    source_code: str,
    stdin: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Executes source code in a sandboxed Judge0 environment.
    Supports Python, C, C++, Java, JavaScript, TypeScript, C#, Go, Rust, Ruby, etc.

    Parameters:
        language: Programming language name or alias (e.g. 'python', 'cpp', 'java', 'ruby')
        source_code: The complete source code to compile and execute
        stdin: Optional input text provided to the running process

    Returns:
        Structured execution result containing stdout, stderr, compile_output, and execution stats.
    """
    service = CodeExecutionService.get_instance()
    result = await service.execute_code(
        language=language,
        source_code=source_code,
        stdin=stdin
    )

    return {
        "success": result.success,
        "language": result.language,
        "status": result.status,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "compile_output": result.compile_output,
        "execution_time": result.execution_time,
        "memory": result.memory,
        "error": result.error,
        "status_id": result.status_id
    }
