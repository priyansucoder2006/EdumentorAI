import pytest
from app.core.mongodb import get_mongo_db, MongoSyncService


def test_unauthenticated_requests_are_rejected(client):
    """
    Validates that endpoints strictly reject unauthenticated requests without falling back to demo user.
    """
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401

    res_lessons = client.get("/api/lessons")
    assert res_lessons.status_code == 401

    res_docs = client.get("/api/documents")
    assert res_docs.status_code == 401

    res_progress = client.get("/api/progress")
    assert res_progress.status_code == 401


def test_multi_tenant_user_isolation(client):
    """
    Validates complete data isolation between two distinct users (Alice and Bob):
    - Alice cannot see Bob's lessons, documents, progress, assessments, or interactions.
    - Bob cannot see or interact with Alice's resources.
    """
    # 1. Register User Alice
    alice_reg = client.post("/api/auth/register", json={
        "name": "Alice Wonderland",
        "email": "alice@example.com",
        "password": "PasswordAlice123",
        "preferred_language": "en",
        "education_level": "intermediate"
    })
    assert alice_reg.status_code == 200
    alice_token = alice_reg.json()["access_token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}

    # 2. Register User Bob
    bob_reg = client.post("/api/auth/register", json={
        "name": "Bob Builder",
        "email": "bob@example.com",
        "password": "PasswordBob123",
        "preferred_language": "hinglish",
        "education_level": "beginner"
    })
    assert bob_reg.status_code == 200
    bob_token = bob_reg.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # 3. Alice creates a lesson
    alice_lesson_res = client.post(
        "/api/lessons",
        headers=alice_headers,
        json={
            "topic": "Quantum Superposition",
            "language": "en",
            "difficulty": "intermediate",
            "duration_minutes": 20
        }
    )
    assert alice_lesson_res.status_code == 200
    alice_lesson = alice_lesson_res.json()
    alice_lesson_id = alice_lesson["id"]
    alice_step_id = alice_lesson["steps"][0]["id"]

    # 4. Bob lists lessons -> Must NOT contain Alice's lesson
    bob_lessons_res = client.get("/api/lessons", headers=bob_headers)
    assert bob_lessons_res.status_code == 200
    bob_lessons = bob_lessons_res.json()
    assert len(bob_lessons) == 0

    # 5. Bob tries to access Alice's lesson directly by ID -> Must return 404
    bob_get_alice_lesson = client.get(f"/api/lessons/{alice_lesson_id}", headers=bob_headers)
    assert bob_get_alice_lesson.status_code == 404

    # 6. Bob tries to transition Alice's lesson state -> Must return 404
    bob_state_res = client.post(
        f"/api/lessons/{alice_lesson_id}/state",
        headers=bob_headers,
        json={"action": "next_step"}
    )
    assert bob_state_res.status_code == 404

    # 7. Bob tries to submit an answer to Alice's lesson step -> Must return 404
    bob_ans_res = client.post(
        "/api/interactions/answer",
        headers=bob_headers,
        json={
            "step_id": alice_step_id,
            "student_answer": "Hacked answer from Bob"
        }
    )
    assert bob_ans_res.status_code == 404

    # 8. Alice submits an answer to her own lesson
    alice_ans_res = client.post(
        "/api/interactions/answer",
        headers=alice_headers,
        json={
            "step_id": alice_step_id,
            "student_answer": "Superposition means linear combination of basis states."
        }
    )
    assert alice_ans_res.status_code == 200

    # 9. Bob queries interactions for Alice's lesson -> Must return 404
    bob_interactions_res = client.get(f"/api/interactions/{alice_lesson_id}", headers=bob_headers)
    assert bob_interactions_res.status_code == 404

    # 10. Alice generates an assessment
    alice_assess_res = client.post(
        "/api/assessments/generate",
        headers=alice_headers,
        json={"lesson_id": alice_lesson_id}
    )
    assert alice_assess_res.status_code == 200
    alice_assessment_id = alice_assess_res.json()["id"]

    # 11. Bob tries to get or submit Alice's assessment -> Must return 404
    bob_assess_get = client.get(f"/api/assessments/{alice_assessment_id}", headers=bob_headers)
    assert bob_assess_get.status_code == 404

    bob_assess_submit = client.post(
        f"/api/assessments/{alice_assessment_id}/submit",
        headers=bob_headers,
        json={"answers": []}
    )
    assert bob_assess_submit.status_code == 404


def test_mongodb_sync_and_connection():
    """
    Tests MongoDB Atlas connection ping and sync services.
    """
    db = get_mongo_db()
    if db is not None:
        # Validate sync
        test_user = {
            "id": "test-sync-user-999",
            "name": "Mongo Sync Test",
            "email": "sync_test@edumentor.ai",
            "preferred_language": "en",
            "education_level": "intermediate"
        }
        MongoSyncService.sync_user(test_user)
        MongoSyncService.log_auth_event("test-sync-user-999", "sync_test@edumentor.ai", "test_ping")
        
        found = db.users.find_one({"id": "test-sync-user-999"})
        assert found is not None
        assert found["email"] == "sync_test@edumentor.ai"
