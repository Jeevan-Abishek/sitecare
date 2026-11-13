from typing import Optional

# Points per verified issue category. Kept additive with caps to avoid
# double-counting related issues.
POINTS = {
    "unavailable": 20,
    "invalid_ssl": 20,
    "broken_internal_links": 20,
    "missing_mobile_viewport": 15,
    "slow_response": 10,
    "placeholder_content": 10,
    "missing_metadata": 5,
    "missing_favicon": 3,
    "broken_images": 3,
    "broken_external_links": 3,
    "old_copyright": 2,
}

MAX_SCORE = 100


def compute_score(flags: dict) -> int:
    score = 0
    if flags.get("unavailable"):
        score += POINTS["unavailable"]
    if flags.get("invalid_ssl"):
        score += POINTS["invalid_ssl"]
    if flags.get("broken_internal_links"):
        score += POINTS["broken_internal_links"]
    if flags.get("missing_mobile_viewport"):
        score += POINTS["missing_mobile_viewport"]
    if flags.get("slow_response"):
        score += POINTS["slow_response"]
    if flags.get("placeholder_content"):
        score += POINTS["placeholder_content"]
    if flags.get("missing_metadata"):
        score += POINTS["missing_metadata"]
    if flags.get("missing_favicon"):
        score += POINTS["missing_favicon"]
    if flags.get("broken_images"):
        score += POINTS["broken_images"]
    if flags.get("broken_external_links"):
        score += POINTS["broken_external_links"]
    if flags.get("old_copyright"):
        score += POINTS["old_copyright"]
    return min(score, MAX_SCORE)


def priority_for_score(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def service_for_flags(flags: dict, score: int) -> str:
    if flags.get("unavailable") or flags.get("invalid_ssl"):
        return "Website recovery & SSL restoration"
    if flags.get("broken_internal_links") or flags.get("missing_mobile_viewport"):
        return "Technical website repair"
    if score >= 40:
        return "Website maintenance package"
    if score >= 20:
        return "Basic website health check"
    return "Periodic website monitoring"
