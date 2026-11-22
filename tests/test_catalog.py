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
    with pytest.raises(KeyError):
        build_learning_path("missing")
    with pytest.raises(ValueError):
        build_learning_path("frontend-developer", "expert")

def test_mcp_server_imports_under_sdk_v2():
    from engineeringos.server import mcp
    assert callable(mcp.tool)

def load_vercel_app():
    import importlib.util
    from pathlib import Path
    entry = Path(__file__).resolve().parents[1] / "api" / "index.py"
    spec = importlib.util.spec_from_file_location("engineeringos_vercel_entry", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_vercel_asgi_app_exposes_mcp_and_health_routes():
    module = load_vercel_app()
    paths = {route.path for route in module.app.routes}
    assert "/api/mcp" in paths
    assert "/api/health" in paths

def test_mcp_initialize_tools_list_and_tool_call_over_asgi():
    from starlette.testclient import TestClient

    module = load_vercel_app()
    base_headers = {
        "host": "engineeringos-alonefxs-projects.vercel.app",
        "origin": "https://chatgpt.com",
        "accept": "application/json, text/event-stream",
    }
    with TestClient(module.app) as client:
        health = client.get("/api/health", headers={"host": base_headers["host"]})
        assert health.status_code == 200
        assert health.json()["role_count"] == 276

        initialized = client.post(
            "/api/mcp",
            headers={**base_headers, "content-type": "application/json"},
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "engineeringos-ci", "version": "1.0"},
                },
            },
        )
        assert initialized.status_code == 200, initialized.text
        protocol_version = initialized.json()["result"]["protocolVersion"]

        protocol_headers = {
            **base_headers,
            "content-type": "application/json",
            "MCP-Protocol-Version": protocol_version,
        }
        tools_response = client.post(
            "/api/mcp",
            headers=protocol_headers,
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        assert tools_response.status_code == 200, tools_response.text
        tool_names = {tool["name"] for tool in tools_response.json()["result"]["tools"]}
        assert {
            "list_domains",
            "search_engineering_roles",
            "get_engineering_role",
            "create_role_learning_path",
            "get_role_capstone",
        } <= tool_names

        search_response = client.post(
            "/api/mcp",
            headers=protocol_headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_engineering_roles",
                    "arguments": {"query": "LLM"},
                },
            },
        )
        assert search_response.status_code == 200, search_response.text
        assert "llm-engineer" in search_response.text


def test_learning_path_contains_role_specific_deliverables_and_assessment():
    role = get_role("llm-engineer")
    plan = build_learning_path("llm-engineer", "beginner", 7)

    assert len(plan["phases"]) == 4
    assert sum(phase["weeks"] for phase in plan["phases"]) == plan["estimated_weeks"]
    assert plan["phases"][0]["focus_competencies"]
    covered = {
        competency
        for phase in plan["phases"]
        for competency in phase["focus_competencies"]
    }
    assert set(role["core_competencies"]) <= covered
    assert plan["phases"][-1]["deliverable"] == role["capstone"]
    assert all(phase["assessment_criteria"] for phase in plan["phases"])


def test_learning_paths_generate_for_every_role_and_level():
    for role in load_catalog()["roles"]:
        for level in ("beginner", "intermediate", "advanced"):
            plan = build_learning_path(role["id"], level, 5)
            assert plan["role_id"] == role["id"]
            assert sum(phase["weeks"] for phase in plan["phases"]) == plan["estimated_weeks"]
            covered = {
                competency
                for phase in plan["phases"]
                for competency in phase["focus_competencies"]
            }
            assert set(role["core_competencies"]) <= covered
            assert plan["phases"][-1]["deliverable"] == role["capstone"]
            assert sum(item["share_percent"] for item in plan["weekly_rhythm"]) == 100
