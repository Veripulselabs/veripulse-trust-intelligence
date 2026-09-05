import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_valid_email_and_phone():
    payload = {
        "email": "contact@apple.com",
        "phone": "+14155552671",
        "country_code": "US"
    }
    res = client.post("/v1/trust-score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["trust_score"] >= 70
    assert data["recommended_action"] in ["ALLOW", "FLAG_FOR_REVIEW"]
    assert "execution_time_ms" in data

def test_disposable_email_detection():
    payload = {"email": "burner123@mailinator.com"}
    res = client.post("/v1/trust-score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["trust_score"] <= 20
    assert data["recommended_action"] == "BLOCK"
    assert data["email_intelligence"]["is_disposable"] is True

def test_voip_phone_detection():
    payload = {"phone": "+12025550143"}
    res = client.post("/v1/trust-score", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "phone_intelligence" in data
    assert data["phone_intelligence"]["is_valid"] is True

def test_empty_request_rejected():
    res = client.post("/v1/trust-score", json={})
    assert res.status_code == 400

def test_batch_trust_score():
    payload = {
        "items": [
            {"email": "contact@apple.com", "phone": "+14155552671"},
            {"email": "burner123@mailinator.com"}
        ]
    }
    res = client.post("/v1/trust-score/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_processed"] == 2
    assert len(data["results"]) == 2
