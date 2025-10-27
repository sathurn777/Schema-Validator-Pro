from fastapi.testclient import TestClient
import types

from backend.main import app


def test_generate_records_success_false_when_invalid(monkeypatch):
    client = TestClient(app)

    # Patch DI to return a fake validator that forces invalid result
    from backend.routers import schema as schema_router_module

    class FakeValidator:
        def validate(self, _schema):
            return False, ["forced-error"], []

        def calculate_completeness_score(self, _schema):
            return 0

    def fake_get_schema_validator():
        return FakeValidator()

    calls = {}

    def fake_record_schema_generation(schema_type: str, duration: float, completeness: int, success: bool):
        # capture parameters for assertion
        calls["args"] = {
            "schema_type": schema_type,
            "duration": duration,
            "completeness": completeness,
            "success": success,
        }

    # Override FastAPI dependency for the route
    original_dep = schema_router_module.get_schema_validator
    app.dependency_overrides[original_dep] = fake_get_schema_validator

    try:
        monkeypatch.setattr(schema_router_module, "record_schema_generation", fake_record_schema_generation)

        payload = {
            "schema_type": "Article",
            "content": "Title\nBody",
            "url": "https://example.com/x"
        }
        resp = client.post("/api/v1/schema/generate", json=payload)
        # Debug aid if validation fails
        print("resp:", resp.status_code, resp.text)
        assert resp.status_code == 200
        assert "args" in calls, "metrics should be recorded"
        assert calls["args"]["success"] is False
    finally:
        # Clean up dependency override to avoid affecting other tests
        app.dependency_overrides.clear()

