"""
Auth 도메인 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """인증/인가 API 테스트"""

    def test_signup_success(self, client: TestClient):
        """회원가입 성공 테스트"""
        response = client.post(
            "/api/auth/signup",
            json={"user_id": "new_user", "password": "password123"}
        )

        assert response.status_code == 201
        assert "access_token" in response.json()

    def test_signup_duplicate_user(self, client: TestClient):
        """중복 사용자 회원가입 실패 테스트"""
        # 첫 번째 회원가입
        client.post(
            "/api/auth/signup",
            json={"user_id": "duplicate_user", "password": "password123"}
        )

        # 두 번째 회원가입 (중복)
        response = client.post(
            "/api/auth/signup",
            json={"user_id": "duplicate_user", "password": "password123"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_login_success(self, client: TestClient):
        """로그인 성공 테스트"""
        # 회원가입
        client.post(
            "/api/auth/signup",
            json={"user_id": "login_user", "password": "password123"}
        )

        # 로그인
        response = client.post(
            "/api/auth/login",
            json={"user_id": "login_user", "password": "password123"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client: TestClient):
        """잘못된 비밀번호로 로그인 실패 테스트"""
        # 회원가입
        client.post(
            "/api/auth/signup",
            json={"user_id": "wrong_password_user", "password": "password123"}
        )

        # 잘못된 비밀번호로 로그인
        response = client.post(
            "/api/auth/login",
            json={"user_id": "wrong_password_user", "password": "wrong_password"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """존재하지 않는 사용자로 로그인 실패 테스트"""
        response = client.post(
            "/api/auth/login",
            json={"user_id": "nonexistent_user", "password": "password123"}
        )

        assert response.status_code == 404
