"""Role catalog loading, searching and path generation."""
import json
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[2]
PACKAGE_CATALOG_PATH = Path(__file__).resolve().parent / "roles.json"
CATALOG_PATH = PACKAGE_CATALOG_PATH if PACKAGE_CATALOG_PATH.exists() else ROOT / "data" / "roles.json"
def load_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    roles = data.get("roles")
    if not isinstance(roles, list): raise ValueError("Catalog must contain a roles list")
    ids = [r.get("id") for r in roles]
    if len(ids) != len(set(ids)): raise ValueError("Role IDs must be unique")
    required = {"id", "title", "domain", "mission", "core_competencies", "capstone"}
    for role in roles:
        missing = required - role.keys()
        if missing: raise ValueError(f"Role {role.get(chr(105)+chr(100))} missing {sorted(missing)}")
    return data
def search_roles(query: str = "", domain: str | None = None) -> list[dict[str, Any]]:
    q = query.casefold().strip()
    result = []
    for role in load_catalog()["roles"]:
        if domain and role["domain"].casefold() != domain.casefold(): continue
        haystack = " ".join([role["title"], role["domain"], role["mission"], *role["core_competencies"]]).casefold()
        if not q or q in haystack: result.append(role)
    return result
def get_role(role_id: str) -> dict[str, Any] | None:
    return next((r for r in load_catalog()["roles"] if r["id"] == role_id), None)
def build_learning_path(role_id: str, level: str = "beginner", hours_per_week: int = 7) -> dict[str, Any]:
    role = get_role(role_id)
    if role is None: raise KeyError(f"Unknown role_id: {role_id}")
    if level not in {"beginner", "intermediate", "advanced"}: raise ValueError("Invalid level")
    if not 1 <= hours_per_week <= 60: raise ValueError("hours_per_week must be 1..60")
    weeks = {"beginner": 16, "intermediate": 10, "advanced": 6}[level]
    chunks = [max(1, weeks // 7), max(1, weeks // 4), max(1, weeks // 3)]
    chunks.append(max(1, weeks - sum(chunks)))
    labels = ["Foundations", "Tools and guided practice", "Independent implementation", "Capstone and review"]
    outcomes = ["Explain core concepts and prerequisites.", "Complete practical exercises with feedback.", "Build a working role-specific component.", role["capstone"]]
    return {"role": role["title"], "role_id": role_id, "level": level, "hours_per_week": hours_per_week, "estimated_weeks": weeks, "estimated_hours": weeks * hours_per_week, "competencies": role["core_competencies"], "phases": [{"phase": labels[i], "weeks": chunks[i], "outcome": outcomes[i]} for i in range(4)], "assessment": ["knowledge check", "practical lab", "design or code review", "capstone demonstration", "reflection on trade-offs"], "note": "Planning estimate, not a guarantee of professional mastery."}
