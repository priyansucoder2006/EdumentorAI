import re
from typing import Optional, Dict, Any, List
from app.ai.providers import get_llm_provider
from app.ai.prompts.teacher import EDUMENTOR_MENTOR_SYSTEM_PROMPT
from app.ai.tools.code_execution_tool import execute_code
from app.ai.tools.youtube_tool import find_learning_video
from app.core.logging import logger


class EduMentorAgent:
    """
    Intelligent Educational Mentor Agent.
    Coordinates pedagogical answers, code execution via Judge0, and duration-aware video recommendations.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def chat(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Processes a student's prompt, determines required tool invocations (code execution or video recommendation),
        and synthesizes a clear pedagogical response.
        """
        tool_results: Dict[str, Any] = {}
        code_result: Optional[Dict[str, Any]] = None
        video_result: Optional[Dict[str, Any]] = None

        # 1. Analyze if Code Execution is needed
        code_intent = self._detect_code_execution_intent(message)
        if code_intent:
            lang, code_snippet, stdin_val = code_intent
            logger.info(f"Agent detected code execution request for language: {lang}")
            code_result = await execute_code(language=lang, source_code=code_snippet, stdin=stdin_val)
            tool_results["code_execution"] = code_result

        # 2. Analyze if YouTube Video Recommendation is needed
        video_intent = self._detect_video_intent(message)
        if video_intent:
            topic, target_mins, preference = video_intent
            logger.info(f"Agent detected video search request for topic: '{topic}', duration: {target_mins}m ({preference})")
            video_result = await find_learning_video(
                topic=topic,
                target_duration_minutes=target_mins,
                duration_preference=preference
            )
            tool_results["learning_video"] = video_result

        # 3. Generate pedagogical response using LLM
        prompt = self._construct_prompt(
            user_message=message,
            code_result=code_result,
            video_result=video_result,
            language=language
        )

        system_prompt = EDUMENTOR_MENTOR_SYSTEM_PROMPT.format(language=language)
        ai_response_text = await self.llm.generate_text(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return {
            "response": ai_response_text,
            "tool_results": tool_results,
            "code_result": code_result,
            "video_result": video_result
        }

    def _detect_code_execution_intent(self, message: str) -> Optional[tuple[str, str, str]]:
        """
        Extracts language, source code block, and stdin if execution was requested.
        """
        msg_lower = message.lower()
        run_keywords = ["run", "execute", "compile", "test this", "debug", "what is the output", "run this", "compile this"]
        
        has_run_intent = any(k in msg_lower for k in run_keywords)
        
        # Extract markdown code blocks e.g. ```python ... ```
        code_match = re.search(r"```([a-zA-Z0-9_\+\#\.\-]+)?\n([\s\S]*?)```", message)
        
        if code_match:
            detected_lang = (code_match.group(1) or "python").strip()
            source_code = code_match.group(2).strip()
            
            # If user explicitly asked to run or provided code in a run context
            if has_run_intent or len(source_code) > 0:
                # Extract stdin if provided e.g. "input: 10" or "stdin: 5"
                stdin_match = re.search(r"(?:stdin|input|with input)[:=]\s*([^\n\r]+)", message, re.IGNORECASE)
                stdin_val = stdin_match.group(1).strip() if stdin_match else ""
                return detected_lang, source_code, stdin_val

        # Check inline code pattern e.g. print(2 + 2)
        inline_run_match = re.search(r"(?:run|execute|compile|test)\s+(?:this\s+)?([a-zA-Z\+\#]+)?\s*(?:code|program)?:\s*(.+)", message, re.IGNORECASE | re.DOTALL)
        if inline_run_match:
            lang = inline_run_match.group(1) or "python"
            code = inline_run_match.group(2).strip()
            return lang, code, ""

        return None

    def _detect_video_intent(self, message: str) -> Optional[tuple[str, Optional[float], str]]:
        """
        Detects if learner asked for a YouTube video/tutorial and extracts duration parameters.
        """
        msg_lower = message.lower()
        video_keywords = ["video", "youtube", "tutorial", "watch", "course", "teach me"]
        
        has_video_request = any(k in msg_lower for k in video_keywords)
        if not has_video_request and "minute" not in msg_lower and "hour" not in msg_lower:
            return None

        # Extract duration
        target_mins = None
        duration_pref = "around"

        # Regex for patterns like:
        # "in 20 minutes", "under 30 minutes", "60 minutes or more", "at least 1 hour", "around 45 min", "2 hours"
        under_match = re.search(r"(?:under|less than|within|max)\s+(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|hours?|hrs?)", msg_lower)
        min_match = re.search(r"(?:at least|minimum|more than|\+)\s*(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|hours?|hrs?)", msg_lower) or re.search(r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?)\s*(?:or more|\+)", msg_lower)
        around_match = re.search(r"(?:around|about|approx|approximately)\s+(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|hours?|hrs?)", msg_lower)
        general_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:minute|min|hour|hr)s?", msg_lower)

        if under_match:
            val = float(under_match.group(1))
            target_mins = val * 60.0 if "hour" in under_match.group(0) else val
            duration_pref = "under"
        elif min_match:
            val = float(min_match.group(1))
            target_mins = val * 60.0 if "hour" in min_match.group(0) else val
            duration_pref = "minimum"
        elif around_match:
            val = float(around_match.group(1))
            target_mins = val * 60.0 if "hour" in around_match.group(0) else val
            duration_pref = "around"
        elif general_match:
            val = float(general_match.group(1))
            target_mins = val * 60.0 if "hour" in general_match.group(0) else val
            if "detailed" in msg_lower:
                duration_pref = "detailed"
            else:
                duration_pref = "around"

        if "short" in msg_lower and not target_mins:
            duration_pref = "short"
            target_mins = 15.0
        elif "detailed" in msg_lower and not target_mins:
            duration_pref = "detailed"
            target_mins = 60.0

        # Topic extraction: clean prompt
        topic_clean = re.sub(r"(?:give me a video|find a video|recommend a video|video about|video on|tutorial on|in \d+ minutes|under \d+ minutes|\d+ minutes or more|at least \d+ hour|short video|detailed tutorial|teach me)", "", message, flags=re.IGNORECASE).strip()
        topic = topic_clean if len(topic_clean) > 2 else message

        return topic, target_mins, duration_pref

    def _construct_prompt(
        self,
        user_message: str,
        code_result: Optional[Dict[str, Any]],
        video_result: Optional[Dict[str, Any]],
        language: str
    ) -> str:
        prompt_parts = [f"Student Inquiry: {user_message}"]

        if code_result:
            prompt_parts.append("\n[Official Judge0 Sandboxed Execution Result]:")
            prompt_parts.append(f"Success: {code_result.get('success')}")
            prompt_parts.append(f"Status: {code_result.get('status')}")
            if code_result.get("stdout"):
                prompt_parts.append(f"Standard Output:\n{code_result.get('stdout')}")
            if code_result.get("stderr"):
                prompt_parts.append(f"Standard Error:\n{code_result.get('stderr')}")
            if code_result.get("compile_output"):
                prompt_parts.append(f"Compiler Output:\n{code_result.get('compile_output')}")
            if code_result.get("execution_time"):
                prompt_parts.append(f"Execution Time: {code_result.get('execution_time')}")
            if code_result.get("memory"):
                prompt_parts.append(f"Memory: {code_result.get('memory')}")
            if code_result.get("error"):
                prompt_parts.append(f"Error Diagnostic: {code_result.get('error')}")

        if video_result and video_result.get("found"):
            prompt_parts.append("\n[Verified YouTube Data API Recommendation]:")
            prompt_parts.append(f"Title: {video_result.get('title')}")
            prompt_parts.append(f"Channel: {video_result.get('channel')}")
            prompt_parts.append(f"Duration: {video_result.get('duration')}")
            prompt_parts.append(f"URL: {video_result.get('url')}")
            prompt_parts.append(f"Reason: {video_result.get('reason')}")

        prompt_parts.append(
            "\nProvide a comprehensive, empathetic educational response. "
            "If code was executed, explain the actual output or compiler errors clearly. "
            "If a video was recommended, include the exact video recommendation section with the real URL."
        )

        return "\n".join(prompt_parts)
