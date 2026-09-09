import re
import math
from typing import List, Dict, Any, Optional, Tuple
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.learning_video import VideoMetadata, LearningVideoResponse


def parse_iso8601_duration(duration_str: str) -> Tuple[int, float, str]:
    """
    Parses ISO 8601 duration (e.g. 'PT1H20M15S', 'PT21M14S', 'PT45S')
    Returns: (total_seconds, duration_minutes, formatted_str e.g. '1:20:15' or '21:14')
    """
    if not duration_str or not duration_str.startswith("P"):
        return 0, 0.0, "0:00"

    pattern = re.compile(
        r"P(?:(?P<days>\d+)D)?"
        r"(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?"
    )
    match = pattern.match(duration_str)
    if not match:
        return 0, 0.0, "0:00"

    parts = match.groupdict()
    days = int(parts.get("days") or 0)
    hours = int(parts.get("hours") or 0) + (days * 24)
    minutes = int(parts.get("minutes") or 0)
    seconds = int(parts.get("seconds") or 0)

    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    duration_minutes = round(total_seconds / 60.0, 2)

    if hours > 0:
        formatted = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        formatted = f"{minutes}:{seconds:02d}"

    return total_seconds, duration_minutes, formatted


class YouTubeService:
    """
    Service for searching, scoring, and ranking educational videos via official YouTube Data API v3.
    Always returns exactly ONE best video matching learner topic and duration requirements.
    """

    SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
    VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.YOUTUBE_API_KEY

    async def find_learning_video(
        self,
        topic: str,
        target_duration_minutes: Optional[float] = None,
        duration_preference: Optional[str] = "around",
        learner_level: Optional[str] = "beginner"
    ) -> LearningVideoResponse:
        """
        Searches YouTube for candidates, fetches exact duration & metadata,
        and ranks candidates to find the single best matching educational video.
        """
        if not self.api_key:
            logger.warning("YouTube API key is not configured.")
            return LearningVideoResponse(
                found=False,
                reason="YouTube search is unavailable because YOUTUBE_API_KEY is not configured."
            )

        clean_topic = (topic or "").strip()
        if not clean_topic:
            return LearningVideoResponse(
                found=False,
                reason="Please provide a valid topic to search for learning videos."
            )

        # Normalize duration parameters
        target_mins, preference = self._normalize_duration_request(target_duration_minutes, duration_preference)

        try:
            # 1. Fetch candidate video IDs via Search API
            candidate_ids = await self._search_candidate_video_ids(clean_topic, preference, target_mins)
            if not candidate_ids:
                logger.info(f"No YouTube video candidates found for topic: {clean_topic}")
                return LearningVideoResponse(
                    found=False,
                    reason=f"No suitable video was found for '{clean_topic}'."
                )

            # 2. Fetch full video details (exact ISO durations, statistics, embeddability)
            candidates = await self._fetch_video_details(candidate_ids)
            if not candidates:
                return LearningVideoResponse(
                    found=False,
                    reason=f"Could not retrieve video details for '{clean_topic}'."
                )

            logger.info(f"Retrieved {len(candidates)} YouTube candidates for topic '{clean_topic}'")

            # 3. Filter and rank candidates
            ranked_candidates = self._rank_candidates(
                candidates=candidates,
                topic=clean_topic,
                target_duration_minutes=target_mins,
                duration_preference=preference,
                learner_level=learner_level or "beginner"
            )

            if not ranked_candidates:
                return LearningVideoResponse(
                    found=False,
                    reason=f"No suitable video was found for '{clean_topic}' matching the duration criteria ({preference} {target_mins} min)."
                )

            # 4. Select the ONE best video
            best_video = ranked_candidates[0]
            logger.info(f"Selected best video: '{best_video.title}' ({best_video.duration}) ID: {best_video.video_id}")

            return LearningVideoResponse(
                found=True,
                title=best_video.title,
                channel=best_video.channel,
                video_id=best_video.video_id,
                url=best_video.url,
                duration=best_video.duration,
                duration_minutes=best_video.duration_minutes,
                thumbnail=best_video.thumbnail,
                reason=best_video.reason or f"Best match for '{clean_topic}' ({preference} {best_video.duration}).",
                video=best_video
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"YouTube API HTTP error: {e.response.status_code}")
            return LearningVideoResponse(
                found=False,
                reason="YouTube service returned an error. Please try again later."
            )
        except Exception as e:
            logger.error(f"YouTube service exception: {e}")
            return LearningVideoResponse(
                found=False,
                reason="An error occurred while finding learning videos."
            )

    def _normalize_duration_request(
        self,
        target_minutes: Optional[float],
        preference: Optional[str]
    ) -> Tuple[Optional[float], str]:
        """Normalizes target duration and preference mode."""
        pref = (preference or "around").lower().strip()

        # Handle text variants
        if "under" in pref or "less than" in pref or "max" in pref:
            pref = "under"
        elif "more" in pref or "at least" in pref or "min" in pref or "minimum" in pref:
            pref = "minimum"
        elif "short" in pref:
            pref = "short"
            if not target_minutes:
                target_minutes = 15.0
        elif "detail" in pref or "comprehensive" in pref or "full" in pref:
            pref = "detailed"
            if not target_minutes:
                target_minutes = 60.0
        elif "exact" in pref:
            pref = "exact"
        else:
            pref = "around"

        return target_minutes, pref

    async def _search_candidate_video_ids(
        self,
        topic: str,
        preference: str,
        target_minutes: Optional[float]
    ) -> List[str]:
        """Calls YouTube Data API v3 search endpoint to get candidate video IDs."""
        # Optimize query with educational keywords
        query = f"{topic} tutorial explanation"

        # YouTube search API videoDuration filter supports: 'short' (<4 min), 'medium' (4-20 min), 'long' (>20 min)
        video_duration_param = None
        if target_minutes is not None:
            if target_minutes <= 4.0:
                video_duration_param = "short"
            elif target_minutes > 20.0 or preference in ("minimum", "detailed"):
                video_duration_param = "long"
            else:
                video_duration_param = "medium"

        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": 25,
            "relevanceLanguage": "en",
            "safeSearch": "moderate",
            "key": self.api_key
        }
        if video_duration_param:
            params["videoDuration"] = video_duration_param

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(self.SEARCH_API_URL, params=params)
            if res.status_code != 200:
                # If duration param restricted too much, fallback to broad search
                if video_duration_param:
                    params.pop("videoDuration", None)
                    res = await client.get(self.SEARCH_API_URL, params=params)

                if res.status_code != 200:
                    logger.warning(f"YouTube search API error: {res.status_code}")
                    return []

            data = res.json()
            items = data.get("items", [])
            video_ids = [
                item["id"]["videoId"]
                for item in items
                if item.get("id", {}).get("videoId")
            ]
            return video_ids

    async def _fetch_video_details(self, video_ids: List[str]) -> List[VideoMetadata]:
        """Fetches detailed video information including exact ISO duration and statistics."""
        if not video_ids:
            return []

        ids_param = ",".join(video_ids[:50])
        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ids_param,
            "key": self.api_key
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(self.VIDEOS_API_URL, params=params)
            if res.status_code != 200:
                logger.warning(f"YouTube videos detail API error: {res.status_code}")
                return []

            data = res.json()
            items = data.get("items", [])
            results: List[VideoMetadata] = []

            for item in items:
                vid = item["id"]
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})
                statistics = item.get("statistics", {})
                status_info = item.get("status", {})

                title = snippet.get("title", "")
                channel = snippet.get("channelTitle", "")
                description = snippet.get("description", "")
                published_at = snippet.get("publishedAt")

                # Thumbnail extraction
                thumbnails = snippet.get("thumbnails", {})
                thumb_url = (
                    thumbnails.get("high", {}).get("url")
                    or thumbnails.get("medium", {}).get("url")
                    or thumbnails.get("default", {}).get("url")
                    or f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
                )

                # Parse exact ISO 8601 duration
                raw_duration = content_details.get("duration", "PT0S")
                tot_sec, dur_mins, dur_fmt = parse_iso8601_duration(raw_duration)

                # Statistics
                view_count = int(statistics.get("viewCount") or 0)
                like_count = int(statistics.get("likeCount") or 0)
                embeddable = status_info.get("embeddable", True)

                results.append(
                    VideoMetadata(
                        video_id=vid,
                        title=title,
                        channel=channel,
                        description=description,
                        thumbnail=thumb_url,
                        duration=dur_fmt,
                        duration_minutes=dur_mins,
                        duration_seconds=tot_sec,
                        view_count=view_count,
                        like_count=like_count,
                        published_at=published_at,
                        embeddable=embeddable,
                        url=f"https://www.youtube.com/watch?v={vid}"
                    )
                )

            return results

    def _rank_candidates(
        self,
        candidates: List[VideoMetadata],
        topic: str,
        target_duration_minutes: Optional[float],
        duration_preference: str,
        learner_level: str
    ) -> List[VideoMetadata]:
        """
        Scores and ranks candidate videos based on:
        1. Strict duration filtering (for 'under' / 'minimum')
        2. Duration proximity score
        3. Topic and keyword relevance
        4. Channel and view quality signals
        """
        topic_words = set(re.findall(r"\w+", topic.lower()))
        scored_candidates: List[Tuple[float, VideoMetadata, str]] = []

        for candidate in candidates:
            # Skip non-video / empty items
            if candidate.duration_seconds < 10:
                continue

            dur_mins = candidate.duration_minutes

            # 1. Strict duration constraint check
            if duration_preference == "under" and target_duration_minutes is not None:
                # NEVER recommend a video longer than the target duration
                if dur_mins > (target_duration_minutes + 0.5):
                    continue

            # 2. Duration Score Calculation (0.0 to 100.0)
            duration_score, duration_reason = self._compute_duration_score(
                dur_mins, target_duration_minutes, duration_preference
            )

            # If minimum preference requested and video is far below minimum, severely discount
            if duration_preference == "minimum" and target_duration_minutes is not None:
                if dur_mins < (target_duration_minutes * 0.9):
                    duration_score *= 0.2

            # 3. Topic & Title Relevance (0.0 to 50.0)
            title_lower = candidate.title.lower()
            desc_lower = candidate.description.lower()

            matched_keywords = sum(1 for w in topic_words if w in title_lower)
            topic_score = (matched_keywords / max(len(topic_words), 1)) * 40.0

            # Bonus for educational phrasing in title
            if any(k in title_lower for k in ["tutorial", "course", "explained", "guide", "crash course", "full", "learn"]):
                topic_score += 10.0

            # 4. View Count & Popularity Signal (0.0 to 15.0)
            # Logarithmic scaling so 1M views doesn't completely overwhelm a better-matching 50k view video
            views = candidate.view_count or 0
            view_score = min(math.log10(views + 1) * 2.5, 15.0) if views > 0 else 2.0

            # Total Composite Score
            total_score = (duration_score * 0.50) + (topic_score * 0.40) + (view_score * 0.10)

            reason = (
                f"Selected as top educational resource for '{topic}' ({candidate.duration}). "
                f"{duration_reason}"
            )

            candidate.score = round(total_score, 2)
            candidate.reason = reason
            scored_candidates.append((total_score, candidate, reason))

        # Sort descending by composite score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_candidates]

    def _compute_duration_score(
        self,
        actual_minutes: float,
        target_minutes: Optional[float],
        preference: str
    ) -> Tuple[float, str]:
        """Calculates duration match score from 0.0 to 100.0."""
        if target_minutes is None:
            if preference == "short":
                target_minutes = 12.0
            elif preference == "detailed":
                target_minutes = 60.0
            else:
                return 80.0, f"Duration: {actual_minutes:.1f} mins"

        diff = abs(actual_minutes - target_minutes)

        if preference in ("around", "exact"):
            # Gaussian dropoff centered on target_minutes
            sigma = max(target_minutes * 0.25, 3.0)
            score = 100.0 * math.exp(-((diff ** 2) / (2 * (sigma ** 2))))
            reason = f"Closest duration to requested ~{target_minutes:.0f} mins ({actual_minutes:.1f} mins)."
            return score, reason

        elif preference == "under":
            # Best is close to target without exceeding
            if actual_minutes <= target_minutes:
                # Closer to target from below gets higher score (more comprehensive within limit)
                score = 70.0 + (30.0 * (actual_minutes / target_minutes))
                reason = f"Fits within your {target_minutes:.0f}-minute time limit ({actual_minutes:.1f} mins)."
            else:
                score = 0.0
                reason = f"Exceeds requested {target_minutes:.0f} mins."
            return score, reason

        elif preference == "minimum":
            # Best is >= target_minutes
            if actual_minutes >= target_minutes:
                # High score, slight bonus for solid comprehensive length
                excess = actual_minutes - target_minutes
                score = 85.0 + min(15.0, (excess / target_minutes) * 10.0)
                reason = f"Provides comprehensive {target_minutes:.0f}+ minute coverage ({actual_minutes:.1f} mins)."
            else:
                score = max(0.0, 40.0 - (diff * 2.0))
                reason = f"Below requested minimum of {target_minutes:.0f} mins."
            return score, reason

        elif preference == "short":
            if 5.0 <= actual_minutes <= 18.0:
                score = 95.0
            else:
                score = max(20.0, 90.0 - (abs(actual_minutes - 10.0) * 3.0))
            reason = f"Concise learning overview ({actual_minutes:.1f} mins)."
            return score, reason

        elif preference == "detailed":
            if actual_minutes >= 45.0:
                score = 100.0
            else:
                score = max(20.0, (actual_minutes / 45.0) * 80.0)
            reason = f"In-depth detailed walkthrough ({actual_minutes:.1f} mins)."
            return score, reason

        return 75.0, f"Duration: {actual_minutes:.1f} mins."
