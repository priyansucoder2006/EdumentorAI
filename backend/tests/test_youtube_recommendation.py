import pytest
from unittest.mock import patch, AsyncMock
from app.services.youtube_service import YouTubeService, parse_iso8601_duration
from app.schemas.learning_video import VideoMetadata, LearningVideoResponse


def test_parse_iso8601_duration():
    # 21 minutes 14 seconds
    sec, mins, fmt = parse_iso8601_duration("PT21M14S")
    assert sec == 1274
    assert mins == 21.23
    assert fmt == "21:14"

    # 1 hour 5 minutes 30 seconds
    sec2, mins2, fmt2 = parse_iso8601_duration("PT1H5M30S")
    assert sec2 == 3930
    assert mins2 == 65.5
    assert fmt2 == "1:05:30"

    # 45 seconds
    sec3, mins3, fmt3 = parse_iso8601_duration("PT45S")
    assert sec3 == 45
    assert mins3 == 0.75
    assert fmt3 == "0:45"


@pytest.mark.asyncio
async def test_youtube_missing_api_key():
    service = YouTubeService(api_key="")
    res = await service.find_learning_video("Recursion in Python")
    assert res.found is False
    assert "YOUTUBE_API_KEY is not configured" in res.reason


@pytest.mark.asyncio
async def test_around_20_minutes_ranking():
    service = YouTubeService(api_key="mock_key")
    
    candidates = [
        VideoMetadata(
            video_id="v_short",
            title="Recursion in 3 Minutes",
            channel="CodeShorts",
            duration="3:15",
            duration_minutes=3.25,
            duration_seconds=195,
            view_count=50000,
            url="https://www.youtube.com/watch?v=v_short"
        ),
        VideoMetadata(
            video_id="v_21",
            title="Recursion Full Explained Tutorial",
            channel="TechMentor",
            duration="21:05",
            duration_minutes=21.08,
            duration_seconds=1265,
            view_count=120000,
            url="https://www.youtube.com/watch?v=v_21"
        ),
        VideoMetadata(
            video_id="v_long",
            title="Complete 3 Hour Algorithms Course",
            channel="FreeCourses",
            duration="3:10:00",
            duration_minutes=190.0,
            duration_seconds=11400,
            view_count=500000,
            url="https://www.youtube.com/watch?v=v_long"
        )
    ]

    with patch.object(service, "_search_candidate_video_ids", new_callable=AsyncMock) as mock_search, \
         patch.object(service, "_fetch_video_details", new_callable=AsyncMock) as mock_details:
        
        mock_search.return_value = ["v_short", "v_21", "v_long"]
        mock_details.return_value = candidates

        res = await service.find_learning_video(
            topic="recursion",
            target_duration_minutes=20,
            duration_preference="around"
        )

        assert res.found is True
        assert res.video_id == "v_21"
        assert res.duration == "21:05"
        assert "youtube.com/watch?v=v_21" in res.url


@pytest.mark.asyncio
async def test_under_20_minutes_strict_filtering():
    service = YouTubeService(api_key="mock_key")
    
    candidates = [
        VideoMetadata(
            video_id="v_over",
            title="Docker Full Course Tutorial",
            channel="DevOpsHub",
            duration="28:40",
            duration_minutes=28.67,
            duration_seconds=1720,
            view_count=300000,
            url="https://www.youtube.com/watch?v=v_over"
        ),
        VideoMetadata(
            video_id="v_under",
            title="Docker in 18 Minutes for Beginners",
            channel="FastDev",
            duration="18:20",
            duration_minutes=18.33,
            duration_seconds=1100,
            view_count=150000,
            url="https://www.youtube.com/watch?v=v_under"
        )
    ]

    with patch.object(service, "_search_candidate_video_ids", new_callable=AsyncMock) as mock_search, \
         patch.object(service, "_fetch_video_details", new_callable=AsyncMock) as mock_details:
        
        mock_search.return_value = ["v_over", "v_under"]
        mock_details.return_value = candidates

        res = await service.find_learning_video(
            topic="Docker",
            target_duration_minutes=20,
            duration_preference="under"
        )

        assert res.found is True
        assert res.video_id == "v_under"
        assert res.duration_minutes <= 20.0


@pytest.mark.asyncio
async def test_60_minutes_or_more_ranking():
    service = YouTubeService(api_key="mock_key")
    
    candidates = [
        VideoMetadata(
            video_id="v_short_react",
            title="React Hooks Crash Course",
            duration="12:00",
            duration_minutes=12.0,
            duration_seconds=720,
            channel="WebQuick",
            view_count=500000,
            url="https://www.youtube.com/watch?v=v_short_react"
        ),
        VideoMetadata(
            video_id="v_57_react",
            title="React Hooks Tutorial",
            duration="57:00",
            duration_minutes=57.0,
            duration_seconds=3420,
            channel="CodeCamp",
            view_count=200000,
            url="https://www.youtube.com/watch?v=v_57_react"
        ),
        VideoMetadata(
            video_id="v_68_react",
            title="Complete React Hooks Masterclass and Deep Dive",
            duration="1:08:00",
            duration_minutes=68.0,
            duration_seconds=4080,
            channel="ProReact",
            view_count=180000,
            url="https://www.youtube.com/watch?v=v_68_react"
        )
    ]

    with patch.object(service, "_search_candidate_video_ids", new_callable=AsyncMock) as mock_search, \
         patch.object(service, "_fetch_video_details", new_callable=AsyncMock) as mock_details:
        
        mock_search.return_value = ["v_short_react", "v_57_react", "v_68_react"]
        mock_details.return_value = candidates

        res = await service.find_learning_video(
            topic="React hooks",
            target_duration_minutes=60,
            duration_preference="minimum"
        )

        assert res.found is True
        # Must prefer >= 60 minutes candidate
        assert res.video_id == "v_68_react"
        assert res.duration_minutes >= 60.0


def test_youtube_video_api_endpoint(client, auth_headers):
    mock_resp = LearningVideoResponse(
        found=True,
        title="System Design Primer",
        channel="TechLead",
        video_id="sys_123",
        url="https://www.youtube.com/watch?v=sys_123",
        duration="1:02:15",
        duration_minutes=62.25,
        thumbnail="https://img.youtube.com/vi/sys_123/hqdefault.jpg",
        reason="Best match for 60-minute system design masterclass."
    )
    with patch.object(YouTubeService, "find_learning_video", new_callable=AsyncMock) as mock_find:
        mock_find.return_value = mock_resp

        response = client.post(
            "/api/learning/video",
            headers=auth_headers,
            json={
                "topic": "system design",
                "targetDurationMinutes": 60,
                "durationPreference": "minimum",
                "learnerLevel": "advanced"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["video_id"] == "sys_123"
        assert data["duration"] == "1:02:15"
