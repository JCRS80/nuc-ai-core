from fastapi.testclient import TestClient

from nuc_ai_core.main import app

client = TestClient(app)


def test_health_check_returns_expected_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "online",
        "service": "nuc-ai-core",
        "version": "0.1.0",
        "environment": "nuc-lab",
    }
