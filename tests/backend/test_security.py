"""Security utility tests."""

from app.core.security import (
    create_access_token,
    decode_token,
    generate_otp,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    hashed = get_password_hash("testpassword")
    assert verify_password("testpassword", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_otp_generation():
    otp = generate_otp(6)
    assert len(otp) == 6
    assert otp.isdigit()


def test_jwt_token():
    token = create_access_token({"sub": "test-user", "email": "test@example.com", "role": "developer"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "test-user"
    assert payload["type"] == "access"
