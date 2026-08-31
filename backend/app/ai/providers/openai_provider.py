import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock_provider import MockPedagogicalProvider
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str = "https://api.openai.com/v1"):
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

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": messages}
                )
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"OpenAI error: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"OpenAI exception: {e}")

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

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "response_format": {"type": "json_object"}
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    return response_schema.model_validate(parsed)
                else:
                    logger.warning(f"OpenAI error: {res.status_code}, falling back to mock provider")
        except Exception as e:
            logger.warning(f"OpenAI structured exception: {e}, falling back to mock provider")

        return await self.mock_fallback.generate_structured(prompt, response_schema, system_prompt, **kwargs)
