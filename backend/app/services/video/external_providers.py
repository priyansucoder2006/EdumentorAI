import os
import httpx
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger


class CloudVideoProvider:
    """
    Integrations with premier Generative AI Video & Talking Avatar APIs:
    - D-ID API (https://d-id.com): Generates photorealistic speaking avatars.
    - HeyGen API (https://heygen.com): Generates high-fidelity AI human presenters.
    """

    @staticmethod
    def is_cloud_enabled() -> bool:
        return bool(settings.D_ID_API_KEY or settings.HEYGEN_API_KEY)

    @classmethod
    async def generate_avatar_video_did(
        cls,
        script_text: str,
        avatar_image_url: str = "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg",
        language: str = "en"
    ) -> Optional[str]:
        """
        Submits a talk job to D-ID API (https://api.d-id.com/talks).
        Returns download URL for the generated MP4.
        """
        api_key = settings.D_ID_API_KEY
        if not api_key:
            return None

        headers = {
            "Authorization": f"Basic {api_key}" if not api_key.startswith("Basic ") else api_key,
            "Content-Type": "application/json"
        }

        voice_id = "hi-IN-SwaraNeural" if language in ["hi", "hinglish"] else "en-US-JennyNeural"

        payload = {
            "source_url": avatar_image_url,
            "script": {
                "type": "text",
                "input": script_text[:1000],
                "provider": {
                    "type": "microsoft",
                    "voice_id": voice_id
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.5
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post("https://api.d-id.com/talks", json=payload, headers=headers)
                if res.status_code not in (200, 201):
                    logger.warning(f"D-ID talk creation failed: {res.text}")
                    return None

                data = res.json()
                talk_id = data.get("id")
                if not talk_id:
                    return None

                # Poll for completion (up to 30s)
                for _ in range(15):
                    await asyncio.sleep(2)
                    status_res = await client.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
                    if status_res.status_code == 200:
                        status_data = status_res.json()
                        if status_data.get("status") == "done":
                            return status_data.get("result_url")
                        elif status_data.get("status") == "error":
                            logger.error(f"D-ID processing error: {status_data}")
                            break

        except Exception as e:
            logger.error(f"Error communicating with D-ID API: {e}")
        return None

    @classmethod
    async def generate_avatar_video_heygen(
        cls,
        script_text: str,
        language: str = "en"
    ) -> Optional[str]:
        """
        Submits a video generation job to HeyGen API (https://api.heygen.com/v2/video/generate).
        """
        api_key = settings.HEYGEN_API_KEY
        if not api_key:
            return None

        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": "Angela-inblackskirt-20220820",
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script_text[:1000],
                        "voice_id": "2d5a0e6cf36f460aa81f2f3e74b02957"
                    },
                    "background": {
                        "type": "color",
                        "value": "#0b0f19"
                    }
                }
            ],
            "dimension": {
                "width": 1280,
                "height": 720
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post("https://api.heygen.com/v2/video/generate", json=payload, headers=headers)
                if res.status_code not in (200, 201):
                    logger.warning(f"HeyGen video creation failed: {res.text}")
                    return None

                data = res.json()
                video_id = data.get("data", {}).get("video_id")
                if not video_id:
                    return None

                # Poll for completion
                for _ in range(15):
                    await asyncio.sleep(2)
                    status_res = await client.get(
                        f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
                        headers=headers
                    )
                    if status_res.status_code == 200:
                        status_data = status_res.json().get("data", {})
                        if status_data.get("status") == "completed":
                            return status_data.get("video_url")
                        elif status_data.get("status") == "failed":
                            break

        except Exception as e:
            logger.error(f"Error communicating with HeyGen API: {e}")
        return None
