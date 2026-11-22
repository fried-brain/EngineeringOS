"""Vercel ASGI entrypoint for the EngineeringOS MCP server and REST API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from engineeringos.catalog import (
    load_catalog,
    search_roles,
    get_role,
    build_learning_path,
)

mcp = MCPServer("EngineeringOS")


@mcp.tool()
def list_domains() -> list[str]:
    """List all engineering domains in the role atlas."""
    return load_catalog()["domains"]


@mcp.tool()
def search_engineering_roles(query: str = "", domain: str | None = None) -> list[dict]:
    """Search role titles, domains, missions and competency keywords."""
    return search_roles(query, domain)


@mcp.tool()
def get_engineering_role(role_id: str) -> dict | None:
    """Retrieve a role profile by stable slug, e.g. llm-engineer."""
    return get_role(role_id)


@mcp.tool()
def create_role_learning_path(
    role_id: str, level: str = "beginner", hours_per_week: int = 7
) -> dict:
    """Create a staged learning path; level: beginner, intermediate or advanced."""
    return build_learning_path(role_id, level, hours_per_week)


@mcp.tool()
def get_role_capstone(role_id: str) -> dict:
    """Return the capstone brief and competency baseline for a role."""
    role = get_role(role_id)
    if role is None:
        raise ValueError(f"Unknown role_id: {role_id}")
    return {
        "role": role["title"],
        "capstone": role["capstone"],
        "competencies": role["core_competencies"],
    }


@mcp.custom_route("/api/health", methods=["GET"])
async def health(_: Request) -> Response:
    return JSONResponse(
        {
            "status": "ok",
            "service": "EngineeringOS",
            "role_count": load_catalog()["role_count"],
        }
    )


@mcp.custom_route("/api/catalog", methods=["GET"])
async def catalog(request: Request) -> Response:
    query = request.query_params.get("q", "")
    domain = request.query_params.get("domain") or None
    roles = search_roles(query, domain)
    data = load_catalog()
    return JSONResponse(
        {
            "domains": data["domains"],
            "role_count": data["role_count"],
            "result_count": len(roles),
            "roles": roles,
        }
    )


@mcp.custom_route("/api/role", methods=["GET"])
async def role_detail(request: Request) -> Response:
    role_id = request.query_params.get("id", "")
    role = get_role(role_id)
    if role is None:
        return JSONResponse({"error": "Role not found"}, status_code=404)
    return JSONResponse(role)


@mcp.custom_route("/api/learning-path", methods=["GET"])
async def learning_path(request: Request) -> Response:
    role_id = request.query_params.get("role_id", "")
    level = request.query_params.get("level", "beginner")
    try:
        hours = int(request.query_params.get("hours_per_week", "7"))
        plan = build_learning_path(role_id, level, hours)
    except KeyError:
        return JSONResponse({"error": "Role not found"}, status_code=404)
    except (ValueError, TypeError) as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    return JSONResponse(plan)


security = TransportSecuritySettings(
    allowed_hosts=[
        "engineeringos-alonefxs-projects.vercel.app",
        "engineeringos-alonefxs-projects.vercel.app:*",
        "engineeringos-git-main-alonefxs-projects.vercel.app",
        "engineeringos-git-main-alonefxs-projects.vercel.app:*",
    ],
    allowed_origins=["https://chatgpt.com", "https://chat.openai.com"],
)

app = mcp.streamable_http_app(
    streamable_http_path="/api/mcp",
    transport_security=security,
    json_response=True,
    stateless_http=True,
)
