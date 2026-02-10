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

# Secure Password Check
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

# --- THE NEW "WHY USE THIS" SECTION ---
with st.container():
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.header("⏱️ Speed")
        st.info("**Saves ~45 Mins/Contract**\n\nInstantly summarizes 50-page agreements into a 1-page executive brief.")
        
    with col2:
        st.header("🛡️ Safety")
        st.warning("**Catch Hidden Risks**\n\nAuto-detects dangerous clauses like 'Uncapped Indemnification' that tired eyes might miss.")
        
    with col3:
        st.header("💰 Value")
        st.success("**24/7 Junior Associate**\n\nHandles the 'grunt work' of initial review so you can focus on high-level strategy.")
    st.write("---")

# --- ENGINE SETUP ---
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    st.caption("Upload your 'Gold Standard' contracts here to teach the AI what you like.")
    ref_files = st.file_uploader("Reference PDFs", type="pdf", accept_multiple_files=True)
    ref_text = ""
    if ref_files:
        for ref in ref_files:
            pdf_reader = PyPDF2.PdfReader(ref)
            for page in pdf_reader.pages:
                ref_text += page.extract_text() + "\n"

# --- MAIN AUDIT TOOL ---
st.header("1. Upload Contract for Audit")
target_files = st.file_uploader("Drag & drop contract (PDF)", type="pdf", accept_multiple_files=True)

if target_files:
    if st.button("🚀 Run Executive Audit"):
        for target in target_files:
            st.subheader(f"📄 Analysis: {target.name}")
            
            with st.spinner("Reading contract terms..."):
                pdf_reader = PyPDF2.PdfReader(target)
                target_text = ""
                for page in pdf_reader.pages:
                    target_text += page.extract_text() + "\n"

            with st.spinner("Identifying risks & generating report..."):
                # --- SECURE PROMPT ---
                prompt = f"""
                <system_role>
                You are a senior General Counsel. Your ONLY task is to audit the contract below.
                </system_role>

                <context_standards>
                {ref_text[:30000] if ref_text else "Use strict market standards."}
                </context_standards>
                
                <document_to_audit>
                {target_text[:40000]}
                </document_to_audit>
                
                <task>
                Perform a strict risk audit.
                1. RISK SCORE (1-10)
                2. EXECUTIVE SUMMARY (3 bullets)
                3. CRITICAL REDLINES (Top 3)
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
                        label="💾 Download Word Doc",
                        data=bio.getvalue(),
                        file_name=f"Audit_{target.name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.error(f"Analysis Failed: {e}")
