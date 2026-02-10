import streamlit as st
import google.generativeai as genai
import os
import PyPDF2
from docx import Document
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="Legal Auditor AI", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    h1 { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; border-radius: 5px; }
    .metric-container { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION (SECURE) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

SECURE_PASSWORD = os.environ.get("APP_PASSWORD")

if not st.session_state.auth:
    st.title("🔒 Legal Auditor Login")
    entered_password = st.text_input("Enter Access Password", type="password")
    if entered_password == SECURE_PASSWORD:
        st.session_state.auth = True
        st.rerun()
    elif entered_password:
        st.error("Access Denied.")
    st.stop()

# --- MAIN DASHBOARD ---
st.title("⚖️ Legal Auditor AI")
st.markdown("### Intelligent Contract Risk Analysis")

with st.container():
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("⏱️ Speed")
        st.info("**Saves ~45 Mins/Contract**\n\nInstantly summarizes 50-page agreements.")
    with col2:
        st.header("🛡️ Safety")
        st.warning("**Catch Hidden Risks**\n\nAuto-detects dangerous clauses like 'Uncapped Indemnification'.")
    with col3:
        st.header("💰 Value")
        st.success("**24/7 Junior Associate**\n\nHandles the 'grunt work' of initial review.")
    st.write("---")

# --- ENGINE SETUP (SELF-HEALING) ---
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def get_working_model():
    # Strict list of versions to try. One WILL work.
    candidates = [
        'gemini-1.5-flash-001', # Most likely to work
        'gemini-1.5-flash',
        'gemini-1.5-pro-001',
        'gemini-1.0-pro',
        'gemini-pro'
    ]
    
    for name in candidates:
        try:
            # Create the model
            model = genai.GenerativeModel(name)
            # FIRE A TEST SHOT to prove it works
            model.generate_content("test")
            return model, name # If we get here, it works!
        except:
            continue # If it crashes, try the next one silently
            
    # Fallback if everything explodes (unlikely)
    return genai.GenerativeModel('gemini-1.0-pro'), "gemini-1.0-pro"

# Initialize the verified working model
model, model_name = get_working_model()

# --- SIDEBAR (SMART LIBRARY) ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    # I hid the model name so the user doesn't worry about it
    st.caption("Upload ALL your standard docs here (NDA, MSA, etc).")
    ref_files = st.file_uploader("Reference PDFs", type="pdf", accept_multiple_files=True)
    
    library_text = ""
    if ref_files:
        for ref in ref_files:
            pdf_reader = PyPDF2.PdfReader(ref)
            doc_text = ""
            for page in pdf_reader.pages:
                doc_text += page.extract_text() + "\n"
            library_text += f"\n<reference_doc name='{ref.name}'>\n{doc_text}\n</reference_doc>\n"

# --- MAIN AUDIT TOOL ---
st.header("1. Upload Contract for Audit")
target_files = st.file_uploader("Drag & drop contract (PDF)", type="pdf", accept_multiple_files=True)

if target_files:
    if st.button("🚀 Run Smart Audit"):
        for target in target_files:
            st.subheader(f"📄 Analysis: {target.name}")
            
            with st.spinner(f"Reading {target.name}..."):
                pdf_reader = PyPDF2.PdfReader(target)
                target_text = ""
                for page in pdf_reader.pages:
                    target_text += page.extract_text() + "\n"

            with st.spinner("Auditing contract (this may take 30 seconds)..."):
                prompt = f"""
                <system_role>
                You are a senior General Counsel. You have access to a library of "Gold Standard" reference documents.
                </system_role>

                <library_instructions>
                1. Analyze the 'Document to Audit' below to determine its type.
                2. Search the 'Reference Library' below for the document that best matches that type.
                3. If you find a match, use THAT specific document as the strict standard for grading.
                4. If you do NOT find a match, use general strict market standards.
                </library_instructions>

                <reference_library>
                {library_text if library_text else "No reference documents provided. Use general market standards."}
                </reference_library>
                
                <document_to_audit>
                {target_text[:40000]}
                </document_to_audit>
                
                <task>
                Perform a strict risk audit.
                1. IDENTIFIED DOCUMENT TYPE: (State what type of contract this is and which Reference Doc you are using).
                2. RISK SCORE (1-10)
                3. EXECUTIVE SUMMARY (3 bullets)
                4. CRITICAL REDLINES (Top 3 deviations from the selected standard)
                </task>
                """
                
                try:
                    response = model.generate_content(prompt)
                    report_text = response.text
                    st.markdown(report_text)
                    
                    doc = Document()
                    doc.add_heading(f'Audit Report: {target.name}', 0)
                    doc.add_paragraph(report_text)
                    bio = BytesIO()
                    doc.save(bio)
                    
                    st.download_button(
                        label=f"💾 Download Report ({target.name})",
                        data=bio.getvalue(),
                        file_name=f"Audit_{target.name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key=target.name
                    )
                except Exception as e:
                    st.error(f"Analysis Failed. Please try refreshing the page. Error: {e}")
