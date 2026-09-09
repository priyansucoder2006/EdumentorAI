from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.schemas.code_execution import CodeExecutionResult, LanguageItem


class BaseCodeExecutionProvider(ABC):
    """
    Abstract interface for sandboxed code execution backends (Judge0, etc.).
    EduMentorAI NEVER executes arbitrary code locally on its host server.
    """

    @abstractmethod
    async def execute_code(
        self,
        language_id: int,
        source_code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ) -> CodeExecutionResult:
        """
        Submits code to the execution environment and waits for completion.
        """
        pass

    @abstractmethod
    async def get_languages(self) -> List[LanguageItem]:
        """
        Retrieves supported language runtimes/compilers from execution backend.
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifies execution backend reachability and health.
        """
        pass
