# Architecture

EngineeringOS separates the versioned role catalog, catalog service, MCP adapter, ChatGPT mentor instructions and evaluation suite. The role atlas is structured data; teaching behaviour is defined independently from the transport.

Each role has a stable slug, title, domain, mission, competency baseline, learning sequence and observable capstone. The first release uses shared domain-level competency baselines. It is a broad role atlas, not a fully authored textbook for every role; role-specific syllabi, references, labs and assessment banks should be expanded and reviewed incrementally.

The MCP server exposes read-oriented discovery and planning tools. It does not execute arbitrary code, persist learner records or perform privileged actions.

Before internet exposure, add HTTPS, authentication, authorization, rate limits, audit logging, input validation and a privacy/retention policy. Isolate any future code execution in disposable sandboxes.