
from pathlib import Path
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

from overview import render_overview
from gemini_service import generate_attendance_summary


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# FILE CONFIGURATION
# ==========================================

DEMO_STUDENTS_FILE = Path("demo_students.csv")
DEMO_ATTENDANCE_FILE = Path("demo_attendance.csv")
THEME_FILE = Path("app_theme.css")

ATTENDANCE_COLUMNS = [
    "student_id",
    "name",
    "date",
    "time",
    "status",
    "location",
    "arrival_status",
    "exit_time"
]


# ==========================================
# CREATE FICTIONAL DEMO DATA
# ==========================================

def create_demo_data():

    demo_names = [
        "Aarav Sharma", "Aditi Verma", "Ananya Singh",
        "Arjun Kumar", "Diya Gupta", "Ishaan Das",
        "Kavya Mishra", "Kunal Roy", "Meera Sinha",
        "Neha Kumari", "Rohan Patel", "Sana Khan",
        "Sarthak Jain", "Simran Das", "Tanvi Rao",
        "Vikram Singh", "Yash Gupta", "Zoya Ali",
        "Nikhil Sharma", "Pooja Verma"
    ]

    demo_students = pd.DataFrame({
        "student_id": [
            f"DEMO{number:03d}"
            for number in range(1, 21)
        ],
        "name": demo_names
    })

    demo_students.to_csv(
        DEMO_STUDENTS_FILE,
        index=False
    )

    today = date.today().isoformat()

    sample_statuses = [
        "Present", "Present", "Present", "Present",
        "Present", "Present", "Present", "Present",
        "Present", "Present", "Late", "Late",
        "Late", "Left", "Left"
    ]

    sample_times = [
        "08:10:00", "08:18:00", "08:22:00",
        "08:27:00", "08:31:00", "08:35:00",
        "08:40:00", "08:43:00", "08:48:00",
        "08:52:00", "09:06:00", "09:12:00",
        "09:19:00", "08:25:00", "09:08:00"
    ]

    demo_rows = []

    for index, status in enumerate(sample_statuses):

        student = demo_students.iloc[index]

        arrival_status = (
            "Late"
            if sample_times[index] >= "09:00:00"
            else "Present"
        )

        demo_rows.append({
            "student_id": student["student_id"],
            "name": student["name"],
            "date": today,
            "time": sample_times[index],
            "status": status,
            "location": "Demo location",
            "arrival_status": arrival_status,
            "exit_time": (
                "12:30:00" if status == "Left" else ""
            )
        })

    demo_attendance = pd.DataFrame(
        demo_rows,
        columns=ATTENDANCE_COLUMNS
    )

    demo_attendance.to_csv(
        DEMO_ATTENDANCE_FILE,
        index=False
    )

    return demo_students, demo_attendance


# ==========================================
# STATUS COLORS
# ==========================================

def style_attendance_status(status):

    status_colors = {
        "Present": "#69f0c1",
        "Late": "#ffd166",
        "Absent": "#ff718d",
        "Left": "#70bdff"
    }

    color = status_colors.get(status)

    if color:
        return f"color: {color}; font-weight: 700;"

    return ""


# ==========================================
# LOAD DEMO DATA ONLY
# ==========================================

demo_students, demo_attendance = create_demo_data()


# ==========================================
# NAVIGATION
# ==========================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Demo Mode"
    ],
    key="page_navigation"
)

if page != "Overview":

    if THEME_FILE.exists():

        app_theme = THEME_FILE.read_text(
            encoding="utf-8"
        )

        st.markdown(
            f"<style>{app_theme}</style>",
            unsafe_allow_html=True
        )

    st.title("🎓 Smart Attendance System")

    st.caption(
        "AI-Based Student Attendance Management"
    )


# ==========================================
# OVERVIEW PAGE
# ==========================================

if page == "Overview":

    render_overview()


# ==========================================
# DEMO MODE
# ==========================================

