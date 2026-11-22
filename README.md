# EngineeringOS

An AI-powered engineering role mastery system spanning software, AI/ML/LLMs/agents, data, architecture, cloud, cybersecurity, design, QA, hardware, robotics, games, emerging computing and technical leadership.

## Included
- 276 role profiles across 16 domains.
- ChatGPT mentor instruction pack in `chatgpt/ENGINEERINGOS.md`.
- MCP server for role search, profile retrieval, learning-path generation and capstone briefs.
- Catalog integrity, learning-path and MCP protocol smoke tests, plus GitHub Actions CI.
- Curriculum, architecture, integration and contribution documentation.

## Quick start
Requires Python 3.11+.

    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev]'
    pytest
    python -m engineeringos.server

The Vercel deployment exposes Streamable HTTP at `/api/mcp` and a health check at `/api/health`. For a self-hosted server, configure `ENGINEERINGOS_HOST` and `ENGINEERINGOS_PORT`. Do not expose it publicly without HTTPS, authentication, authorization, rate limits and a security review.

## ChatGPT
Use `chatgpt/ENGINEERINGOS.md` as the portable mentor instruction set. For tool access, deploy the MCP server to a trusted HTTPS host and connect it through a supported ChatGPT MCP/app integration. A GitHub repository cannot install itself into ChatGPT; account/workspace support and user/admin approval may be required. See `docs/CHATGPT-INTEGRATION.md`.

## Important scope note
This first release is a broad role atlas, not a full textbook for every role. Role profiles share domain-level competency baselines. Role-specific syllabi, verified learning resources, lab manuals and assessment banks are the next expansion layer.

## Layout
- `data/roles.json` — role catalog
- `chatgpt/ENGINEERINGOS.md` — mentor instructions
- `src/engineeringos` — catalog service and MCP server
- `tests` — automated tests
- `docs` — architecture, curriculum and integration

MIT licensed. See LICENSE.
