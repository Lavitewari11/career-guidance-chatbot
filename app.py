from __future__ import annotations

import traceback
from typing import Optional

import streamlit as st

from agents import (
    SECTION_CAREERS,
    SECTION_JOB_PREP,
    SECTION_LEARNING,
    SECTION_PROFILE,
    SECTION_ROADMAP,
    UserProfile,
    build_career_guidance_crew,
    split_sections,
)
from llm_config import build_crewai_llm, preferred_provider_order


def _set_page_style() -> None:
    st.set_page_config(
        page_title="Career Guidance Chatbot",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        """
<style>
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stHeader"] {
    display: none !important;
}

.stApp {
    background:
      radial-gradient(circle at 10% 10%, rgba(124,58,237,.20), transparent 30%),
      radial-gradient(circle at 90% 20%, rgba(37,99,235,.15), transparent 28%),
      linear-gradient(135deg, #fbfbff 0%, #f1f4ff 45%, #f7f0ff 100%);
    color: #0f172a;
}

.block-container {
    padding-top: 1.2rem !important;
    max-width: 1220px !important;
}

html, body, p, div, span, label {
    color: #0f172a !important;
    font-family: Inter, Segoe UI, sans-serif;
}

.cg-navbar {
    background: rgba(255,255,255,.86);
    border: 1px solid rgba(15,23,42,.10);
    border-radius: 22px;
    padding: 15px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 18px 45px rgba(15,23,42,.08);
    margin-bottom: 34px;
}

.cg-brand {
    font-size: 21px;
    font-weight: 900;
}

.cg-brand span {
    color: #7c3aed !important;
}

.cg-menu {
    display: flex;
    gap: 18px;
    font-weight: 700;
    font-size: 14px;
}

.cg-menu span {
    padding: 8px 12px;
    border-radius: 999px;
}

.cg-menu span:hover {
    background: #eef2ff;
}

.cg-deploy {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white !important;
    padding: 10px 20px;
    border-radius: 15px;
    font-weight: 800;
}

.hero {
    text-align: center;
    margin-bottom: 24px;
}

.hero h1 {
    font-size: 43px;
    line-height: 1.1;
    font-weight: 950;
    letter-spacing: -1.5px;
    margin-bottom: 12px;
}

.hero h1 span {
    color: #7c3aed !important;
}

.hero p {
    font-size: 17px;
    color: #475569 !important;
}

.form-card {
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(15,23,42,.10);
    border-radius: 30px;
    padding: 34px;
    box-shadow: 0 28px 75px rgba(15,23,42,.11);
    margin-bottom: 26px;
}

.form-title {
    font-size: 25px;
    font-weight: 950;
    margin-bottom: 6px;
}

.form-subtitle {
    color: #64748b !important;
    margin-bottom: 22px;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 15px !important;
    border: 1px solid #dbe1f0 !important;
    background: white !important;
    min-height: 48px;
    box-shadow: 0 8px 22px rgba(15,23,42,.05);
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
    font-size: 15px !important;
    color: #0f172a !important;
}

label {
    font-weight: 800 !important;
    color: #172554 !important;
}

div.stButton > button {
    width: 100%;
    height: 58px;
    border: none;
    border-radius: 16px;
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    font-size: 18px;
    font-weight: 900;
    box-shadow: 0 18px 40px rgba(37,99,235,.25);
}

div.stButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.05);
}

.stat-card {
    background: rgba(255,255,255,.88);
    border: 1px solid rgba(15,23,42,.08);
    border-radius: 24px;
    padding: 25px 18px;
    text-align: center;
    box-shadow: 0 18px 40px rgba(15,23,42,.07);
    min-height: 150px;
}

.stat-icon {
    font-size: 34px;
    margin-bottom: 8px;
}

.stat-title {
    font-size: 22px;
    font-weight: 950;
    color: #7c3aed !important;
}

.stat-desc {
    color: #475569 !important;
    font-weight: 600;
    margin-top: 5px;
}

.result-card {
    background: rgba(255,255,255,.94);
    border: 1px solid rgba(15,23,42,.10);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 18px 45px rgba(15,23,42,.08);
}

.result-heading {
    font-size: 22px;
    font-weight: 950;
    margin-bottom: 12px;
}

@media(max-width: 900px) {
    .cg-menu { display: none; }
    .hero h1 { font-size: 32px; }
}
</style>
""",
        unsafe_allow_html=True,
    )


def _validate_profile(profile: UserProfile) -> Optional[str]:
    if not profile.name.strip():
        return "Please enter your name."
    if not profile.education.strip():
        return "Please enter your education."
    if not profile.skills.strip():
        return "Please enter your skills."
    if not profile.interests.strip():
        return "Please enter your interests."
    if not profile.experience_level.strip():
        return "Please select your experience level."
    if not profile.career_goal.strip():
        return "Please enter your career goal."
    return None


def run_career_guidance(profile: UserProfile) -> str:
    provider_order = preferred_provider_order()
    if not provider_order:
        raise RuntimeError("No API keys found. Add GEMINI_API_KEY or GROQ_API_KEY in your .env file.")

    last_error: Optional[BaseException] = None

    for provider in provider_order:
        try:
            llm = build_crewai_llm(provider)
            crew = build_career_guidance_crew(profile, llm=llm)
            result = crew.kickoff()
            return str(result)
        except BaseException as e:
            last_error = e
            continue

    raise RuntimeError(f"All AI providers failed. Last error: {last_error}") from last_error


