def test_lesson_planner_and_time_adaptation(client, auth_headers):
    # Test 5-minute lesson
    res_5m = client.post(
        "/api/lessons",
        headers=auth_headers,
        json={
            "topic": "Newton's Laws",
            "duration_minutes": 5,
            "language": "hinglish",
            "difficulty": "beginner"
        }
    )
    assert res_5m.status_code == 200
    lesson_5m = res_5m.json()
    assert lesson_5m["duration_minutes"] == 5
    assert len(lesson_5m["steps"]) >= 1

    # Test 20-minute lesson
    res_20m = client.post(
        "/api/lessons",
        headers=auth_headers,
        json={
            "topic": "Newton's Laws",
            "duration_minutes": 20,
            "language": "hinglish",
            "difficulty": "beginner"
        }
    )
    assert res_20m.status_code == 200
    lesson_20m = res_20m.json()
    assert lesson_20m["duration_minutes"] == 20
    assert len(lesson_20m["steps"]) >= len(lesson_5m["steps"])
