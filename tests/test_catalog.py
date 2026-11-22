from engineeringos.catalog import load_catalog, search_roles, get_role, build_learning_path
def test_catalog_integrity():
    data = load_catalog()
    assert data["role_count"] == len(data["roles"])
    assert len({r["id"] for r in data["roles"]}) == len(data["roles"])
    assert len(data["domains"]) >= 10
def test_llm_role_search():
    assert any(r["id"] == "llm-engineer" for r in search_roles("LLM"))
def test_domain_filter():
    result = search_roles(domain="cybersecurity")
    assert result and all(r["domain"] == "Cybersecurity" for r in result)
def test_missing_role():
    assert get_role("not-a-real-role") is None
def test_learning_path():
    plan = build_learning_path("frontend-developer", "beginner", 5)
    assert plan["estimated_hours"] == plan["estimated_weeks"] * 5
    assert len(plan["phases"]) == 4
def test_invalid_path_inputs():
    import pytest
    with pytest.raises(KeyError): build_learning_path("missing")
    with pytest.raises(ValueError): build_learning_path("frontend-developer", "expert")


def test_mcp_server_imports_under_sdk_v2():
    from engineeringos.server import mcp
    assert callable(mcp.tool)


def test_vercel_asgi_app_exposes_mcp_and_health_routes():
    import importlib.util
    from pathlib import Path
    entry = Path(__file__).resolve().parents[1] / "api" / "index.py"
    spec = importlib.util.spec_from_file_location("engineeringos_vercel_entry", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.app
    paths = {route.path for route in app.routes}
    assert "/mcp" in paths
    assert "/health" in paths