def _render_section(title: str, icon: str, content: str) -> None:
    st.markdown(
        f"""
<div class="result-card">
  <div class="result-heading">{icon} {title}</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(content)


def _show_bottom_cards() -> None:
    cards = [
        ("🤖", "4+", "AI Agents Working"),
        ("🎯", "100%", "Personalized Results"),
        ("🗺️", "Step-by-Step", "Roadmap & Mini Projects"),
        ("📚", "Best", "Resources & Courses"),
        ("🚀", "Career", "Success Starts Here"),
    ]

    cols = st.columns(5, gap="medium")
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
<div class="stat-card">
  <div class="stat-icon">{icon}</div>
  <div class="stat-title">{title}</div>
  <div class="stat-desc">{desc}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def main() -> None:
    _set_page_style()

    st.markdown(
        """
<div class="cg-navbar">
  <div class="cg-brand">🎓 Career Guidance <span>Chatbot</span></div>
  <div class="cg-menu">
    <span>🏠 Home</span>
    <span>📈 Profile Analysis</span>
    <span>💼 Career Options</span>
    <span>🗺️ Roadmap</span>
    <span>📚 Courses</span>
    <span>🎯 Job Prep</span>
  </div>
  <div class="cg-deploy">Deploy 🚀</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
<div class="hero">
  <h1>🚀 Plan your career like a <span>premium AI</span> product</h1>
  <p>Tell us your skills, interests, education, experience, and goals — the chatbot generates a complete guidance plan.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([0.08, 1, 0.08])

    with center:
        st.markdown('<div class="form-card">', unsafe_allow_html=True)

        st.markdown(
            """
<div class="form-title">✨ Create your personalized career plan</div>
<div class="form-subtitle">Fill in your details below to get career options, roadmap, resources, and job preparation tips.</div>
""",
            unsafe_allow_html=True,
        )

        with st.form("profile_form", border=False):
            c1, c2 = st.columns(2, gap="large")

            with c1:
                name = st.text_input("Name", value="Lavi")
                education = st.text_input("Education", placeholder="e.g., MCA / BCA / B.Tech CSE")
                skills = st.text_area(
                    "Skills",
                    placeholder="e.g., Python, HTML, CSS, JavaScript, Java, Communication",
                    height=100,
                )
                strengths = st.text_area(
                    "Strengths",
                    placeholder="e.g., Quick learner, logical thinking, consistency",
                    height=100,
                )

            with c2:
                experience_level = st.selectbox(
                    "Experience Level",
                    [
                        "Student / Fresher",
                        "Beginner (0-1 years)",
                        "Intermediate (1-3 years)",
                        "Experienced (3+ years)",
                    ],
                )
                career_goal = st.text_input(
                    "Career Goal",
                    placeholder="e.g., Web Developer / Data Analyst / Software Engineer",
                )
                interests = st.text_area(
                    "Interests",
                    placeholder="e.g., Web development, AI, design, teaching",
                    height=100,
                )
                weaknesses = st.text_area(
                    "Weaknesses",
                    placeholder="e.g., Time management, weak math, distraction",
                    height=100,
                )

            notes = st.text_area(
                "Optional Notes",
                placeholder="Anything else? preferred role, time per week, target country, constraints...",
                height=90,
            )

            submitted = st.form_submit_button("✨ Generate Career Plan")

        st.markdown("</div>", unsafe_allow_html=True)

        _show_bottom_cards()

    profile = UserProfile(
        name=name,
        education=education,
        skills=skills,
        interests=interests,
        strengths=strengths,
        weaknesses=weaknesses,
        experience_level=experience_level,
        career_goal=career_goal + (f"\n\nExtra Notes: {notes}" if notes.strip() else ""),
    )

    if not submitted:
        return

    error = _validate_profile(profile)
    if error:
        st.error(error)
        return

    with st.spinner("Generating your personalized career plan..."):
        try:
            output = run_career_guidance(profile)
            sections = split_sections(output)

            st.markdown("## 🎯 Your Personalized Career Plan")

            if not sections:
                st.warning("AI response generated, but section formatting was different.")
                st.markdown(output)
                return

            _render_section("Profile Analysis", "🧠", sections.get(SECTION_PROFILE, "Not generated."))
            _render_section("Career Options", "💼", sections.get(SECTION_CAREERS, "Not generated."))
            _render_section("Study Roadmap", "🗺️", sections.get(SECTION_ROADMAP, "Not generated."))
            _render_section("Courses & Certifications", "📚", sections.get(SECTION_LEARNING, "Not generated."))
            _render_section("Job Preparation Tips", "🚀", sections.get(SECTION_JOB_PREP, "Not generated."))

        except Exception:
            st.error("AI service unavailable. API key, model name, or quota issue ho sakta hai.")
            st.info("Technical details open karke screenshot bhej dena.")
            with st.expander("Technical details"):
                st.code(traceback.format_exc())


if __name__ == "__main__":
    main()