elif page == "Demo Mode":

    st.header("🧪 Demo Mode")

    st.error(
        "DEMO DATA — FICTIONAL STUDENTS. "
        "This page is for demonstration only "
        "and is not real attendance."
    )

    st.caption(
        "All records shown below are fictional "
        "and are separate from real attendance."
    )

    # Today's demo records

    today = date.today().isoformat()

    demo_today = demo_attendance[
        demo_attendance["date"].astype(str) == today
    ].copy()

    # Attendance calculations

    demo_total = len(demo_students)

    demo_present = int(
        (demo_today["status"] == "Present").sum()
    )

    demo_late = int(
        (demo_today["status"] == "Late").sum()
    )

    demo_left = int(
        (demo_today["status"] == "Left").sum()
    )

    demo_marked = (
        demo_today["student_id"].astype(str).nunique()
    )

    demo_absent = max(
        0,
        demo_total - demo_marked
    )

    # ======================================
    # ATTENDANCE OVERVIEW
    # ======================================

    st.subheader("📊 Sample Attendance Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Total Students", demo_total)
    col2.metric("Present", demo_present)
    col3.metric("Late", demo_late)
    col4.metric("Left", demo_left)
    col5.metric("Absent", demo_absent)

    # ======================================
    # ATTENDANCE RECORDS
    # ======================================

    st.divider()

    st.subheader("📋 Sample Attendance Records")

    demo_display = demo_today.copy()

    absent_ids = (
        set(demo_students["student_id"])
        - set(demo_today["student_id"])
    )

    if absent_ids:

        absent_rows = demo_students[
            demo_students["student_id"].isin(absent_ids)
        ].copy()

        absent_rows["date"] = today
        absent_rows["time"] = "-"
        absent_rows["status"] = "Absent"
        absent_rows["location"] = "Demo location"
        absent_rows["arrival_status"] = "Absent"
        absent_rows["exit_time"] = "-"

        demo_display = pd.concat(
            [
                demo_display,
                absent_rows[ATTENDANCE_COLUMNS]
            ],
            ignore_index=True
        )

    status_order = {
        "Present": 0,
        "Late": 1,
        "Left": 2,
        "Absent": 3
    }

    demo_display["_order"] = (
        demo_display["status"].map(status_order)
    )

    demo_display = (
        demo_display
        .sort_values(["_order", "student_id"])
        .drop(columns=["_order"])
    )

    st.dataframe(
        demo_display[
            [
                "student_id",
                "name",
                "date",
                "time",
                "status",
                "location",
                "exit_time"
            ]
        ].style.map(
            style_attendance_status,
            subset=["status"]
        ),
        use_container_width=True,
        hide_index=True
    )

    # ======================================
    # ATTENDANCE CHART
    # ======================================

    st.divider()

    st.subheader("📈 Demo Attendance Chart")

    demo_summary = pd.DataFrame({
        "Category": [
            "Present",
            "Late",
            "Left",
            "Absent"
        ],
        "Students": [
            demo_present,
            demo_late,
            demo_left,
            demo_absent
        ]
    })

    st.bar_chart(
        demo_summary.set_index("Category")
    )

    # ======================================
    # GEMINI AI SUMMARY
    # ======================================

    st.divider()

    st.subheader(
        "🤖 Gemini AI — Demo Attendance Insights"
    )

    st.caption(
        "AI analysis uses fictional demo attendance records only."
    )

    if st.button("Generate Demo AI Summary"):

        try:

            with st.spinner(
                "Gemini AI is analyzing demo records..."
            ):

                demo_ai_summary = generate_attendance_summary(
                    demo_display.to_dict(orient="records")
                )

            st.markdown("### 📋 AI Analysis")

            st.write(demo_ai_summary)

        except Exception as error:

            st.warning(
                "Gemini AI is currently unavailable. "
                "Please check the API key in Streamlit Secrets."
            )

    # ======================================
    # EXCEL DOWNLOAD
    # ======================================

    st.divider()

    st.subheader("📥 Download Demo Report")

    demo_excel_buffer = BytesIO()

    with pd.ExcelWriter(
        demo_excel_buffer,
        engine="openpyxl"
    ) as writer:

        demo_display.to_excel(
            writer,
            index=False,
            sheet_name="DEMO Attendance"
        )

        demo_summary.to_excel(
            writer,
            index=False,
            sheet_name="DEMO Summary"
        )

    st.download_button(
        label="Download DEMO Excel Report",
        data=demo_excel_buffer.getvalue(),
        file_name="DEMO_attendance_report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.warning(
        "Do not submit the demo report as actual college attendance."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Smart Attendance System | BCA Project"
)
