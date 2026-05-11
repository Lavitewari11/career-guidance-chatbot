from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMSettings:
    gemini_api_key: Optional[str]
    groq_api_key: Optional[str]
    gemini_model: str
    groq_model: str
    temperature: float


def load_settings() -> LLMSettings:
    load_dotenv(override=True)

    import os

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")

    gemini_model = os.getenv("GEMINI_MODEL", "gemini/gemini-2.0-flash")
    groq_model = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")

    try:
        temperature = float(os.getenv("TEMPERATURE", "0.4"))
    except ValueError:
        temperature = 0.4

    return LLMSettings(
        gemini_api_key=gemini_api_key,
        groq_api_key=groq_api_key,
        gemini_model=gemini_model,
        groq_model=groq_model,
        temperature=temperature,
    )


def build_crewai_llm(provider: str):
    from crewai import LLM

    settings = load_settings()

    if provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY in .env file.")
        return LLM(
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
            temperature=settings.temperature,
        )

    if provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in .env file.")
        return LLM(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=settings.temperature,
        )

    raise ValueError("Unknown provider. Use 'gemini' or 'groq'.")


def preferred_provider_order() -> list[str]:
    settings = load_settings()

    order: list[str] = []

    if settings.gemini_api_key:
        order.append("gemini")

    if settings.groq_api_key:
        order.append("groq")

    return order