# ChatGPT Integration

## Mentor instructions
Use chatgpt/ENGINEERINGOS.md as the portable instruction set for a supported custom GPT or project instruction surface.

## MCP tools
The server exposes list_domains, search_engineering_roles, get_engineering_role, create_role_learning_path and get_role_capstone.

To connect: deploy to a trusted HTTPS host; configure authenticated Streamable HTTP MCP; add it through the custom connector/app workflow supported by the user's ChatGPT account and workspace; review permissions; test every tool. Workspace approval may be required.

A GitHub repository cannot install itself into ChatGPT. This source package is not yet connected to a live ChatGPT app. The MCP server currently has no OAuth, user accounts or learner-progress storage. Do not expose it as an unauthenticated public service.