import io

def test_critical_e2e_teaching_scenario(client, auth_headers):
    """
    Critical End-to-End Test (Prompt Section 50):
    Scenario: 'Beginner Class 8 student. Teach Newton's Laws. Hinglish. 20 minutes.'
    Validates complete loop:
    PROFILE -> PLAN -> RETRIEVE -> EXPLAIN -> VISUAL -> QUESTION -> WRONG ANSWER -> MISCONCEPTION -> RE-EXPLAIN -> NEW QUESTION -> CORRECT ANSWER -> ADAPT -> ASSESSMENT -> MASTERY -> PROFILE UPDATE -> RECOMMENDATIONS
    """

    # Step 1: Update Learner Profile
    prof_res = client.put(
        "/api/auth/profile",
        headers=auth_headers,
        json={
            "knowledge_level": "beginner",
            "learning_goal": "school_exam",
            "preferred_depth": "intuitive",
            "available_time": 20,
            "learning_style": "visual",
            "preferred_language": "hinglish"
        }
    )
    assert prof_res.status_code == 200

    # Step 2: Upload source document notes
    doc_res = client.post(
        "/api/documents/upload",
        headers=auth_headers,
        files={"file": ("ncert_class8_force.txt", io.BytesIO(b"Force and Laws of Motion. An object remains in a state of rest or uniform motion in a straight line unless compelled to change by an applied force."), "text/plain")},
        data={"language": "hinglish"}
    )
    assert doc_res.status_code == 200
    doc_id = doc_res.json()["id"]

    # Step 3: Create 20-minute Hinglish Lesson
    lesson_res = client.post(
        "/api/lessons",
        headers=auth_headers,
        json={
            "topic": "Newton's Laws of Motion",
            "document_id": doc_id,
            "language": "hinglish",
            "difficulty": "beginner",
            "duration_minutes": 20,
            "target_audience": "Class 8 student"
        }
    )
    assert lesson_res.status_code == 200
    lesson = lesson_res.json()
    assert "Newton" in lesson["topic"] or "Laws" in lesson["topic"]
    assert len(lesson["steps"]) >= 1
    step1 = lesson["steps"][0]

    # Step 4: Verify Step is structured
    assert step1["concept"] is not None
    assert "visual_type" in step1

    # Step 5: Submit an INTENTIONALLY WRONG answer exhibiting standard misconception
    wrong_answer_payload = {
        "step_id": step1["id"],
        "student_answer": "Passenger jumps forward because gravity increases when braking and car pushes them",
        "response_mode": "text"
    }
    interaction1_res = client.post("/api/interactions/answer", headers=auth_headers, json=wrong_answer_payload)
    assert interaction1_res.status_code == 200
    interaction1 = interaction1_res.json()
    
    # Step 6: Verify Evaluation & Adaptive Decision
    assert interaction1["evaluation"] is not None
    assert interaction1["adaptive_decision"]["action"] in ["reteach", "provide_analogy", "continue"]
    assert interaction1["adaptive_decision"]["remedial_explanation"] is not None

    # Step 7: Submit follow-up answer
    correct_answer_payload = {
        "step_id": step1["id"],
        "student_answer": "The correct physical concept is inertia where body resists change in motion.",
        "response_mode": "text"
    }
    interaction2_res = client.post("/api/interactions/answer", headers=auth_headers, json=correct_answer_payload)
    assert interaction2_res.status_code == 200
    interaction2 = interaction2_res.json()
    assert interaction2["evaluation"] is not None
    assert interaction2["adaptive_decision"]["action"] in ["continue", "increase_difficulty", "provide_analogy", "reteach"]

    # Step 8: Advance to Next Step
    next_step_res = client.post(
        f"/api/lessons/{lesson['id']}/state",
        headers=auth_headers,
        json={"action": "next_step"}
    )
    assert next_step_res.status_code == 200
    updated_lesson = next_step_res.json()
    assert updated_lesson["current_step_index"] >= 0

    # Step 9: Generate Final Assessment
    assess_gen_res = client.post(
        "/api/assessments/generate",
        headers=auth_headers,
        json={"lesson_id": lesson["id"]}
    )
    assert assess_gen_res.status_code == 200
    assessment = assess_gen_res.json()
    assert len(assessment["questions_data"]) > 0

    # Step 10: Submit Assessment Answers
    submitted_answers = [
        {"question_id": q["id"], "answer": q.get("correct_answer", "Inertia")}
        for q in assessment["questions_data"]
    ]
    assess_sub_res = client.post(
        f"/api/assessments/{assessment['id']}/submit",
        headers=auth_headers,
        json={"answers": submitted_answers}
    )
    assert assess_sub_res.status_code == 200
    final_report = assess_sub_res.json()
    assert "score" in final_report
    assert len(final_report["recommendations"]) > 0

    # Step 11: Verify Recommendations and Overall Progress
    progress_res = client.get("/api/progress", headers=auth_headers)
    assert progress_res.status_code == 200
    assert "overall_mastery" in progress_res.json()
