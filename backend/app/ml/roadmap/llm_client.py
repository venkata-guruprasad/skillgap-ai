"""Configurable LLM integration for personalized roadmap generation with strict Pydantic validation.

Never logs or exposes LLM_API_KEY. Gracefully returns None when unconfigured or on failure,
allowing the deterministic verified-resource generator to run seamlessly.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field, field_validator

from app.config import settings
from app.ml.roadmap.resource_catalog import get_skill_curriculum, is_trusted_resource_url

logger = logging.getLogger("skillgap_ai.llm_client")


class VerifiedResourceSchema(BaseModel):
    title: str = Field(..., min_length=2, max_length=180)
    source: str = Field(..., min_length=2, max_length=80)
    url: str = Field(..., min_length=10, max_length=500)

    @field_validator("url")
    @classmethod
    def validate_trusted_url(cls, value: str) -> str:
        if not is_trusted_resource_url(value.strip()):
            raise ValueError("Resource URL must use HTTPS on a trusted verified learning domain.")
        return value.strip()


class GeneratedTaskSchema(BaseModel):
    week_label: str = Field(..., min_length=3, max_length=40)
    title: str = Field(..., min_length=4, max_length=220)
    description: str = Field(default="", max_length=600)
    task_type: str = Field(default="study")
    estimated_hours: int = Field(default=3, ge=1, le=40)


class GeneratedPhaseSchema(BaseModel):
    phase_number: int = Field(..., ge=1, le=12)
    timeframe: str = Field(..., min_length=3, max_length=60)
    title: str = Field(..., min_length=4, max_length=180)
    skill_name: str = Field(..., min_length=1, max_length=120)
    priority: str = Field(default="High")
    estimated_hours: int = Field(default=10, ge=2, le=120)
    learning_objectives: List[str] = Field(..., min_length=1)
    weekly_tasks: List[GeneratedTaskSchema] = Field(..., min_length=1)
    practical_exercises: List[str] = Field(..., min_length=1)
    mini_project: str = Field(..., min_length=5, max_length=400)
    assessment_checkpoint: str = Field(..., min_length=5, max_length=400)
    resources: List[VerifiedResourceSchema] = Field(default_factory=list)


class GeneratedRoadmapPlan(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    target_role: str = Field(..., min_length=2, max_length=150)
    duration_days: int = Field(..., ge=30, le=90)
    estimated_weeks: int = Field(..., ge=4, le=13)
    summary_explanation: str = Field(..., min_length=15, max_length=1500)
    prioritized_missing_skills: List[str] = Field(default_factory=list)
    phases: List[GeneratedPhaseSchema] = Field(..., min_length=1)


def is_llm_configured() -> bool:
    """Return True only when both an LLM provider and API key are configured via env vars."""
    provider = (settings.LLM_PROVIDER or "none").strip().lower()
    api_key = (settings.LLM_API_KEY or "").strip()
    return provider in {"openai", "gemini"} and len(api_key) >= 10


def _sanitize_resources_for_phases(plan_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure every phase contains verified trusted URLs (replacing any untrusted LLM links)."""
    for phase in plan_dict.get("phases", []):
        skill_name = phase.get("skill_name", "")
        valid_res = [
            r for r in (phase.get("resources") or [])
            if isinstance(r, dict) and is_trusted_resource_url(str(r.get("url", "")))
        ]
        if not valid_res:
            valid_res = get_skill_curriculum(skill_name)["resources"]
        phase["resources"] = valid_res
    return plan_dict


def _extract_json_block(raw_text: str) -> Optional[Dict[str, Any]]:
    text = (raw_text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def generate_roadmap_via_llm(
    target_role: str,
    duration_days: int,
    resume_skills: List[str],
    missing_skills: List[str],
    weekly_hours: int,
    learning_style: str,
) -> Optional[GeneratedRoadmapPlan]:
    """Call configured LLM provider and strictly validate output with Pydantic. Never exposes API keys."""
    if not is_llm_configured():
        return None

    provider = settings.LLM_PROVIDER.strip().lower()
    api_key = settings.LLM_API_KEY.strip()
    timeout = settings.LLM_TIMEOUT_SECONDS

    curated_urls_hint = {
        skill: get_skill_curriculum(skill)["resources"]
        for skill in missing_skills[:6]
    }

    prompt = (
        f"You are a senior career mentor designing a {duration_days}-day personalized learning roadmap "
        f"for target role '{target_role}'.\n"
        f"Candidate existing skills: {', '.join(resume_skills) or 'None listed'}.\n"
        f"Prioritized missing skills: {', '.join(missing_skills)}.\n"
        f"Weekly budget: {weekly_hours} hours/week. Learning preference: {learning_style}.\n"
        f"Use ONLY verified URLs from this trusted map: {json.dumps(curated_urls_hint)}.\n"
        "Return ONLY valid JSON matching keys: title, target_role, duration_days, estimated_weeks, "
        "summary_explanation, prioritized_missing_skills, phases (array of phase_number, timeframe, "
        "title, skill_name, priority, estimated_hours, learning_objectives, weekly_tasks "
        "[week_label, title, description, task_type, estimated_hours], practical_exercises, "
        "mini_project, assessment_checkpoint, resources [title, source, url])."
    )

    try:
        raw_content = ""
        if provider == "openai":
            base_url = (settings.LLM_BASE_URL or "https://api.openai.com/v1").rstrip("/")
            model = settings.LLM_MODEL or "gpt-4o-mini"
            resp = httpx.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "Return strictly valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            raw_content = resp.json()["choices"][0]["message"]["content"]
        elif provider == "gemini":
            model = settings.LLM_MODEL or "gemini-2.0-flash"
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model}:generateContent"
            )
            resp = httpx.post(
                url,
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"},
                },
                timeout=timeout,
            )
            resp.raise_for_status()
            raw_content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return None

        parsed = _extract_json_block(raw_content)
        if not parsed:
            logger.warning("LLM response did not contain valid JSON; falling back to deterministic generator.")
            return None

        sanitized = _sanitize_resources_for_phases(parsed)
        return GeneratedRoadmapPlan.model_validate(sanitized)
    except Exception as exc:
        # Never include api_key in exception logs
        logger.warning(
            "LLM roadmap generation failed (%s); falling back cleanly to deterministic engine.",
            exc.__class__.__name__,
        )
        return None
