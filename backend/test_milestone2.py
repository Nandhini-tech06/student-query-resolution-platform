from fastapi.testclient import TestClient
from app.main import app


def test_milestone_2_full():
    with TestClient(app) as client:
        print("\n========================================================")
        print("RUNNING MILESTONE 2: RAG & KNOWLEDGE MANAGEMENT TESTS")
        print("========================================================\n")

        # 1. Admin Authentication
        admin_login = client.post("/api/v1/auth/login", json={
            "email": "admin@platform.edu",
            "password": "Admin@12345"
        })
        assert admin_login.status_code == 200, admin_login.text
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("[PASSED] Admin authenticated successfully")

        # 2. Verify Initial Seeded Knowledge Items
        list_res = client.get("/api/v1/admin/knowledge", headers=admin_headers)
        assert list_res.status_code == 200, list_res.text
        items = list_res.json()
        assert len(items) >= 10, f"Expected >= 10 seeded items, got {len(items)}"
        print(f"[PASSED] Admin verified {len(items)} knowledge items in database")

        # 3. Admin CRUD Operations (Zero-retraining update test)
        create_payload = {
            "title": "Semester Exchange & Credit Transfer Policy 2026",
            "category": "academics",
            "content": "Students with CGPA >= 8.0 can undertake one semester at approved partner foreign universities. A maximum of 20 credits can be transferred back upon review by the Dean.",
            "source_name": "International Relations Cell Notification #44",
            "source_url": "https://university.edu/international/exchange",
            "tags": "exchange, abroad, credit transfer, foreign university",
            "is_active": True
        }
        create_res = client.post("/api/v1/admin/knowledge", json=create_payload, headers=admin_headers)
        assert create_res.status_code == 201, create_res.text
        new_doc = create_res.json()
        new_doc_id = new_doc["id"]
        print(f"[PASSED] Admin created new knowledge document #{new_doc_id}")

        # Update document
        update_res = client.put(f"/api/v1/admin/knowledge/{new_doc_id}", json={
            "content": "Updated: Students with CGPA >= 8.5 can undertake semester exchange at approved partner universities with up to 24 transferable credits."
        }, headers=admin_headers)
        assert update_res.status_code == 200
        assert "CGPA >= 8.5" in update_res.json()["content"]
        print(f"[PASSED] Admin updated knowledge document #{new_doc_id}")

        # Toggle status (Archive document)
        toggle_res = client.patch(f"/api/v1/admin/knowledge/{new_doc_id}/toggle-status", headers=admin_headers)
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_active"] is False
        print(f"[PASSED] Admin archived knowledge document #{new_doc_id}")

        # Activate document back
        toggle_res2 = client.patch(f"/api/v1/admin/knowledge/{new_doc_id}/toggle-status", headers=admin_headers)
        assert toggle_res2.status_code == 200
        assert toggle_res2.json()["is_active"] is True
        print(f"[PASSED] Admin re-activated knowledge document #{new_doc_id}")

        # 4. Student Authentication
        student_login = client.post("/api/v1/auth/login", json={
            "email": "sarah.connor@student.edu",
            "password": "SecurePass@2026"
        })
        assert student_login.status_code == 200, student_login.text
        student_token = student_login.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print("[PASSED] Student authenticated successfully")

        # 5. Strict RBAC: Student blocked from Admin Knowledge Management
        blocked_create = client.post("/api/v1/admin/knowledge", json=create_payload, headers=student_headers)
        assert blocked_create.status_code == 403
        blocked_stats = client.get("/api/v1/admin/feedback-stats", headers=student_headers)
        assert blocked_stats.status_code == 403
        print("[PASSED] RBAC: Student strictly forbidden from Admin knowledge management APIs (403)")

        # 6. RAG Query 1: In-Domain Attendance Query
        q1_res = client.post("/api/v1/queries/ask", json={
            "question": "What is the minimum attendance required to appear for exams?",
            "category": "academics"
        }, headers=student_headers)
        assert q1_res.status_code == 200, q1_res.text
        q1_data = q1_res.json()
        assert q1_data["is_resolved"] is True
        assert "75%" in q1_data["answer"]
        assert len(q1_data["sources"]) > 0
        assert "Academic Regulations" in q1_data["sources"][0]["source_name"]
        q1_id = q1_data["id"]
        print("[PASSED] RAG In-Domain Query 1 resolved with verified institutional citations")

        # 7. RAG Query 2: In-Domain Fees Query
        q2_res = client.post("/api/v1/queries/ask", json={
            "question": "How much late fine is charged if semester tuition fees are delayed?",
            "category": "fees"
        }, headers=student_headers)
        assert q2_res.status_code == 200, q2_res.text
        q2_data = q2_res.json()
        assert q2_data["is_resolved"] is True
        assert "500" in q2_data["answer"]
        assert any("Finance" in s["source_name"] for s in q2_data["sources"])
        print("[PASSED] RAG In-Domain Query 2 resolved with fee policy and late fine citations")

        # 8. RAG Query 3: Anti-Hallucination Out-of-Domain Query (Must NOT Invent)
        q3_res = client.post("/api/v1/queries/ask", json={
            "question": "What is the capital of Australia and who won the 1998 World Cup?",
        }, headers=student_headers)
        assert q3_res.status_code == 200, q3_res.text
        q3_data = q3_res.json()
        assert q3_data["is_resolved"] is False
        assert "could not find verified institutional records" in q3_data["answer"]
        assert len(q3_data["sources"]) == 0
        print("[PASSED] Anti-Hallucination Guardrail: Out-of-domain query refused with official fallback")

        # 9. Query History Retrieval
        hist_res = client.get("/api/v1/queries/history", headers=student_headers)
        assert hist_res.status_code == 200
        history_list = hist_res.json()
        assert len(history_list) >= 3
        print(f"[PASSED] Student retrieved personal query history ({len(history_list)} records)")

        # 10. Student Feedback Submission
        fb_res = client.post(f"/api/v1/queries/{q1_id}/feedback", json={
            "rating": "HELPFUL",
            "comment": "Accurate attendance policy"
        }, headers=student_headers)
        assert fb_res.status_code == 200
        print(f"[PASSED] Student submitted feedback on Query #{q1_id}")

        # 11. Admin Review Feedback & Aggregated Stats
        stats_res = client.get("/api/v1/admin/feedback-stats", headers=admin_headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_queries"] >= 3
        assert stats["helpful_feedback"] >= 1
        print(f"[PASSED] Admin reviewed real-time telemetry: Total Queries={stats['total_queries']}, Helpful={stats['helpful_feedback']}")

        # Cleanup test document
        del_res = client.delete(f"/api/v1/admin/knowledge/{new_doc_id}", headers=admin_headers)
        assert del_res.status_code == 200
        print(f"[PASSED] Cleaned up temporary knowledge document #{new_doc_id}")

        print("\n========================================================")
        print("ALL MILESTONE 2 BACKEND & RAG TESTS PASSED SUCCESSFULLY!")
        print("========================================================\n")


if __name__ == "__main__":
    test_milestone_2_full()
