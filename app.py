import datetime
import json
import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from crew.crew_setup import run_analysis

st.set_page_config(page_title="AgriGuard-AI", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
        .hero-banner {
            background: linear-gradient(135deg, #1B5E20, #2E7D32);
            color: white;
            padding: 1.8rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1.2rem;
        }
        .result-card {
            background: #F1F8E9;
            border: 2px solid #81C784;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            text-align: center;
        }
        .result-card h4 { color: #1B5E20; margin-bottom: 0.3rem; }
        .result-card p { font-size: 1.1rem; font-weight: bold; color: #33691E; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🌿 AgriGuard-AI</h1>
            <p>Your AI-powered crop disease diagnosis and treatment assistant</p>
            <small>Multi-agent AI · RAG · Weather-aware recommendations</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    with st.sidebar:
        st.header("📋 Farmer Input")
        st.divider()
        uploaded_file = st.file_uploader("Choose a photo of the affected plant", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded crop photo", use_column_width=True)

        st.divider()
        city = st.text_input("Enter your city", placeholder="e.g. Nairobi, Pune, Lagos")
        st.divider()
        analyze_clicked = st.button("🔍 Analyze Crop", type="primary", use_container_width=True, disabled=(uploaded_file is None or not city.strip()))

        if uploaded_file is None:
            st.caption("⬆️ Please upload a photo to begin.")
        elif not city.strip():
            st.caption("📍 Please enter your city to begin.")

    return uploaded_file, city.strip(), analyze_clicked


def run_agents_with_ui(image_path: str, city: str) -> dict:
    from tools.vlm_tool import diagnose_crop
    from rag.search import retrieve_treatment

    with st.status("🩺 Diagnostician Agent — Analyzing crop image...", expanded=True) as status1:
        diagnosis = diagnose_crop(image_path)
        st.write(f"✅ Detected: {diagnosis.get('crop', 'Unknown')} — {diagnosis.get('disease', 'Unknown')}")
        status1.update(label="🩺 Diagnostician Agent — Complete ✓", state="complete")

    with st.status("📚 Research Agent — Searching treatment database...", expanded=True) as status2:
        treatment = retrieve_treatment(diagnosis.get("disease", ""))
        st.write(f"✅ Treatment found with similarity {treatment.get('similarity_score', 0):.2f}")
        status2.update(label="📚 Research Agent — Complete ✓", state="complete")

    with st.status("🌦 Chief Agronomist — Synthesizing final report...", expanded=True) as status3:
        result = run_analysis(image_path=image_path, location=city, diagnosis=diagnosis, treatment=treatment)
        st.write("✅ Final recommendation generated")
        status3.update(label="🌦 Chief Agronomist — Complete ✓", state="complete")

    return result


def render_results(result: dict) -> None:
    st.divider()
    st.subheader("✅ Analysis Complete — Your Report")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"<div class=\"result-card\"><h4>🌱 Crop</h4><p>{result.get('crop', 'Unknown')}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class=\"result-card\"><h4>🦠 Disease</h4><p>{result.get('disease', 'Unknown')}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class=\"result-card\"><h4>💊 Treatment</h4><p>{result.get('treatment', 'See recommendation below')}</p></div>", unsafe_allow_html=True)

    st.divider()
    if result.get("weather_summary"):
        st.info(f"🌦 **Weather Context:** {result['weather_summary']}")
    st.subheader("📋 Chief Agronomist's Recommendation")
    st.success(result.get("final_recommendation", "No recommendation generated."))
    render_download_button(result)


def render_download_button(result: dict) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    report_text = f"""
============================================================
  AgriGuard-AI — Crop Disease Report
  Generated: {timestamp}
============================================================

CROP          : {result.get('crop', 'N/A')}
DISEASE       : {result.get('disease', 'N/A')}
TREATMENT     : {result.get('treatment', 'N/A')}

WEATHER SUMMARY
---------------
{result.get('weather_summary', 'N/A')}

FINAL RECOMMENDATION
--------------------
{result.get('final_recommendation', 'N/A')}
============================================================
""".strip()
    st.download_button("⬇️ Download Report as Text File", data=report_text, file_name=f"agriguard_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt", mime="text/plain", use_container_width=True)


def main() -> None:
    apply_custom_styles()
    render_hero()
    uploaded_file, city, analyze_clicked = render_sidebar()

    if not analyze_clicked and "result" not in st.session_state:
        st.markdown(
            """
            ### 👋 Welcome to AgriGuard-AI!

            1. 📷 Upload a photo of your sick crop.
            2. 📍 Type your city name.
            3. 🔍 Click **Analyze Crop**.

            The system will diagnose the crop, search a trusted treatment database, review local weather, and provide a farmer-friendly recommendation.
            """
        )
        return

    if analyze_clicked and uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        with st.spinner("Agents are working... please wait."):
            st.session_state["result"] = run_agents_with_ui(temp_path, city)
            st.session_state["city"] = city

    if "result" in st.session_state:
        render_results(st.session_state["result"])


if __name__ == "__main__":
    main()
