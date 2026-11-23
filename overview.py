

import streamlit as st


def navigate_to_page(page_name):
    st.session_state["page_navigation"] = page_name


def render_overview():
      project_dir = Path(__file__).parent
    stylesheet = project_dir / "overview.css"

    css = stylesheet.read_text(encoding="utf-8")
    css = css.replace("__NEBULA_IMAGE__", "none")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    hero_markup = """
        <section class="overview-hero">
            <div class="hero-copy">
                <div class="hero-eyebrow">
                    <span class="eyebrow-mark">✦</span>
                    SMART ATTENDANCE <span class="eyebrow-dot">·</span> MY OVERVIEW
                </div>
                <h1>Attendance,<br>made smarter.</h1>
                <p class="hero-description">
                    An AI-powered student attendance system using face
                    verification and campus location validation.
                </p>
                <div class="hero-badges">
                    <span class="hero-badge badge-cyan"><span>✧</span> AI Powered</span>
                    <span class="hero-badge badge-violet"><span>⌖</span> GPS Verified</span>
                    <span class="hero-badge badge-magenta"><span>↗</span> Real-time</span>
                </div>
            </div>
            <div class="hero-team">
                <img src="__TEAM_IMAGE__" alt="The Smart Attendance team">
            </div>
            <div class="hero-orbit orbit-one"></div>
            <div class="hero-orbit orbit-two"></div>
            <div class="hero-signal"><span></span> CAMPUS NETWORK <b>LIVE</b></div>
        </section>
        """
    hero_markup = hero_markup.replace(
        "__TEAM_IMAGE__",
        f"data:image/png;base64,{team_image_data}"
    )
    st.markdown(
        hero_markup,
        unsafe_allow_html=True
    )

    cards = [
        {
            "key": "student",
            "number": "01",
            "title": "Student Attendance",
            "description": (
                "Real attendance with face and campus location verification."
            ),
            "button": "Mark Attendance",
            "target": "Student Attendance",
            "accent": "cyan"
        },
        {
            "key": "teacher",
            "number": "02",
            "title": "Teacher Dashboard",
            "description": (
                "View student attendance, present / absent lists and reports."
            ),
            "button": "View Dashboard",
            "target": "Teacher Dashboard",
            "accent": "violet"
        },
        {
            "key": "demo",
            "number": "03",
            "title": "Demo Mode",
            "description": (
                "Try the system using fictional demo records."
            ),
            "button": "Try Demo",
            "target": "Demo Mode",
            "accent": "magenta"
        }
    ]

    columns = st.columns(3, gap="medium")
    for column, card in zip(columns, cards):
        with column:
            with st.container(key=f"overview_card_{card['key']}"):
                st.markdown(
                    f"""
                    <div class="nav-card-content accent-{card['accent']}">
                        <div class="card-topline">
                            <span class="card-number">{card['number']}</span>
                            <span class="card-index">WORKSPACE / {card['number']}</span>
                        </div>
                        <h2>{card['title']}</h2>
                        <p>{card['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.button(
                    card["button"],
                    key=f"overview_button_{card['key']}",
                    type="primary",
                    use_container_width=True,
                    on_click=navigate_to_page,
                    args=(card["target"],)
                )

    st.markdown(
        """
        <section class="workflow-panel">
            <div class="section-heading">
                <div>
                    <div class="section-kicker">A CLEAR PATH TO TRUSTED DATA</div>
                    <h2>How the system works</h2>
                </div>
                <span class="workflow-label">01 — 04 <i></i> VERIFIED FLOW</span>
            </div>
            <div class="workflow-steps">
                <div class="workflow-step">
                    <span class="step-number">01</span>
                    <span class="step-indicator">◎</span>
                    <p>Student selects<br>their identity.</p>
                </div>
                <div class="workflow-step">
                    <span class="step-number">02</span>
                    <span class="step-indicator">◉</span>
                    <p>Face verification checks<br>the registered student.</p>
                </div>
                <div class="workflow-step">
                    <span class="step-number">03</span>
                    <span class="step-indicator">⌖</span>
                    <p>GPS validates the<br>campus location.</p>
                </div>
                <div class="workflow-step">
                    <span class="step-number">04</span>
                    <span class="step-indicator">✓</span>
                    <p>Attendance is recorded<br>and shown to teachers.</p>
                </div>
            </div>
        </section>
        <footer class="technology-footer">
            <span class="tech-label">BUILT WITH</span>
            <span>Python</span><i></i><span>Streamlit</span><i></i>
            <span>DeepFace</span><i></i><span>Gemini API</span><i></i>
            <span>CSV</span>
        </footer>
        """,
        unsafe_allow_html=True
    )

