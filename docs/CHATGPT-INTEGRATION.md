# ChatGPT Integration

## Mentor instructions
Use chatgpt/ENGINEERINGOS.md as the portable instruction set for a supported custom GPT or project instruction surface.

## Hosted MCP endpoint
The public Vercel deployment exposes Streamable HTTP at `https://engineeringos-alonefxs-projects.vercel.app/api/mcp` and a health check at `/api/health`.

The current MCP tools are read-only: list domains, search role profiles, retrieve a role, generate a learning path and retrieve a capstone brief. The endpoint contains no user records and has no write-capable tools. It is intentionally public; it does not implement OAuth or per-user authentication. Do not add private data or write tools without first implementing and reviewing an authentication/authorization layer and abuse controls.

## Connect in ChatGPT
Where custom MCP apps/connectors are enabled for the account or workspace, add a remote MCP server using the HTTPS endpoint above, review the listed tools and approve the connection. Availability and exact setup controls depend on ChatGPT plan and workspace policy. If custom MCP connections are unavailable, use the mentor instructions directly in a ChatGPT project or supported custom GPT.

A GitHub repository or Vercel deployment cannot install itself into ChatGPT. The user must complete the final connector authorization in ChatGPT. This project does not claim a live ChatGPT connection until that approval is completed.
