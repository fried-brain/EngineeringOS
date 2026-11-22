"""Vercel ASGI entrypoint for the EngineeringOS MCP server."""
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from engineeringos.catalog import load_catalog, search_roles, get_role, build_learning_path

mcp = FastMCP("EngineeringOS")

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
def create_role_learning_path(role_id: str, level: str = "beginner", hours_per_week: int = 7) -> dict:
    """Create a staged learning path; level: beginner, intermediate or advanced."""
    return build_learning_path(role_id, level, hours_per_week)

@mcp.tool()
def get_role_capstone(role_id: str) -> dict:
    """Return the capstone brief and competency baseline for a role."""
    role = get_role(role_id)
    if role is None:
        raise ValueError(f"Unknown role_id: {role_id}")
    return {"role": role["title"], "capstone": role["capstone"], "competencies": role["core_competencies"]}

@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> Response:
    return JSONResponse({"status": "ok", "service": "EngineeringOS", "role_count": load_catalog()["role_count"]})

# Vercel terminates TLS and controls the public Host header. Replace this allowlist
# if the assigned project domain changes.
security = TransportSecuritySettings(
    allowed_hosts=["engineeringos.vercel.app", "engineeringos.vercel.app:*"],
    allowed_origins=["https://chatgpt.com", "https://chat.openai.com"],
)
app = mcp.streamable_http_app(transport_security=security, json_response=True, stateless_http=True)
