from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict

from langchain_core.prompts import ChatPromptTemplate


SECTION_PROFILE = "PROFILE_ANALYSIS"
SECTION_CAREERS = "CAREER_OPTIONS"
SECTION_ROADMAP = "STUDY_ROADMAP"
SECTION_LEARNING = "COURSES_CERTIFICATIONS"
SECTION_JOB_PREP = "JOB_PREPARATION"


@dataclass
class UserProfile:
    name: str
    education: str
    skills: str
    interests: str
    strengths: str
    weaknesses: str
    experience_level: str
    career_goal: str


def _profile_as_text(profile: UserProfile) -> str:
    template = ChatPromptTemplate.from_template(
        "User Profile:\n"
        "- Name: {name}\n"
        "- Education: {education}\n"
        "- Skills: {skills}\n"
        "- Interests: {interests}\n"
        "- Strengths: {strengths}\n"
        "- Weaknesses: {weaknesses}\n"
        "- Experience level: {experience_level}\n"
        "- Career goal: {career_goal}\n"
    )
    return template.format_messages(**asdict(profile))[0].content


def build_career_guidance_crew(profile: UserProfile, llm):
    from crewai import Agent, Crew, Process, Task

    profile_text = _profile_as_text(profile)

    career_agent = Agent(
        role="Career Guidance Expert",
        goal="Generate a complete personalized career plan with profile analysis, career options, roadmap, learning resources, and job preparation tips.",
        backstory=(
            "You are an expert career counselor, learning roadmap planner, and job preparation mentor. "
            "You give practical, beginner-friendly, structured, and realistic guidance."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    final_task = Task(
        description=(
            "Create a complete personalized career guidance report for this user.\n\n"
            f"{profile_text}\n\n"
            "VERY IMPORTANT:\n"
            "Return ALL sections below exactly with same headings.\n"
            "Do not skip any heading.\n"
            "Use markdown format.\n\n"
            "## PROFILE_ANALYSIS\n"
            "Include:\n"
            "- Strong areas\n"
            "- Weak/improvement areas\n"
            "- Short profile summary\n"
            "- 3 specific next steps\n\n"
            "## CAREER_OPTIONS\n"
            "Suggest 5 realistic career options. For each option include:\n"
            "- Why it matches\n"
            "- First steps\n"
            "- Future scope\n\n"
            "## STUDY_ROADMAP\n"
            "Create a practical 3-month roadmap. Include:\n"
            "- Week-wise plan\n"
            "- Tools/technologies\n"
            "- Mini projects\n\n"
            "## COURSES_CERTIFICATIONS\n"
            "Recommend:\n"
            "- Courses\n"
            "- Certifications\n"
            "- YouTube channels\n"
            "- Practice platforms\n\n"
            "## JOB_PREPARATION\n"
            "Include:\n"
            "- Resume tips\n"
            "- LinkedIn tips\n"
            "- GitHub/portfolio tips\n"
            "- Interview preparation plan\n"
            "- 5 portfolio project ideas\n\n"
            "Keep answer simple, clear, practical, and suitable for a student/fresher."
        ),
        agent=career_agent,
        expected_output="A complete career guidance report with all five exact markdown headings.",
    )

    return Crew(
        agents=[career_agent],
        tasks=[final_task],
        process=Process.sequential,
        verbose=False,
    )


def split_sections(full_text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}

    text = full_text.strip()

    # Clean old marker style if model uses it
    text = text.replace("<<<END_SECTION>>>", "")
    text = re.sub(r"<<<SECTION:(.*?)>>>", r"## \1", text)

    section_order = [
        SECTION_PROFILE,
        SECTION_CAREERS,
        SECTION_ROADMAP,
        SECTION_LEARNING,
        SECTION_JOB_PREP,
    ]

    heading_pattern = re.compile(
        r"(?im)^\s*#{1,3}\s*"
        r"(PROFILE_ANALYSIS|CAREER_OPTIONS|STUDY_ROADMAP|COURSES_CERTIFICATIONS|JOB_PREPARATION)"
        r"\s*:?\s*$"
    )

    matches = list(heading_pattern.finditer(text))

    if matches:
        for i, match in enumerate(matches):
            section_name = match.group(1).upper().strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            if section_name in section_order and body:
                sections[section_name] = body

    # Fallback if model writes normal headings instead of exact ones
    if not sections:
        fallback_headings = {
            SECTION_PROFILE: ["profile analysis", "profile summary"],
            SECTION_CAREERS: ["career options", "career paths"],
            SECTION_ROADMAP: ["study roadmap", "roadmap"],
            SECTION_LEARNING: ["courses", "certifications", "learning resources"],
            SECTION_JOB_PREP: ["job preparation", "resume tips", "interview"],
        }

        lower_text = text.lower()
        found = []

        for key, names in fallback_headings.items():
            for name in names:
                idx = lower_text.find(name)
                if idx != -1:
                    found.append((idx, key))
                    break

        found.sort()

        for i, (idx, key) in enumerate(found):
            next_idx = found[i + 1][0] if i + 1 < len(found) else len(text)
            body = text[idx:next_idx].strip()
            if body:
                sections[key] = body

    # Last fallback: show complete output under profile instead of "Not generated"
    if not sections:
        sections[SECTION_PROFILE] = text

    return sections