import streamlit as st
import time
import pandas as pd
from PIL import Image
import io
import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AgriGuard-AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Design & Custom Aesthetics ---
def inject_custom_css():
    st.markdown("""
    <style>
        /* Import premium font families */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
        
        /* Apply fonts */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Main Layout Styles */
        .title-container {
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .main-title {
            background: linear-gradient(90deg, #10b981 0%, #059669 45%, #60a5fa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.8rem;
            margin: 0;
            letter-spacing: -1.2px;
        }
        .main-subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-top: 0.2rem;
            font-weight: 400;
        }
        
        /* Sidebar Styling Overrides */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        /* Premium custom containers */
        .premium-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            margin-bottom: 24px;
        }
        
        .placeholder-box {
            border: 2px dashed rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            color: #64748b;
            background: rgba(30, 41, 59, 0.3);
        }
        
        /* Styled custom buttons */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3);
            width: 100%;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(16, 185, 129, 0.4);
            border: none;
            color: white;
        }
        
        div.stDownloadButton > button:first-child {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
            width: 100%;
        }
        div.stDownloadButton > button:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
            border: none;
            color: white;
        }
        
        /* Overrides for Streamlit expanders & status blocks */
        div[data-testid="stStatus"] {
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background-color: #1e293b !important;
            border-radius: 12px !important;
            padding: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- Diagnostic Scenarios Database ---
DIAGNOSTIC_MODELS = {
    "tomato": {
        "crop": {
            "Botanical Name": "Tomato (Solanum lycopersicum)",
            "Estimated Variety": "Roma / Plum Type",
            "Growth Stage": "Flowering & Early Fruiting",
            "Vitality Index": "Compromised (Immediate action required)"
        },
        "disease": {
            "Pathogen Detected": "Early Blight (Alternaria solani)",
            "Diagnostic Confidence": "94.2%",
            "Spread Severity": "Moderate (~22% leaf canopy affected)",
            "Primary Symptoms": "Target-like brown spots with yellow chlorotic halos"
        },
        "treatment": {
            "Organic Control": "Liquid copper fungicide spray, Bacillus subtilis bio-fungicide",
            "Chemical Control": "Azoxystrobin or Chlorothalonil application (follow dosage labels)",
            "Cultural Sanitation": "Prune lower foliage up to 12 inches, switch to drip irrigation",
            "Agronomist Note": "Apply copper spray early morning or late evening to prevent leaf phytotoxicity."
        }
    },
    "wheat": {
        "crop": {
            "Botanical Name": "Wheat (Triticum aestivum)",
            "Estimated Variety": "Hard Red Winter Wheat",
            "Growth Stage": "Tillering / Heading",
            "Vitality Index": "Warning Stage (Active rust spores present)"
        },
        "disease": {
            "Pathogen Detected": "Leaf Rust (Puccinia triticina)",
            "Diagnostic Confidence": "91.8%",
            "Spread Severity": "High (~35% of flag leaves affected)",
            "Primary Symptoms": "Powdery orange-brown pustules scattering leaf surface"
        },
        "treatment": {
            "Organic Control": "Sulfur-based dusts (preventative only, low therapeutic impact)",
            "Chemical Control": "Tebuconazole or Propiconazole systemic fungicide spray",
            "Cultural Sanitation": "Eradicate local volunteer wheat crops, manage nitrogen ratios",
            "Agronomist Note": "Focus chemistry on protecting the critical flag leaf to maintain yield integrity."
        }
    },
    "potato": {
        "crop": {
            "Botanical Name": "Potato (Solanum tuberosum)",
            "Estimated Variety": "Russet Burbank",
            "Growth Stage": "Tuber Bulking",
            "Vitality Index": "Critical Risk (Highly contagious water mold outbreak)"
        },
        "disease": {
            "Pathogen Detected": "Late Blight (Phytophthora infestans)",
            "Diagnostic Confidence": "96.5%",
            "Spread Severity": "Critical (~15% canopy with rapid spatial progression)",
            "Primary Symptoms": "Dark water-soaked lesions, white fuzzy mold under leaves"
        },
        "treatment": {
            "Organic Control": "Certified disease-free seed selection, copper sprays as preventive",
            "Chemical Control": "Fluopicolide, Cyazofamid, or Metalaxyl-M systemic application",
            "Cultural Sanitation": "Immediately destroy cull piles, avoid overhead sprinklers entirely",
            "Agronomist Note": "Mow and destroy vines 14 days before harvest to prevent tuber contamination."
        }
    },
    "default": {
        "crop": {
            "Botanical Name": "Grapevine (Vitis vinifera)",
            "Estimated Variety": "Chardonnay",
            "Growth Stage": "Berry Development",
            "Vitality Index": "Mild Alert (Airborne fungal spores detected)"
        },
        "disease": {
            "Pathogen Detected": "Powdery Mildew (Erysiphe necator)",
            "Diagnostic Confidence": "89.4%",
            "Spread Severity": "Mild-to-Moderate (~12% berry bunch exposure)",
            "Primary Symptoms": "Powdery, white-to-gray flour-like coating on leaves & stems"
        },
        "treatment": {
            "Organic Control": "Horticultural oils, potassium bicarbonate, or wettable sulfur sprays",
            "Chemical Control": "Rotate Strobilurin (azoxystrobin) with DMI fungicides (myclobutanil)",
            "Cultural Sanitation": "Prune excess canopy shoots to optimize sun penetration and airflow",
            "Agronomist Note": "Maintain spray intervals of 10-14 days. Do not apply sulfur above 90°F."
        }
    }
}

# --- Reusable UI Helpers ---
def render_result_card(title, icon, content_items, border_color="#10b981"):
    content_html = ""
    for k, v in content_items.items():
        content_html += f"""
        <div style="margin-bottom: 12px;">
            <strong style="color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.6px;">{k}</strong>
            <div style="color: #f8fafc; font-size: 1.05rem; font-weight: 500; margin-top: 3px; line-height: 1.4;">{v}</div>
        </div>
        """
    
    card_html = f"""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 4px solid {border_color};
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        min-height: 290px;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 18px;">
            <span style="font-size: 28px; margin-right: 12px;">{icon}</span>
            <h3 style="margin: 0; color: #f8fafc; font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.3rem; letter-spacing: -0.5px;">{title}</h3>
        </div>
        <div>
            {content_html}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def generate_report_text(location, scenario_key, data):
    crop_data = data["crop"]
    disease_data = data["disease"]
    treatment_data = data["treatment"]
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""======================================================================
                   AGRIGUARD-AI DIAGNOSTIC REPORT
======================================================================
Generated On : {timestamp}
Location     : {location}
Target Crop  : {crop_data['Botanical Name']} ({crop_data['Estimated Variety']})
----------------------------------------------------------------------

[1] CROP ASSESSMENT
-------------------
* Botanical Classification: {crop_data['Botanical Name']}
* Estimated Variety      : {crop_data['Estimated Variety']}
* Current Growth Stage   : {crop_data['Growth Stage']}
* Field Vitality Status  : {crop_data['Vitality Index']}

[2] PATHOLOGY EVALUATION
-----------------------
* Identified Pathogen    : {disease_data['Pathogen Detected']}
* Diagnostic Confidence  : {disease_data['Diagnostic Confidence']}
* Spread Severity Level  : {disease_data['Spread Severity']}
* Diagnostic Symptoms    : {disease_data['Primary Symptoms']}

[3] AGRONOMIST TREATMENT PROTOCOL
---------------------------------
* Biological / Organic   : {treatment_data['Organic Control']}
* Chemical Therapeutics  : {treatment_data['Chemical Control']}
* Cultural / Preventative: {treatment_data['Cultural Sanitation']}
* Chief Agronomist Note  : {treatment_data['Agronomist Note']}

----------------------------------------------------------------------
Disclaimer: This analysis is compiled by the AgriGuard-AI multi-agent 
diagnostics network. Direct field verification by local agricultural 
extension services is recommended before initiating chemical programs.
======================================================================
"""
    return report

def get_progression_chart(scenario_key):
    days = [f"Day {i}" for i in range(1, 11)]
    if scenario_key == "tomato":
        untreated = [10, 15, 22, 30, 42, 55, 70, 85, 95, 100]
        treated = [10, 15, 20, 18, 14, 10, 8, 5, 3, 1]
    elif scenario_key == "wheat":
        untreated = [8, 14, 22, 35, 48, 60, 75, 88, 95, 98]
        treated = [8, 14, 20, 22, 19, 15, 11, 8, 6, 4]
    elif scenario_key == "potato":
        untreated = [5, 15, 30, 50, 75, 95, 100, 100, 100, 100]
        treated = [5, 15, 25, 20, 15, 10, 5, 2, 1, 0]
    else:
        untreated = [5, 10, 12, 18, 25, 33, 45, 58, 70, 80]
        treated = [5, 10, 12, 14, 11, 8, 6, 4, 2, 1]
        
    df = pd.DataFrame({
        "Untreated Infection Spread (%)": untreated,
        "With Recommended Treatment (%)": treated
    }, index=days)
    return df

# --- Multi-Agent Simulation Block ---
def execute_agent_pipeline(location):
    st.markdown("### 🤖 Agent Network Diagnostics Execution")
    
    # 1. Diagnostician Agent
    with st.status("Diagnostician Agent", expanded=True) as status_diag:
        st.write("📸 Loading uploaded crop leaf image...")
        time.sleep(0.8)
        st.write("📐 Normalizing image contrast & extraction profiles...")
        time.sleep(1.0)
        st.write("🔬 Executing neural network leaf lesion localization...")
        time.sleep(1.2)
        st.write("🧬 Analyzing spot margins and color histogram variance...")
        time.sleep(1.0)
        status_diag.update(label="✅ Diagnostician Agent: Diagnostic Features Formulated", state="complete", expanded=False)
        
    # 2. Research Agent
    with st.status("Research Agent", expanded=True) as status_res:
        st.write(f"🌍 Resolving regional crop registries near '{location}'...")
        time.sleep(0.8)
        st.write("🌤️ Analyzing humidity threshold limits for fungal spore expansion...")
        time.sleep(1.2)
        st.write("📖 Matching pathogen patterns with agronomic publications...")
        time.sleep(1.0)
        st.write("⚖️ Querying regional restriction catalogs for registered fungicides...")
        time.sleep(0.8)
        status_res.update(label="✅ Research Agent: Ecological & Treatment Literatures Resolved", state="complete", expanded=False)
        
    # 3. Chief Agronomist
    with st.status("Chief Agronomist", expanded=True) as status_agro:
        st.write("🧠 Compiling logs from Diagnostician and Research Agents...")
        time.sleep(1.0)
        st.write("🧪 Structuring dual organic & chemical recovery schedule...")
        time.sleep(1.1)
        st.write("🛡️ Compiling microclimate rotation & airflow optimization tactics...")
        time.sleep(0.9)
        st.write("📝 Certifying treatment recipe and generating final advisory...")
        time.sleep(0.8)
        status_agro.update(label="✅ Chief Agronomist: Recovery Protocol Signed & Certified", state="complete", expanded=False)

# --- Main Application Logic ---
def main():
    inject_custom_css()
    
    # Header Section
    st.markdown("""
    <div class="title-container">
        <h1 class="main-title">🌱 AgriGuard-AI</h1>
        <div class="main-subtitle">Autonomous Multi-Agent Agriculture Diagnostics & Cognitive Advisory</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for analysis trigger
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "analysis_running" not in st.session_state:
        st.session_state.analysis_running = False
    if "active_case" not in st.session_state:
        st.session_state.active_case = "default"
        
    # Sidebar: Instructions & Dashboard Status Info
    with st.sidebar:
        st.markdown("### 🌾 Systems Control")
        st.markdown("""
        AgriGuard-AI runs an autonomous tripartite agent swarm to scan, research, and prescribe agricultural treatment plans.
        
        **Swarm Structure:**
        1. **Diagnostician Agent:** Handles visual computing, lesion analysis, and confidence scoring.
        2. **Research Agent:** Performs climate checks, literature review, and legal compliance lookups.
        3. **Chief Agronomist:** Consolidates insights and signs off on the recovery plan.
        """)
        
        st.markdown("---")
        st.markdown("### 📋 Sample Cases to Try")
        st.markdown("""
        Upload images with these terms in their filenames to trigger specific scenarios:
        - `tomato` (Early Blight)
        - `wheat` (Leaf Rust)
        - `potato` (Late Blight)
        """)
        
        st.markdown("---")
        st.markdown("<div style='font-size:0.8rem; color:#64748b;'>v2.4.0-Beta • System Online</div>", unsafe_allow_html=True)
        
    # Columns Layout
    col_input, col_display = st.columns([2, 3], gap="large")
    
    with col_input:
        st.markdown("### 🚜 Crop Registration Console")
        
        # Wrapped input inside CSS container
        with st.container():
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            
            # Location Input
            location = st.text_input(
                "Farmer Region / Location", 
                value="", 
                placeholder="e.g. Central Valley, California",
                help="Entering your location helps the Research Agent query weather data and local chemical restrictions."
            )
            
            # Image Upload
            uploaded_file = st.file_uploader(
                "Upload Affected Leaf Image", 
                type=["jpg", "jpeg", "png"],
                help="Upload a clear close-up picture of the infected area on the leaf."
            )
            
            # OR select a demo case
            st.markdown("<div style='text-align: center; color: #64748b; margin: 10px 0;'>— OR —</div>", unsafe_allow_html=True)
            demo_case = st.selectbox(
                "Use a Demo Specimen",
                options=["None", "Tomato Early Blight", "Wheat Leaf Rust", "Potato Late Blight", "Grape Powdery Mildew"],
                help="Select one of our pre-packaged specimens to test the multi-agent swarming intelligence instantly."
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Determine image source & case key
        img = None
        case_key = "default"
        
        if uploaded_file is not None:
            img = Image.open(uploaded_file)
            filename = uploaded_file.name.lower()
            if "tomato" in filename:
                case_key = "tomato"
            elif "wheat" in filename:
                case_key = "wheat"
            elif "potato" in filename:
                case_key = "potato"
            else:
                case_key = "default"
        elif demo_case != "None":
            filename = demo_case.lower()
            if "tomato" in filename:
                case_key = "tomato"
            elif "wheat" in filename:
                case_key = "wheat"
            elif "potato" in filename:
                case_key = "potato"
            else:
                case_key = "default"
            try:
                img = Image.open("tomato_leaf.png")
            except Exception:
                img = Image.new('RGB', (400, 400), color='#15803d')
                
        # Image Preview Card
        if img is not None:
            st.markdown("### 📸 Leaf Specimen Preview")
            with st.container():
                st.markdown('<div class="premium-card" style="text-align: center;">', unsafe_allow_html=True)
                st.image(img, caption="Specimen Image", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Submit/Run button
            if location.strip() == "":
                st.warning("⚠️ Please provide a farmer location before starting analysis.")
            else:
                if st.button("🚀 Execute Multi-Agent Diagnostic Scan"):
                    st.session_state.analysis_running = True
                    st.session_state.analysis_complete = False
                    st.session_state.active_case = case_key
                    st.rerun()
        else:
            st.markdown("### 📸 Leaf Specimen Preview")
            st.markdown("""
            <div class="placeholder-box">
                <span style="font-size: 2.5rem;">📷</span>
                <p style="margin-top: 10px; font-weight: 500;">Awaiting image upload...</p>
                <span style="font-size: 0.8rem;">Upload a leaf picture or choose a demo specimen above.</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Reset states if no file is uploaded
            if not st.session_state.analysis_complete and not st.session_state.analysis_running:
                st.session_state.analysis_running = False
                st.session_state.analysis_complete = False
            
    with col_display:
        if st.session_state.analysis_running:
            # Perform simulated agents pipeline
            execute_agent_pipeline(location)
            
            # Finished simulation
            st.session_state.analysis_running = False
            st.session_state.analysis_complete = True
            st.rerun()
            
        elif st.session_state.analysis_complete:
            # Load active case details
            case_key = st.session_state.active_case
            case_data = DIAGNOSTIC_MODELS[case_key]
            
            st.markdown("### 🏆 AI Diagnostics Dashboard")
            st.success(f"✅ Diagnostic Completed successfully for location: **{location}**")
            
            # Result cards row (3 Columns)
            card_col1, card_col2, card_col3 = st.columns(3)
            
            with card_col1:
                render_result_card(
                    title="Crop Identification",
                    icon="🌿",
                    content_items=case_data["crop"],
                    border_color="#10b981" # Green
                )
                
            with card_col2:
                render_result_card(
                    title="Disease Diagnosis",
                    icon="🔬",
                    content_items=case_data["disease"],
                    border_color="#f59e0b" # Amber
                )
                
            with card_col3:
                render_result_card(
                    title="Treatment Plan",
                    icon="💊",
                    content_items=case_data["treatment"],
                    border_color="#3b82f6" # Blue
                )
                
            # Analytics Expansion: Pandas-powered trend lines
            st.markdown("### 📊 Prognosis & Recovery Projections")
            with st.container():
                st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                st.markdown("#### Fungal Spread & Cure Rate Curves (10-Day Projection)")
                st.markdown("This chart plots the estimated disease expansion if left untreated versus the response curve following the agronomist's prescribed treatment plan.")
                
                # Fetch pandas progression table
                progression_df = get_progression_chart(case_key)
                
                # Line chart rendering
                st.line_chart(progression_df)
                
                # Quick stats
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric(
                        label="Untreated Spread in 10 Days", 
                        value="100%" if case_key in ["tomato", "potato"] else "98%", 
                        delta="Critical Outbreak Risk",
                        delta_color="inverse"
                    )
                with col_stat2:
                    st.metric(
                        label="Treated Infection Rate (Day 10)", 
                        value="0%" if case_key == "potato" else "1% - 4%", 
                        delta="Control Established",
                        delta_color="normal"
                    )
                st.markdown('</div>', unsafe_allow_html=True)
                
            # Download report button
            report_content = generate_report_text(location, case_key, case_data)
            
            st.markdown("### 📥 Document Generation")
            st.download_button(
                label="📥 Download Comprehensive Agronomist Report (TXT)",
                data=report_content,
                file_name=f"AgriGuard_Report_{case_key}_{datetime.date.today().isoformat()}.txt",
                mime="text/plain",
                help="Downloads the complete compiled agent diagnosis and treatment prescription report."
            )
            
        else:
            # Standby state
            st.markdown("### 🏆 AI Diagnostics Dashboard")
            st.markdown("""
            <div class="placeholder-box" style="padding: 100px 20px;">
                <span style="font-size: 3.5rem;">🤖</span>
                <h4 style="margin-top: 15px; color: #f1f5f9;">Tripartite Agent Network Idle</h4>
                <p style="color: #64748b; font-size: 0.95rem; max-width: 450px; margin: 10px auto;">
                    AgriGuard-AI is ready. Enter a farmer location and upload a plant leaf image in the console, then trigger the scan to engage the AI agents.
                </p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
