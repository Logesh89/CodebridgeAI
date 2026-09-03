"""Authentication API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_login_sends_otp(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "remember_me": False},
    )
    assert response.status_code == 200
    assert "OTP" in response.json()["message"]


@pytest.mark.asyncio
async def test_verify_otp_invalid(client: AsyncClient):
    await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com"},
    )
    response = await client.post(
        "/api/v1/auth/verify-otp",
        json={"email": "test@example.com", "otp": "000000"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 401
