import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app


class TestAPI:
    """Test suite for ISTQB Chatbot API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "healthy"
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        with TestClient(app) as client:
            user_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201
            data = response.json()
            assert "token" in data or "message" in data
    
    def test_user_login(self):
        """Test user login endpoint"""
        with TestClient(app) as client:
            # First register a user
            user_data = {
                "name": "Test User",
                "email": "login_test@example.com",
                "password": "testpassword123"
            }
            client.post("/api/auth/register", json=user_data)
            
            # Then try to login
            login_data = {
                "email": "login_test@example.com",
                "password": "testpassword123"
            }
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            data = response.json()
            assert "token" in data or "access_token" in data
    
    def test_certifications_endpoint(self):
        """Test certifications endpoint"""
        with TestClient(app) as client:
            # First get a token
            user_data = {
                "name": "Test User",
                "email": "cert_test@example.com",
                "password": "testpassword123"
            }
            register_response = client.post("/api/auth/register", json=user_data)
            
            if register_response.status_code == 201:
                token_data = register_response.json()
                token = token_data.get("token") or token_data.get("access_token")
                
                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    response = client.get("/api/certifications", headers=headers)
                    assert response.status_code == 200
                    data = response.json()
                    assert isinstance(data, (list, dict))
    
    def test_invalid_endpoint(self):
        """Test handling of invalid endpoints"""
        with TestClient(app) as client:
            response = client.get("/api/invalid-endpoint")
            assert response.status_code == 404


@pytest.mark.asyncio
class TestAsyncAPI:
    """Async test suite for performance testing"""
    
    async def test_concurrent_health_checks(self):
        """Test multiple concurrent health check requests"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            tasks = []
            for _ in range(10):
                tasks.append(ac.get("/health"))
            
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])
