import json
from typing import Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock_provider import MockPedagogicalProvider
from app.core.logging import logger

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.mock_fallback = MockPedagogicalProvider()

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.api_key:
            return await self.mock_fallback.generate_text(prompt, system_prompt, **kwargs)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Directive:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow all directives."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {"contents": contents}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    logger.error(f"Gemini API error status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Gemini request exception: {e}")

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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with pure JSON strictly matching this JSON Schema:\n{json.dumps(response_schema.model_json_schema())}"
        
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Directive:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow all directives and return pure JSON."}]})
        contents.append({"role": "user", "parts": [{"text": json_prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    clean_json = raw_text.strip()
                    if clean_json.startswith("```json"):
                        clean_json = clean_json[7:]
                    if clean_json.endswith("```"):
                        clean_json = clean_json[:-3]
                    parsed = json.loads(clean_json.strip())
                    return response_schema.model_validate(parsed)
                else:
                    logger.warning(f"Gemini API failed with {res.status_code}, falling back to mock provider")
        except Exception as e:
            logger.warning(f"Gemini structured exception: {e}, falling back to mock provider")

        return await self.mock_fallback.generate_structured(prompt, response_schema, system_prompt, **kwargs)
