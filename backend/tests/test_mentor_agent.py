import pytest
from unittest.mock import patch, AsyncMock
from app.ai.agents.mentor_agent import EduMentorAgent


@pytest.mark.asyncio
async def test_mentor_agent_executes_code():
    agent = EduMentorAgent()
    
    mock_code_result = {
        "success": True,
        "language": "python",
        "status": "Accepted",
        "stdout": "4\n",
        "stderr": "",
        "compile_output": "",
        "execution_time": "0.01s",
        "memory": "5120 KB",
        "error": None
    }

    with patch("app.ai.agents.mentor_agent.execute_code", new_callable=AsyncMock) as mock_exec, \
         patch.object(agent.llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        
        mock_exec.return_value = mock_code_result
        mock_llm.return_value = "The Python program successfully evaluated 2 + 2 to produce 4."

        msg = "Run this Python code:\n```python\nprint(2 + 2)\n```"
        result = await agent.chat(msg)

        assert "tool_results" in result
        assert result["tool_results"].get("code_execution") is not None
        assert result["code_result"]["stdout"] == "4\n"
        assert "4" in result["response"]


@pytest.mark.asyncio
async def test_mentor_agent_recommends_youtube_video():
    agent = EduMentorAgent()

    mock_vid_result = {
        "found": True,
        "title": "Recursion in 20 Minutes Explained",
        "channel": "ComputerScienceHub",
        "video_id": "rec_20m",
        "url": "https://www.youtube.com/watch?v=rec_20m",
        "duration": "20:45",
        "duration_minutes": 20.75,
        "thumbnail": "https://img.youtube.com/vi/rec_20m/hqdefault.jpg",
        "reason": "Best match for 20-minute recursion concept tutorial."
    }

    with patch("app.ai.agents.mentor_agent.find_learning_video", new_callable=AsyncMock) as mock_vid, \
         patch.object(agent.llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        
        mock_vid.return_value = mock_vid_result
        mock_llm.return_value = (
            "Recursion is a programming method where a function calls itself.\n\n"
            "Recommended video:\n"
            "Recursion in 20 Minutes Explained\n"
            "Channel: ComputerScienceHub\n"
            "Duration: 20:45\n"
            "Watch: https://www.youtube.com/watch?v=rec_20m"
        )

        msg = "Explain recursion. I want a video that teaches it in about 20 minutes."
        result = await agent.chat(msg)

        assert "tool_results" in result
        assert result["tool_results"].get("learning_video") is not None
        assert result["video_result"]["video_id"] == "rec_20m"
        assert "https://www.youtube.com/watch?v=rec_20m" in result["response"]


@pytest.mark.asyncio
async def test_mentor_agent_normal_educational_question():
    agent = EduMentorAgent()

    with patch("app.ai.agents.mentor_agent.execute_code", new_callable=AsyncMock) as mock_exec, \
         patch("app.ai.agents.mentor_agent.find_learning_video", new_callable=AsyncMock) as mock_vid, \
         patch.object(agent.llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        
        mock_llm.return_value = "Pointers in C store memory addresses of other variables."

        msg = "What is a pointer in C?"
        result = await agent.chat(msg)

        # Neither execute_code nor find_learning_video should be called for pure conceptual inquiries
        mock_exec.assert_not_called()
        mock_vid.assert_not_called()
        assert "Pointers in C" in result["response"]
