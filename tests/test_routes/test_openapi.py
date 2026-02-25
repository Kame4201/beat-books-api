"""Tests for OpenAPI schema validation (issue #23)."""

import pytest


class TestOpenAPISchema:
    """Validate the OpenAPI schema structure and content."""

    def test_openapi_endpoint_returns_200(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_returns_valid_json(self, client):
        response = client.get("/openapi.json")
        schema = response.json()
        assert isinstance(schema, dict)

    def test_openapi_version_is_3x(self, client):
        schema = client.get("/openapi.json").json()
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.")

    def test_openapi_has_info_block(self, client):
        schema = client.get("/openapi.json").json()
        info = schema["info"]
        assert info["title"] == "BeatTheBooks API"
        assert info["version"] == "1.0.0"

    def test_openapi_has_paths(self, client):
        schema = client.get("/openapi.json").json()
        assert "paths" in schema
        assert len(schema["paths"]) > 0


class TestAllRoutesDocumented:
    """Ensure every registered route appears in the OpenAPI schema."""

    EXPECTED_PATHS = [
        "/",
        "/scrape/{team}/{year}",
        "/scrape/{year}",
        "/scrape/excel",
        "/teams/{team}/stats",
        "/players",
        "/games",
        "/standings",
        "/predictions/predict",
        "/predictions/backtest/{run_id}",
        "/predictions/models",
        "/metrics",
    ]

    def test_all_routes_present(self, client):
        schema = client.get("/openapi.json").json()
        paths = set(schema["paths"].keys())
        for expected in self.EXPECTED_PATHS:
            assert expected in paths, f"Route {expected} missing from OpenAPI schema"

    def test_no_undocumented_routes(self, client):
        schema = client.get("/openapi.json").json()
        paths = set(schema["paths"].keys())
        expected = set(self.EXPECTED_PATHS)
        extra = paths - expected
        assert not extra, f"Undocumented routes found in schema: {extra}"


class TestResponseModelsInSchema:
    """Verify response models are referenced in the schema."""

    def test_prediction_response_model_defined(self, client):
        schema = client.get("/openapi.json").json()
        schemas = schema.get("components", {}).get("schemas", {})
        assert "PredictionResponse" in schemas

    def test_backtest_response_model_defined(self, client):
        schema = client.get("/openapi.json").json()
        schemas = schema.get("components", {}).get("schemas", {})
        assert "BacktestResponse" in schemas

    def test_models_list_response_model_defined(self, client):
        schema = client.get("/openapi.json").json()
        schemas = schema.get("components", {}).get("schemas", {})
        assert "ModelsListResponse" in schemas

    def test_prediction_response_has_required_fields(self, client):
        schema = client.get("/openapi.json").json()
        pred_schema = schema["components"]["schemas"]["PredictionResponse"]
        props = pred_schema["properties"]
        expected_fields = [
            "home_team",
            "away_team",
            "home_win_probability",
            "away_win_probability",
            "predicted_spread",
            "model_version",
            "feature_version",
            "edge_vs_market",
            "recommended_bet_size",
            "bet_recommendation",
        ]
        for field in expected_fields:
            assert field in props, f"PredictionResponse missing field: {field}"

    def test_backtest_response_has_required_fields(self, client):
        schema = client.get("/openapi.json").json()
        bt_schema = schema["components"]["schemas"]["BacktestResponse"]
        props = bt_schema["properties"]
        expected_fields = [
            "run_id",
            "start_date",
            "end_date",
            "total_games",
            "correct_predictions",
            "accuracy",
            "total_profit",
            "roi",
        ]
        for field in expected_fields:
            assert field in props, f"BacktestResponse missing field: {field}"


class TestEndpointMethods:
    """Verify correct HTTP methods are documented for each endpoint."""

    def test_health_is_get(self, client):
        schema = client.get("/openapi.json").json()
        assert "get" in schema["paths"]["/"]

    def test_scrape_excel_is_post(self, client):
        schema = client.get("/openapi.json").json()
        assert "post" in schema["paths"]["/scrape/excel"]

    def test_predict_is_get(self, client):
        schema = client.get("/openapi.json").json()
        assert "get" in schema["paths"]["/predictions/predict"]

    def test_endpoints_have_tags(self, client):
        schema = client.get("/openapi.json").json()
        for path, methods in schema["paths"].items():
            for method, details in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    assert "tags" in details, f"{method.upper()} {path} has no tags"
