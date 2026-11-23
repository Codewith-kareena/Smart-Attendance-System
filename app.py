import math
import tempfile
from pathlib import Path
from datetime import datetime, date, time
from io import BytesIO

import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_autorefresh import st_autorefresh
from gemini_service import generate_attendance_summary
from overview import navigate_to_page, render_overview


# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide"
)

# RKDF University, Ranchi coordinates
COLLEGE_LAT = 23.357244
COLLEGE_LON = 85.267532
ALLOWED_DISTANCE = 200
REPORTING_TIME = time(9, 0)

STUDENTS_FILE = Path("students.csv")
ATTENDANCE_FILE = Path("attendance.csv")

# Demo data is stored separately and never added to attendance.csv.
DEMO_STUDENTS_FILE = Path("demo_students.csv")
DEMO_ATTENDANCE_FILE = Path("demo_attendance.csv")

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
# HELPER FUNCTIONS
# ==========================================
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS coordinates in metres."""
    earth_radius = 6371000

    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return earth_radius * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )


def load_attendance_file(file_path):
    """Create or migrate an attendance CSV without losing existing records."""
    if not file_path.exists():
        pd.DataFrame(columns=ATTENDANCE_COLUMNS).to_csv(
            file_path, index=False
        )

    data = pd.read_csv(file_path)

    for column in ATTENDANCE_COLUMNS:
        if column not in data.columns:
            data[column] = ""

    if not data.empty:
        missing_arrival = (
            data["arrival_status"].isna()
            | (data["arrival_status"].astype(str) == "")
        )
        data.loc[missing_arrival, "arrival_status"] = data.loc[
            missing_arrival, "status"
        ]

    data = data[ATTENDANCE_COLUMNS]
    data.to_csv(file_path, index=False)
    return data


def create_demo_data():
    """
    Create a separate set of 20 fictional students and today's demo records.
    This data is illustrative only and is never mixed with real attendance.
    """
    demo_names = [
        "Aarav Sharma", "Aditi Verma", "Ananya Singh", "Arjun Kumar",
        "Diya Gupta", "Ishaan Das", "Kavya Mishra", "Kunal Roy",
        "Meera Sinha", "Neha Kumari", "Rohan Patel", "Sana Khan",
        "Sarthak Jain", "Simran Das", "Tanvi Rao", "Vikram Singh",
        "Yash Gupta", "Zoya Ali", "Nikhil Sharma", "Pooja Verma"
    ]

    demo_students = pd.DataFrame({
        "student_id": [f"DEMO{number:03d}" for number in range(1, 21)],
        "name": demo_names
    })

    # Keep the same 20 fictional students in their own demo file.
    demo_students.to_csv(DEMO_STUDENTS_FILE, index=False)

    today = date.today().isoformat()

    # Rebuild today's demo records on each app start so the sample
    # statuses remain predictable and independent of real attendance.
    demo_rows = []
    sample_statuses = [
        "Present", "Present", "Present", "Present", "Present",
        "Present", "Present", "Present", "Present", "Present",
        "Late", "Late", "Late",
        "Left", "Left"
    ]

    sample_times = [
        "08:10:00", "08:18:00", "08:22:00", "08:27:00", "08:31:00",
        "08:35:00", "08:40:00", "08:43:00", "08:48:00", "08:52:00",
        "09:06:00", "09:12:00", "09:19:00",
        "08:25:00", "09:08:00"
    ]

    for index, status in enumerate(sample_statuses):
        student = demo_students.iloc[index]
        arrival_status = "Late" if sample_times[index] >= "09:00:00" else "Present"

        demo_rows.append({
            "student_id": student["student_id"],
            "name": student["name"],
            "date": today,
            "time": sample_times[index],
            "status": status,
            "location": "Demo location",
            "arrival_status": arrival_status,
            "exit_time": "12:30:00" if status == "Left" else ""
        })

    demo_attendance = pd.DataFrame(
        demo_rows,
        columns=ATTENDANCE_COLUMNS
    )
    demo_attendance.to_csv(DEMO_ATTENDANCE_FILE, index=False)

    return demo_students, demo_attendance


def style_attendance_status(status):
    """Apply display-only colors to attendance status cells."""
    status_colors = {
        "Present": "#69f0c1",
        "Late": "#ffd166",
        "Absent": "#ff718d",
        "Left": "#70bdff"
    }
    color = status_colors.get(status)
    return f"color: {color}; font-weight: 700;" if color else ""


# ==========================================
# LOAD REAL STUDENT DATA
# ==========================================
try:
    students = pd.read_csv(STUDENTS_FILE)

    required_student_columns = ["student_id", "name", "image"]
    if not all(
        column in students.columns
        for column in required_student_columns
    ):
        st.error("students.csv is missing required columns.")
        st.stop()

except FileNotFoundError:
    st.error("students.csv not found in project folder.")
    st.stop()


# ==========================================
# LOAD REAL ATTENDANCE DATA
# ==========================================
attendance = load_attendance_file(ATTENDANCE_FILE)


# ==========================================
# CREATE SEPARATE DEMO DATA
# ==========================================
demo_students, demo_attendance = create_demo_data()


# ==========================================
# NAVIGATION
# ==========================================
page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Student Attendance",
        "Teacher Dashboard",
        "Demo Mode"
    ],
    key="page_navigation"
)

if page != "Overview":
    app_theme = Path(__file__).with_name("app_theme.css").read_text(
        encoding="utf-8"
    )
    st.markdown(f"<style>{app_theme}</style>", unsafe_allow_html=True)
    st.title("🎓 Smart Attendance System")
    st.caption("AI-Based Student Attendance Management")


# ==========================================
# OVERVIEW PAGE
# ==========================================
if page == "Overview":
    render_overview()


# ==========================================
# STUDENT ATTENDANCE PAGE
# ==========================================
elif page == "Student Attendance":
    st.header("Student Attendance")
    st.caption("Real attendance — face and campus location verification required.")

    student_name = st.selectbox(
        "Select your name",
        students["name"].tolist()
    )

    student = students[
        students["name"] == student_name
    ].iloc[0]

    registered_image = Path(str(student["image"]))

    # Camera
    photo = st.camera_input("Capture your attendance photo")

    # Location verification
    st.divider()
    st.subheader("📍 Location Verification")

    location = streamlit_geolocation()
    location_status = None

    if (
        location
        and location.get("latitude") is not None
        and location.get("longitude") is not None
    ):
        distance = calculate_distance(
            location["latitude"],
            location["longitude"],
            COLLEGE_LAT,
            COLLEGE_LON
        )

        st.write(f"Distance from college: {distance:.2f} metres")

        if distance <= ALLOWED_DISTANCE:
            st.success("Inside college campus")
            location_status = "Inside"
        else:
            st.warning("Outside college campus")
            location_status = "Outside"
    else:
        st.info("Allow browser location permission.")

    # Face verification
    st.divider()
    st.subheader("🤖 AI Face Verification")

    if st.button("Verify Face & Mark Attendance"):
        if photo is None:
            st.warning("Please capture your photo first.")

        elif not registered_image.exists():
            st.error(
                f"Registered photo not found: {registered_image}"
            )

        else:
            captured_path = None

            try:
                from deepface import DeepFace

                with st.spinner("AI is comparing the two photos..."):
                    with tempfile.NamedTemporaryFile(
                        suffix=".jpg",
                        delete=False
                    ) as temp_file:
                        temp_file.write(photo.getvalue())
                        captured_path = temp_file.name

                    try:
                        result = DeepFace.verify(
                            img1_path=str(registered_image),
                            img2_path=captured_path,
                            enforce_detection=True
                        )
                    finally:
                        if captured_path:
                            Path(captured_path).unlink(missing_ok=True)

                if result["verified"]:
                    st.success("Face Matched! Same person detected.")
                    st.write(
                        f"Face distance: {result['distance']:.4f}"
                    )
                    st.write(f"Model: {result['model']}")

                    if location_status == "Inside":
                        today = date.today().isoformat()
                        now = datetime.now()

                        # Reload from the real attendance file before checking duplicates.
                        attendance = load_attendance_file(ATTENDANCE_FILE)

                        already_marked = (
                            (
                                attendance["student_id"].astype(str)
                                == str(student["student_id"])
                            )
                            & (
                                attendance["date"].astype(str)
                                == today
                            )
                        ).any()

                        if already_marked:
                            st.info(
                                "Attendance is already marked today."
                            )
                        else:
                            status = (
                                "Present"
                                if now.time() < REPORTING_TIME
                                else "Late"
                            )

                            new_record = pd.DataFrame([{
                                "student_id": student["student_id"],
                                "name": student_name,
                                "date": today,
                                "time": now.strftime("%H:%M:%S"),
                                "status": status,
                                "location": "Inside",
                                "arrival_status": status,
                                "exit_time": ""
                            }])

                            attendance = pd.concat(
                                [attendance, new_record],
                                ignore_index=True
                            )

                            attendance.to_csv(
                                ATTENDANCE_FILE,
                                index=False
                            )

                            st.success(
                                f"Attendance saved successfully! Status: {status}"
                            )

                    else:
                        st.warning(
                            "Face matched, but attendance cannot be marked "
                            "because campus location is not verified."
                        )

                else:
                    st.error(
                        "Face Not Matched! Attendance rejected."
                    )

            except Exception as error:
                st.error(f"Face verification failed: {error}")
                st.info(
                    "Check your registered photo and DeepFace installation."
                )


# ==========================================
# TEACHER DASHBOARD — REAL ATTENDANCE ONLY
# ==========================================
elif page == "Teacher Dashboard":
    st.header("👩‍🏫 Teacher Dashboard")
    st.caption("Live overview of REAL student attendance.")
    st.info("REAL DATA MODE — This dashboard reads only attendance.csv.")

    # Auto refresh every 10 seconds
    st_autorefresh(
        interval=10000,
        key="dashboard_refresh"
    )

    attendance = load_attendance_file(ATTENDANCE_FILE)
    today = date.today().isoformat()

    today_attendance = attendance[
        attendance["date"].astype(str) == today
    ].copy()

    total_students = len(students)

    present_ids = set(
        today_attendance[
            today_attendance["status"] == "Present"
        ]["student_id"].astype(str)
    )

    late_ids = set(
        today_attendance[
            today_attendance["status"] == "Late"
        ]["student_id"].astype(str)
    )

    left_ids = set(
        today_attendance[
            today_attendance["status"] == "Left"
        ]["student_id"].astype(str)
    )

    marked_ids = present_ids | late_ids | left_ids

    present_count = len(present_ids)
    late_count = len(late_ids)
    left_count = len(left_ids)
    absent_count = max(0, total_students - len(marked_ids))

    # Dashboard metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Students", total_students)
    col2.metric("Present", present_count)
    col3.metric("Late", late_count)
    col4.metric("Left", left_count)
    col5.metric("Absent", absent_count)

    # Today's records
    st.divider()
    st.subheader("📋 Today's Attendance Records")

    if today_attendance.empty:
        st.info("No attendance records found for today.")
    else:
        st.dataframe(
            today_attendance[
                [
                    "student_id", "name", "date", "time",
                    "status", "location", "exit_time"
                ]
            ].style.map(style_attendance_status, subset=["status"]),
            use_container_width=True,
            hide_index=True
        )

    # Mark student as left
    st.divider()
    st.subheader("🚪 Student Departure Management")

    eligible_students = today_attendance[
        today_attendance["status"].isin(["Present", "Late"])
    ]

    if eligible_students.empty:
        st.info("No present students available to mark as Left.")
    else:
        departure_options = (
            eligible_students["student_id"].astype(str)
            + " - "
            + eligible_students["name"].astype(str)
        ).tolist()

        selected_departure = st.selectbox(
            "Select student who is leaving",
            departure_options
        )

        if st.button("Mark Student as Left"):
            selected_id = selected_departure.split(" - ", 1)[0]
            current_time = datetime.now().strftime("%H:%M:%S")

            mask = (
                (attendance["student_id"].astype(str) == selected_id)
                & (attendance["date"].astype(str) == today)
                & (attendance["status"].isin(["Present", "Late"]))
            )

            if mask.any():
                attendance.loc[mask, "status"] = "Left"
                attendance.loc[mask, "exit_time"] = current_time
                attendance.to_csv(ATTENDANCE_FILE, index=False)

                st.success(
                    f"Student departure recorded at {current_time}."
                )
                st.rerun()
            else:
                st.warning(
                    "This student's attendance cannot be updated."
                )

    # Attendance chart
    st.divider()
    st.subheader("📊 Attendance Summary")

    summary = pd.DataFrame({
        "Category": ["Present", "Late", "Left", "Absent"],
        "Students": [
            present_count,
            late_count,
            left_count,
            absent_count
        ]
    })

    st.bar_chart(summary.set_index("Category"))

    # Gemini AI insights
    st.divider()
    st.subheader("🤖 Gemini AI Attendance Insights")
    st.write(
        "Generate an AI-powered summary of today's REAL attendance."
    )

    if st.button("Generate AI Attendance Summary"):
        if today_attendance.empty:
            st.info(
                "No attendance records available for AI analysis."
            )
        else:
            with st.spinner("Gemini AI is analyzing attendance..."):
                ai_summary = generate_attendance_summary(
                    today_attendance.to_dict(orient="records")
                )

            st.markdown("### 📋 AI Analysis")
            st.write(ai_summary)

    # Attendance history
    st.divider()
    st.subheader("📅 Attendance History")

    if not attendance.empty:
        available_dates = sorted(
            attendance["date"].dropna().astype(str).unique(),
            reverse=True
        )

        if available_dates:
            selected_date = st.selectbox(
                "Select attendance date",
                available_dates
            )

            history = attendance[
                attendance["date"].astype(str) == selected_date
            ]

            st.dataframe(
                history.style.map(
                    style_attendance_status,
                    subset=["status"]
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No attendance history available.")
    else:
        st.info("No attendance history available.")

    # Excel download — real data only
    st.divider()
    st.subheader("📥 Download Attendance Report")

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:
        attendance.to_excel(
            writer,
            index=False,
            sheet_name="Real Attendance"
        )
        summary.to_excel(
            writer,
            index=False,
            sheet_name="Today's Summary"
        )

    st.download_button(
        label="Download Excel Report",
        data=excel_buffer.getvalue(),
        file_name="attendance_report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.caption(
        "Dashboard refreshes automatically every 10 seconds."
    )


# ==========================================
# DEMO MODE — FICTIONAL DATA ONLY
# ==========================================
elif page == "Demo Mode":
    st.header("🧪 Demo Mode")
    st.error(
        "DEMO DATA — FICTIONAL STUDENTS. "
        "This page is for demonstration only and is not real attendance."
    )

    st.caption(
        "Demo records are stored separately in demo_attendance.csv. "
        "They are never written to attendance.csv."
    )

    demo_students, demo_attendance = create_demo_data()

    today = date.today().isoformat()
    demo_today = demo_attendance[
        demo_attendance["date"].astype(str) == today
    ].copy()

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
    demo_marked = demo_today["student_id"].astype(str).nunique()
    demo_absent = max(0, demo_total - demo_marked)

    # Demo metrics
    st.subheader("📊 Sample Attendance Overview")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Students", demo_total)
    col2.metric("Present", demo_present)
    col3.metric("Late", demo_late)
    col4.metric("Left", demo_left)
    col5.metric("Absent", demo_absent)

    # Demo attendance table
    st.divider()
    st.subheader("📋 Sample Attendance Records")

    demo_display = demo_today.copy()
    absent_ids = set(demo_students["student_id"]) - set(
        demo_today["student_id"]
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
            [demo_display, absent_rows[ATTENDANCE_COLUMNS]],
            ignore_index=True
        )

    status_order = {
        "Present": 0,
        "Late": 1,
        "Left": 2,
        "Absent": 3
    }

    demo_display["_order"] = demo_display["status"].map(status_order)
    demo_display = demo_display.sort_values(
        ["_order", "student_id"]
    ).drop(columns=["_order"])

    st.dataframe(
        demo_display[
            [
                "student_id", "name", "date", "time",
                "status", "location", "exit_time"
            ]
        ].style.map(style_attendance_status, subset=["status"]),
        use_container_width=True,
        hide_index=True
    )

    # Demo chart
    st.divider()
    st.subheader("📈 Demo Attendance Chart")

    demo_summary = pd.DataFrame({
        "Category": ["Present", "Late", "Left", "Absent"],
        "Students": [
            demo_present,
            demo_late,
            demo_left,
            demo_absent
        ]
    })

    st.bar_chart(demo_summary.set_index("Category"))

    # Gemini analysis of demo data
    st.divider()
    st.subheader("🤖 Gemini AI — Demo Attendance Insights")
    st.caption(
        "The AI summary below uses fictional demo records only."
    )

    if st.button("Generate Demo AI Summary"):
        with st.spinner("Gemini AI is analyzing demo records..."):
            demo_ai_summary = generate_attendance_summary(
                demo_display.to_dict(orient="records")
            )

        st.markdown("### 📋 Demo AI Analysis")
        st.write(demo_ai_summary)

    # Demo-only Excel download
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
st.caption("Smart Attendance System | BCA Project")
