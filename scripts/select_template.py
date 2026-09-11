"""Choose a project template from a user's instruction or observed feedback text."""

from __future__ import annotations


def select_template(
    templates: list[dict],
    *,
    content: str,
    requested_template: str | None = None,
    default_template: str | None = None,
) -> str:
    """Return an explicit choice first, otherwise score configured route keywords."""
    ids = [str(template.get("id", "")) for template in templates]
    if requested_template:
        if requested_template not in ids:
            raise ValueError(f"unknown requested template: {requested_template}")
        return requested_template

    normalized = content.casefold()
    scores = [
        sum(keyword.casefold() in normalized for keyword in template.get("route_keywords", []) if isinstance(keyword, str))
        for template in templates
    ]
    if scores and max(scores) > 0:
        return ids[scores.index(max(scores))]
    if default_template and default_template in ids:
        return default_template
    if not ids:
        raise ValueError("project has no templates")
    return ids[0]
