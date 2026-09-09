import asyncio
import base64
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.code_execution import CodeExecutionResult, LanguageItem
from app.services.code_execution.base import BaseCodeExecutionProvider


class Judge0Provider(BaseCodeExecutionProvider):
    """
    HTTP client for communicating with self-hosted Judge0 instance.
    Requires NO paid API key or credit card.
    Communicates directly with JUDGE0_API_URL (e.g. http://localhost:2358).
    """

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = (api_url or settings.JUDGE0_API_URL).rstrip("/")
        self.timeout = float(settings.CODE_EXECUTION_TIMEOUT_SECONDS)

    async def execute_code(
        self,
        language_id: int,
        source_code: str,
        stdin: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ) -> CodeExecutionResult:
        """
        Submits source code to Judge0, waits for execution result, and normalizes output.
        """
        request_timeout = timeout_seconds or self.timeout
        submission_payload = {
            "language_id": language_id,
            "source_code": source_code,
            "stdin": stdin or "",
        }

        # Use base64_encoded=false by default for clean text transfer
        submit_url = f"{self.api_url}/submissions?base64_encoded=false&wait=true"

        try:
            async with httpx.AsyncClient(timeout=request_timeout + 5.0) as client:
                res = await client.post(submit_url, json=submission_payload)

                if res.status_code not in (200, 201):
                    # If wait=true was rejected or failed, attempt asynchronous submit
                    logger.warning(f"Judge0 sync submit returned {res.status_code}. Attempting async polling.")
                    return await self._submit_and_poll(client, submission_payload, request_timeout)

                data = res.json()
                status_obj = data.get("status", {})
                status_id = status_obj.get("id", 0)
                status_desc = status_obj.get("description", "Unknown")

                # If the submission is still queued or processing, poll for completion
                if status_id in (1, 2) and "token" in data:
                    return await self._poll_submission(client, data["token"], request_timeout)

                return self._normalize_judge0_response(data, language_id)

        except httpx.ConnectError as e:
            logger.error(f"Judge0 connection error at {self.api_url}: {e}")
            return CodeExecutionResult(
                success=False,
                language=str(language_id),
                status="Service Unavailable",
                error="Code execution service is temporarily unavailable. Please verify the self-hosted Judge0 instance is running."
            )
        except httpx.TimeoutException:
            logger.warning(f"Judge0 execution timed out after {request_timeout}s")
            return CodeExecutionResult(
                success=False,
                language=str(language_id),
                status="Time Limit Exceeded",
                error=f"Execution timed out after {request_timeout} seconds."
            )
        except Exception as e:
            logger.error(f"Judge0 execution error: {e}")
            return CodeExecutionResult(
                success=False,
                language=str(language_id),
                status="Execution Error",
                error=f"An error occurred while communicating with the code execution service."
            )

    async def _submit_and_poll(
        self,
        client: httpx.AsyncClient,
        payload: Dict[str, Any],
        max_wait_seconds: float
    ) -> CodeExecutionResult:
        """Asynchronously submits code and polls token until completion."""
        async_url = f"{self.api_url}/submissions?base64_encoded=false&wait=false"
        res = await client.post(async_url, json=payload)
        if res.status_code not in (200, 201):
            raise RuntimeError(f"Judge0 async submission failed with HTTP {res.status_code}")

        token = res.json().get("token")
        if not token:
            raise RuntimeError("Judge0 did not return a submission token.")

        return await self._poll_submission(client, token, max_wait_seconds)

    async def _poll_submission(
        self,
        client: httpx.AsyncClient,
        token: str,
        max_wait_seconds: float
    ) -> CodeExecutionResult:
        """Polls Judge0 submission token until status is no longer In Queue / Processing."""
        poll_url = f"{self.api_url}/submissions/{token}?base64_encoded=false"
        start_time = asyncio.get_event_loop().time()
        poll_interval = 0.5

        while (asyncio.get_event_loop().time() - start_time) < max_wait_seconds:
            await asyncio.sleep(poll_interval)
            poll_res = await client.get(poll_url)
            if poll_res.status_code == 200:
                data = poll_res.json()
                status_id = data.get("status", {}).get("id", 0)
                if status_id not in (1, 2):  # 1: In Queue, 2: Processing
                    return self._normalize_judge0_response(data, data.get("language_id", 0))
            poll_interval = min(poll_interval * 1.3, 2.0)

        return CodeExecutionResult(
            success=False,
            language=str(token),
            status="Time Limit Exceeded",
            error=f"Code execution timed out waiting for queue processing."
        )

    def _normalize_judge0_response(self, data: Dict[str, Any], language_id: int) -> CodeExecutionResult:
        """Normalizes raw Judge0 response into standard CodeExecutionResult."""
        status_info = data.get("status", {})
        status_id = status_info.get("id", 0)
        status_desc = status_info.get("description", "Unknown")

        stdout = data.get("stdout") or ""
        stderr = data.get("stderr") or ""
        compile_output = data.get("compile_output") or ""
        message = data.get("message") or ""

        # Decode base64 if returned encoded
        if data.get("is_base64_encoded", False):
            try:
                if stdout:
                    stdout = base64.b64decode(stdout).decode("utf-8", errors="replace")
                if stderr:
                    stderr = base64.b64decode(stderr).decode("utf-8", errors="replace")
                if compile_output:
                    compile_output = base64.b64decode(compile_output).decode("utf-8", errors="replace")
                if message:
                    message = base64.b64decode(message).decode("utf-8", errors="replace")
            except Exception:
                pass

        time_val = data.get("time")
        execution_time = f"{time_val}s" if time_val is not None else None

        memory_val = data.get("memory")
        memory_str = f"{memory_val} KB" if memory_val is not None else None

        # Judge0 status IDs:
        # 3: Accepted
        # 4: Wrong Answer
        # 5: Time Limit Exceeded
        # 6: Compilation Error
        # 7-12: Runtime Error
        # 13: Internal Error
        # 14: Exec Format Error
        is_success = (status_id == 3)
        error_msg = None

        if status_id == 6:
            error_msg = compile_output.strip() or "Compilation Error"
        elif status_id in (7, 8, 9, 10, 11, 12):
            error_msg = stderr.strip() or status_desc
        elif status_id == 5:
            error_msg = "Time Limit Exceeded"
        elif status_id == 13:
            error_msg = message or "Judge0 internal execution error"
        elif not is_success:
            error_msg = stderr.strip() or compile_output.strip() or status_desc

        return CodeExecutionResult(
            success=is_success,
            language=str(language_id),
            status=status_desc,
            stdout=stdout,
            stderr=stderr,
            compile_output=compile_output,
            execution_time=execution_time,
            memory=memory_str,
            error=error_msg,
            status_id=status_id
        )

    async def get_languages(self) -> List[LanguageItem]:
        """Fetches the list of active compilers/interpreters from Judge0."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(f"{self.api_url}/languages")
                if res.status_code == 200:
                    raw_list = res.json()
                    return [
                        LanguageItem(
                            id=item["id"],
                            name=item["name"],
                            is_archived=item.get("is_archived", False)
                        )
                        for item in raw_list
                    ]
        except Exception as e:
            logger.warning(f"Failed to fetch languages from Judge0 ({self.api_url}): {e}")
        return []

    async def health_check(self) -> Dict[str, Any]:
        """Checks if Judge0 HTTP server is reachable and responsive."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.api_url}/system_info")
                if res.status_code == 200:
                    return {"status": "healthy", "details": res.json()}
                
                # Fallback check to /languages
                lang_res = await client.get(f"{self.api_url}/languages")
                if lang_res.status_code == 200:
                    return {"status": "healthy", "languages_count": len(lang_res.json())}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

        return {"status": "unhealthy", "error": "Unable to communicate with Judge0"}
