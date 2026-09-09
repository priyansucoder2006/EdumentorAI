import json
import re
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock_provider import MockPedagogicalProvider
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


def clean_json_text(text: str) -> str:
    """Strips markdown code blocks, preamble, and whitespace around JSON."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    # If still not starting with { or [, find first bracket
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        cleaned = cleaned[first_brace : last_brace + 1]
    return cleaned.strip()


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "openai/gpt-oss-20b", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.mock_fallback = MockPedagogicalProvider()

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.api_key:
            return await self.mock_fallback.generate_text(prompt, system_prompt, **kwargs)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model]
        if self.model != "openai/gpt-oss-20b" and "groq.com" in self.base_url:
            models_to_try.append("openai/gpt-oss-20b")

        for m in models_to_try:
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    res = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"model": m, "messages": messages}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.warning(f"OpenAI error with {m}: {res.status_code} {res.text}")
            except Exception as e:
                logger.error(f"OpenAI exception with {m}: {e}")

        return await self.mock_fallback.generate_text(prompt, system_prompt, **kwargs)

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> T:
        if not self.api_key:
            return await self.mock_fallback.generate_structured(prompt, response_schema, system_prompt, **kwargs)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        json_instruction = f"\n\nReturn strict JSON matching this schema:\n{json.dumps(response_schema.model_json_schema())}"
        messages.append({"role": "user", "content": prompt + json_instruction})

        models_to_try = [self.model]
        if self.model != "openai/gpt-oss-20b" and "groq.com" in self.base_url:
            models_to_try.append("openai/gpt-oss-20b")

        for m in models_to_try:
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    res = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "model": m,
                            "messages": messages,
                            "response_format": {"type": "json_object"}
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"]
                        parsed = json.loads(clean_json_text(content))
                        return response_schema.model_validate(parsed)
                    else:
                        logger.warning(f"OpenAI error with {m}: {res.status_code} {res.text}")
            except Exception as e:
                logger.warning(f"OpenAI structured exception with {m}: {e}")

        return await self.mock_fallback.generate_structured(prompt, response_schema, system_prompt, **kwargs)
