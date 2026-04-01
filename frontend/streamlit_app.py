import streamlit as st
import requests
import json

#API_URL = "http://localhost:8000"
API_URL = "http://127.0.0.1:8000"

# Page config
st.set_page_config(
    page_title="Healthcare Prior Authorization Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .approval-high { color: #28a745; font-size: 2em; font-weight: bold; }
    .approval-medium { color: #ffc107; font-size: 2em; font-weight: bold; }
    .approval-low { color: #dc3545; font-size: 2em; font-weight: bold; }
    .section-header {
        background: #1f77b4;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_approval_color(likelihood: int) -> str:
    if likelihood >= 75:
        return "approval-high"
    elif likelihood >= 50:
        return "approval-medium"
    return "approval-low"

def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hospital.png", width=80)
    st.title("Auth Platform")
    st.markdown("---")

    persona = st.radio(
        "Select Your Role",
        ["🩺 Physician", "💼 Billing Staff", "👤 Patient"],
        index=0
    )

    st.markdown("---")

    # API Status
    if check_api():
        st.success("🟢 API Connected")
    else:
        st.error("🔴 API Offline")
        st.info("Run: uvicorn app.api.main:app --reload")

    st.markdown("---")
    st.markdown("### Quick Stats")
    try:
        stats = requests.get(f"{API_URL}/stats", timeout=3).json()
        vs = stats.get("vector_store", {})
        st.metric("Policy Chunks", vs.get("policy_chunks", 0))
        st.metric("Clinical Chunks", vs.get("clinical_chunks", 0))
    except:
        st.metric("Policy Chunks", "—")
        st.metric("Clinical Chunks", "—")

# Main content
st.title("🏥 Healthcare Prior Authorization Platform")
st.markdown(
    "**AI-powered coverage intelligence — "
    "from clinical documentation to authorization decision**"
)
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📋 Authorization Analysis",
    "📁 Upload Documents",
    "📊 History"
])

# ── TAB 1: Authorization Analysis ──
with tab1:
    st.markdown("### Prior Authorization Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Procedure Information")
        procedure = st.text_input(
            "Procedure / Surgery Requested",
            placeholder="e.g., Spinal Fusion L4-L5 (CPT 22612)",
            help="Enter the procedure name and CPT code"
        )

        include_note = st.checkbox(
            "Include Clinical Note",
            value=True
        )

        if include_note:
            clinical_note = st.text_area(
                "Clinical Note / Patient Summary",
                height=300,
                placeholder="""Patient presents with...
Diagnosis: 
ICD-10 Code:
Conservative Treatments:
- Physical therapy: X weeks
- NSAIDs: X months
Procedure Requested: CPT XXXXX
Medical Necessity: ..."""
            )
        else:
            clinical_note = None

    with col2:
        st.markdown("#### Persona-Specific View")

        if "🩺 Physician" in persona:
            st.info("""
**As a Physician, this tool helps you:**
- Identify missing documentation before submission
- Get exact language for medical necessity letters
- Understand insurance requirements in real-time
- Reduce authorization denials proactively
            """)
        elif "💼 Billing" in persona:
            st.info("""
**As Billing Staff, this tool helps you:**
- Catch documentation gaps before submission
- Get step-by-step action items
- Track authorization status
- Reduce claim denial rates
            """)
        else:
            st.info("""
**As a Patient, this tool helps you:**
- Understand if your procedure is covered
- Know your estimated out-of-pocket costs
- Understand what documentation is needed
- Get a timeline for the approval process
            """)

    st.markdown("---")

    if st.button(
        "🚀 Run Authorization Analysis",
        type="primary",
        use_container_width=True
    ):
        if not procedure:
            st.error("Please enter a procedure name")
        elif not check_api():
            st.error("API is offline. Please start the FastAPI server.")
        else:
            with st.spinner(
                "🤖 Multi-agent analysis running... "
                "(Policy → Clinical → Gaps → Recommendations)"
            ):
                try:
                    payload = {"procedure": procedure}
                    if clinical_note:
                        payload["clinical_note"] = clinical_note

                    response = requests.post(
                        f"{API_URL}/analyze",
                        json=payload,
                        timeout=120
                    )
                    result = response.json()

                    if result.get("status") == "success":
                        # Approval likelihood metrics
                        st.markdown("---")
                        st.markdown("### 📊 Analysis Results")

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            likelihood = result.get(
                                "approval_likelihood", 0
                            )
                            color = get_approval_color(likelihood)
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div>Current Likelihood</div>"
                                f"<div class='{color}'>{likelihood}%</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        with m2:
                            after = result.get(
                                "approval_likelihood_after", 0
                            )
                            color2 = get_approval_color(after)
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div>After Fixes</div>"
                                f"<div class='{color2}'>{after}%</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        with m3:
                            improvement = after - likelihood
                            st.markdown(
                                f"<div class='metric-card'>"
                                f"<div>Improvement</div>"
                                f"<div class='approval-high'>"
                                f"+{improvement}%</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown("---")

                        # Show results based on persona
                        if "🩺 Physician" in persona:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                with st.expander(
                                    "📋 Policy Requirements",
                                    expanded=True
                                ):
                                    st.markdown(
                                        result.get("policy_analysis", "")
                                    )
                                with st.expander(
                                    "🔍 Documentation Gaps",
                                    expanded=True
                                ):
                                    st.markdown(
                                        result.get("gap_analysis", "")
                                    )
                            with col_b:
                                with st.expander(
                                    "📝 Clinical Summary",
                                    expanded=True
                                ):
                                    st.markdown(
                                        result.get("clinical_analysis", "")
                                    )
                                with st.expander(
                                    "✅ Your Action Items",
                                    expanded=True
                                ):
                                    recs = result.get("recommendations", "")
                                    # Show physician section only
                                    if "FOR THE PHYSICIAN" in recs:
                                        physician_section = recs.split(
                                            "FOR BILLING STAFF"
                                        )[0]
                                        st.markdown(physician_section)
                                    else:
                                        st.markdown(recs)

                        elif "💼 Billing" in persona:
                            with st.expander(
                                "🔍 Gap Analysis",
                                expanded=True
                            ):
                                st.markdown(
                                    result.get("gap_analysis", "")
                                )
                            with st.expander(
                                "✅ Billing Action Items",
                                expanded=True
                            ):
                                recs = result.get("recommendations", "")
                                if "FOR BILLING STAFF" in recs:
                                    billing_section = recs.split(
                                        "FOR BILLING STAFF"
                                    )[1].split("FOR THE PATIENT")[0]
                                    st.markdown(billing_section)
                                else:
                                    st.markdown(recs)

                        else:  # Patient
                            with st.expander(
                                "ℹ️ Coverage Summary",
                                expanded=True
                            ):
                                policy = result.get("policy_analysis", "")
                                # Show only coverage status
                                lines = policy.split("\n")
                                summary_lines = [
                                    l for l in lines
                                    if any(k in l for k in [
                                        "COVERAGE STATUS",
                                        "CPT CODES",
                                        "REQUIRED"
                                    ])
                                ]
                                st.markdown(
                                    "\n".join(summary_lines)
                                )
                            with st.expander(
                                "📋 What You Need to Do",
                                expanded=True
                            ):
                                recs = result.get("recommendations", "")
                                if "FOR THE PATIENT" in recs:
                                    patient_section = recs.split(
                                        "FOR THE PATIENT"
                                    )[1].split(
                                        "PRIORITY ACTIONS"
                                    )[0]
                                    st.markdown(patient_section)
                                else:
                                    st.markdown(recs)

                        # Full analysis download
                        st.markdown("---")
                        st.download_button(
                            "📥 Download Full Analysis",
                            data=json.dumps(result, indent=2),
                            file_name=f"auth_analysis_{procedure[:20]}.json",
                            mime="application/json"
                        )

                    else:
                        st.error(
                            f"Analysis failed: {result.get('error')}"
                        )

                except requests.exceptions.Timeout:
                    st.error(
                        "Analysis timed out. "
                        "Please try again."
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ── TAB 2: Upload Documents ──
with tab2:
    st.markdown("### Upload Documents")
    st.info(
        "Upload insurance policy PDFs or enter clinical notes "
        "to build your knowledge base."
    )

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:
        st.markdown("#### 📄 Upload Insurance Policy PDF")
        policy_file = st.file_uploader(
            "Choose PDF",
            type=["pdf"],
            key="policy_upload"
        )
        if policy_file and st.button("Upload Policy"):
            with st.spinner("Processing PDF..."):
                try:
                    files = {
                        "file": (
                            policy_file.name,
                            policy_file.getvalue(),
                            "application/pdf"
                        )
                    }
                    r = requests.post(
                        f"{API_URL}/upload/pdf?doc_type=policy",
                        files=files,
                        timeout=60
                    )
                    result = r.json()
                    if result.get("status") == "success":
                        st.success(
                            f"✅ Uploaded! "
                            f"{result['chunks_stored']} chunks stored. "
                            f"{result['pii_entities_found']} PII entities scrubbed."
                        )
                    else:
                        st.error("Upload failed")
                except Exception as e:
                    st.error(f"Error: {e}")

    with upload_col2:
        st.markdown("#### 🏥 Enter Clinical Note")
        clinical_text = st.text_area(
            "Paste clinical note here",
            height=200,
            key="clinical_upload"
        )
        note_name = st.text_input(
            "Note name",
            value="clinical_note_1"
        )
        if st.button("Upload Clinical Note"):
            if clinical_text:
                with st.spinner("Processing..."):
                    try:
                        r = requests.post(
                            f"{API_URL}/upload/text",
                            json={
                                "text": clinical_text,
                                "doc_type": "clinical",
                                "name": note_name
                            },
                            timeout=30
                        )
                        result = r.json()
                        if result.get("status") == "success":
                            st.success(
                                f"✅ Stored "
                                f"{result['chunks_stored']} chunks"
                            )
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter clinical note text")

# ── TAB 3: History ──
with tab3:
    st.markdown("### Authorization History")

    if st.button("🔄 Refresh"):
        st.rerun()

    try:
        r = requests.get(f"{API_URL}/history?limit=20", timeout=5)
        records = r.json().get("records", [])

        if not records:
            st.info(
                "No authorization analyses yet. "
                "Run your first analysis in the Analysis tab."
            )
        else:
            for rec in records:
                likelihood = rec.get("approval_likelihood", 0)
                after = rec.get("approval_likelihood_after", 0)
                color = "🟢" if likelihood >= 75 else \
                        "🟡" if likelihood >= 50 else "🔴"

                with st.expander(
                    f"{color} {rec['procedure']} — "
                    f"{likelihood}% → {after}% | "
                    f"{rec['created_at'][:10]}"
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Initial Likelihood", f"{likelihood}%")
                    with col2:
                        st.metric("After Fixes", f"{after}%")
                    with col3:
                        st.metric(
                            "Improvement",
                            f"+{after - likelihood}%"
                        )

    except Exception as e:
        st.error(f"Could not load history: {e}")

st.markdown("---")
st.markdown(
    "<center>Healthcare Prior Authorization Platform | "
    "Built with LangGraph, OpenAI, ChromaDB, FastAPI</center>",
    unsafe_allow_html=True
)