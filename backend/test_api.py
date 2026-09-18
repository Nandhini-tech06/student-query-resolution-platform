from fastapi.testclient import TestClient
from app.main import app


def run_all_tests():
    with TestClient(app) as client:
        # 1. Health check endpoints
        res_health_v1 = client.get("/api/v1/health")
        assert res_health_v1.status_code == 200, res_health_v1.text
        data_v1 = res_health_v1.json()
        assert data_v1["status"] == "healthy"
        assert data_v1["database"]["status"] == "connected"
        print("[PASSED] /api/v1/health endpoint verified:", data_v1["database"])

        res_health_root = client.get("/health")
        assert res_health_root.status_code == 200, res_health_root.text
        print("[PASSED] /health root endpoint verified")

        # 2. Admin Login
        admin_login_res = client.post("/api/v1/auth/login", json={
            "email": "admin@platform.edu",
            "password": "Admin@12345"
        })
        assert admin_login_res.status_code == 200, admin_login_res.text
        admin_token_data = admin_login_res.json()
        assert admin_token_data["role"] == "ADMIN"
        admin_token = admin_token_data["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("[PASSED] Seeded Admin login verified (Role: ADMIN)")

        # 3. Student Registration
        student_payload = {
            "email": "sarah.connor@student.edu",
            "password": "SecurePass@2026",
            "full_name": "Sarah Connor",
            "student_id": "STU-2026-999",
            "department": "Mechanical Engineering"
        }
        reg_res = client.post("/api/v1/auth/register", json=student_payload)
        assert reg_res.status_code in [201, 400], reg_res.text
        print("[PASSED] Student registration endpoint verified")

        # 4. Student Login
        student_login_res = client.post("/api/v1/auth/login", json={
            "email": "sarah.connor@student.edu",
            "password": "SecurePass@2026"
        })
        assert student_login_res.status_code == 200, student_login_res.text
        student_token_data = student_login_res.json()
        assert student_token_data["role"] == "STUDENT"
        student_token = student_token_data["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print("[PASSED] Student login verified (Role: STUDENT)")

        # 5. Profile /me endpoint
        me_res = client.get("/api/v1/auth/me", headers=student_headers)
        assert me_res.status_code == 200, me_res.text
        me_data = me_res.json()
        assert me_data["email"] == "sarah.connor@student.edu"
        assert me_data["student_id"] == "STU-2026-999"
        assert me_data["department"] == "Mechanical Engineering"
        print("[PASSED] Student /me profile verified:", me_data["full_name"], f"({me_data['student_id']})")

        # 6. Student accesses Student-only route -> SUCCESS (200)
        stu_role_res = client.get("/api/v1/auth/test-student", headers=student_headers)
        assert stu_role_res.status_code == 200, stu_role_res.text
        print("[PASSED] RBAC: Student authorized for Student route")

        # 7. Student attempts to access Admin-only route -> FORBIDDEN (403)
        forbidden_res = client.get("/api/v1/auth/test-admin", headers=student_headers)
        assert forbidden_res.status_code == 403, f"Expected 403, got {forbidden_res.status_code}"
        print("[PASSED] RBAC: Student strictly blocked from Admin endpoint (HTTP 403 Forbidden)")

        # 8. Admin accesses Admin-only route -> SUCCESS (200)
        admin_role_res = client.get("/api/v1/auth/test-admin", headers=admin_headers)
        assert admin_role_res.status_code == 200, admin_role_res.text
        print("[PASSED] RBAC: Admin authorized for Admin route")

        print("\n========================================================")
        print("ALL BACKEND INTEGRATION & RBAC TESTS PASSED SUCCESSFULLY!")
        print("========================================================\n")


if __name__ == "__main__":
    run_all_tests()
