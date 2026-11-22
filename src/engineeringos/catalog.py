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
    if not isinstance(roles, list):
        raise ValueError("Catalog must contain a roles list")
    ids = [role.get("id") for role in roles]
    if len(ids) != len(set(ids)):
        raise ValueError("Role IDs must be unique")

    required = {"id", "title", "domain", "mission", "core_competencies", "capstone"}
    for role in roles:
        missing = required - role.keys()
        if missing:
            raise ValueError(f"Role {role.get('id')} missing {sorted(missing)}")
    return data


def search_roles(query: str = "", domain: str | None = None) -> list[dict[str, Any]]:
    q = query.casefold().strip()
    result = []
    for role in load_catalog()["roles"]:
        if domain and role["domain"].casefold() != domain.casefold():
            continue
        haystack = " ".join(
            [role["title"], role["domain"], role["mission"], *role["core_competencies"]]
        ).casefold()
        if not q or q in haystack:
            result.append(role)
    return result


def get_role(role_id: str) -> dict[str, Any] | None:
    return next((role for role in load_catalog()["roles"] if role["id"] == role_id), None)


def build_learning_path(
    role_id: str, level: str = "beginner", hours_per_week: int = 7
) -> dict[str, Any]:
    """Build a staged, role-specific plan with deliverables and review gates."""
    role = get_role(role_id)
    if role is None:
        raise KeyError(f"Unknown role_id: {role_id}")
    if level not in {"beginner", "intermediate", "advanced"}:
        raise ValueError("Invalid level")
    if not 1 <= hours_per_week <= 60:
        raise ValueError("hours_per_week must be 1..60")

    weeks = {"beginner": 16, "intermediate": 10, "advanced": 6}[level]
    chunks = [max(1, weeks // 7), max(1, weeks // 4), max(1, weeks // 3)]
    chunks.append(max(1, weeks - sum(chunks)))

    competencies = role["core_competencies"]
    focus_groups: list[list[str]] = [[], [], []]
    for index, competency in enumerate(competencies):
        group_index = min(index * 3 // max(len(competencies), 1), 2)
        focus_groups[group_index].append(competency)

    phases = [
        {
            "phase": "Foundations",
            "weeks": chunks[0],
            "focus_competencies": focus_groups[0],
            "outcome": f"Explain the mission of {role['title']} and its foundational competencies.",
            "practice": [
                "Create a role map showing the systems, people and decisions this role touches.",
                "Write concise notes defining each assigned competency in your own words.",
            ],
            "deliverable": "A role map and competency glossary.",
            "assessment_criteria": [
                "Explain the role mission without relying on copied definitions.",
                "Connect each assigned competency to a concrete responsibility.",
            ],
        },
        {
            "phase": "Tools and guided practice",
            "weeks": chunks[1],
            "focus_competencies": focus_groups[1],
            "outcome": (
                "Apply the assigned competencies through guided workflows: "
                + ", ".join(focus_groups[1] or competencies)
                + "."
            ),
            "practice": [
                "Set up a reproducible practice environment and document the tools used.",
                "Complete one guided exercise for each assigned competency.",
            ],
            "deliverable": "A reproducible environment and guided-lab evidence.",
            "assessment_criteria": [
                "Repeat the workflow from written instructions.",
                "Explain the purpose and limitations of each tool used.",
            ],
        },
        {
            "phase": "Independent implementation",
            "weeks": chunks[2],
            "focus_competencies": focus_groups[2],
            "outcome": (
                f"Design, build and test an independent {role['title']} work sample "
                "using the role's competency set."
            ),
            "practice": [
                "Translate a small problem into acceptance criteria before implementation.",
                "Build a working artefact and test it against those criteria.",
            ],
            "deliverable": "An independently built work sample with tests and a short design note.",
            "assessment_criteria": [
                "Demonstrate that the artefact meets its stated acceptance criteria.",
                "Identify at least one limitation and explain a reasonable trade-off.",
            ],
        },
        {
            "phase": "Capstone and review",
            "weeks": chunks[3],
            "focus_competencies": competencies,
            "outcome": role["capstone"],
            "practice": [
                "Complete the capstone and preserve the decisions, tests and evidence.",
                "Present the result, explain trade-offs and identify the next improvement.",
            ],
            "deliverable": role["capstone"],
            "assessment_criteria": [
                "Demonstrate the capstone against explicit success criteria.",
                "Defend key design choices with evidence.",
                "State remaining risks, limitations and follow-up work.",
            ],
        },
    ]

    return {
        "role": role["title"],
        "role_id": role_id,
        "domain": role["domain"],
        "mission": role["mission"],
        "level": level,
        "hours_per_week": hours_per_week,
        "estimated_weeks": weeks,
        "estimated_hours": weeks * hours_per_week,
        "competencies": competencies,
        "phases": phases,
        "weekly_rhythm": [
            {"activity": "Concept study and notes", "share_percent": 25},
            {"activity": "Hands-on building", "share_percent": 50},
            {"activity": "Testing and review", "share_percent": 15},
            {"activity": "Documentation and reflection", "share_percent": 10},
        ],
        "portfolio_artifacts": [phase["deliverable"] for phase in phases],
        "assessment": [
            "knowledge check",
            "practical lab",
            "design or code review",
            "capstone demonstration",
            "reflection on trade-offs",
        ],
        "note": "Planning estimate, not a guarantee of professional mastery.",
    }
