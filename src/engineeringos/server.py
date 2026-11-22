"""EngineeringOS MCP server."""
import os
from mcp.server import MCPServer
from engineeringos.catalog import load_catalog, search_roles, get_role, build_learning_path
mcp = MCPServer("EngineeringOS")
@mcp.tool()
def list_domains() -> list[str]:
    """List engineering domains in the role atlas."""
    return load_catalog()["domains"]
@mcp.tool()
def search_engineering_roles(query: str = "", domain: str | None = None) -> list[dict]:
    """Search role titles, missions, domains and competencies."""
    return search_roles(query, domain)
@mcp.tool()
def get_engineering_role(role_id: str) -> dict | None:
    """Retrieve a role profile by stable slug, e.g. llm-engineer."""
    return get_role(role_id)
@mcp.tool()
def create_role_learning_path(role_id: str, level: str = "beginner", hours_per_week: int = 7) -> dict:
    """Create a staged plan; level is beginner, intermediate or advanced."""
    return build_learning_path(role_id, level, hours_per_week)
@mcp.tool()
def get_role_capstone(role_id: str) -> dict:
    """Get a role capstone and competencies."""
    role = get_role(role_id)
    if role is None: raise ValueError(f"Unknown role_id: {role_id}")
    return {"role": role["title"], "capstone": role["capstone"], "competencies": role["core_competencies"]}
def main() -> None:
    """Run local Streamable HTTP MCP server."""
    mcp.settings.host = os.getenv("ENGINEERINGOS_HOST", "127.0.0.1")
    mcp.settings.port = int(os.getenv("ENGINEERINGOS_PORT", "8000"))
    mcp.run(transport="streamable-http")
if __name__ == "__main__": main()
