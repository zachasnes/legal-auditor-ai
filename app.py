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
    .sidebar .sidebar-content { background: #ffffff; }
    h1 { color: #1e3a8a; }
    .stButton>button { background-color: #1e3a8a; color: white; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Legal Auditor AI")
st.markdown("### Contract Risk Analysis & Redlining")

# --- AUTH ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    password = st.text_input("Enter Access Password", type="password")
    if password == "LegalEagle2026":
        st.session_state.auth = True
        st.rerun()
    st.stop()

# --- SETUP ENGINE ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.error("System Error: API Key missing.")
    st.stop()

genai.configure(api_key=api_key)

# *** THE FIX: USING THE EXACT MODEL NAME FROM YOUR LIST ***
try:
    model = genai.GenerativeModel('gemini-flash-latest')
except:
    # Fallback just in case
    model = genai.GenerativeModel('gemini-pro')

# --- SIDEBAR: KNOWLEDGE BASE ---
with st.sidebar:
    st.header("📂 Knowledge Base")
    st.info("Upload your standard templates (NDAs, MSAs) here.")
    ref_files = st.file_uploader("Reference Standards", type="pdf", accept_multiple_files=True)
    
    ref_text = ""
    if ref_files:
        for ref in ref_files:
            pdf_reader = PyPDF2.PdfReader(ref)
            for page in pdf_reader.pages:
                ref_text += page.extract_text() + "\n"
        st.success(f"✅ {len(ref_files)} Standards Loaded")

# --- MAIN: AUDIT ---
st.write("---")
st.header("1. Upload Contract")
target_files = st.file_uploader("Drag & drop the contract to audit (PDF)", type="pdf", accept_multiple_files=True)

if target_files:
    if st.button("🚀 Run Executive Audit"):
        for target in target_files:
            st.write("---")
            st.subheader(f"📄 Analysis: {target.name}")
            
            with st.spinner("Reading contract..."):
                pdf_reader = PyPDF2.PdfReader(target)
                target_text = ""
                for page in pdf_reader.pages:
                    target_text += page.extract_text() + "\n"

            with st.spinner("Consulting Knowledge Base & Generating Report..."):
                # The Executive Prompt
                prompt = f"""
                You are a senior General Counsel. 
                
                CONTEXT (My Standards): 
                {ref_text[:30000] if ref_text else "No specific standards provided. Use strict market-standard best practices."}
                
                CONTRACT TO AUDIT: 
                {target_text[:40000]}
                
                TASK:
                Perform a strict risk audit.
                
                OUTPUT FORMAT:
                1. **RISK SCORE:** Give a score from 1-10 (10=Safe, 1=High Risk).
                2. **EXECUTIVE SUMMARY:** 3 bullet points summarizing the deal breakers.
                3. **CRITICAL REDLINES:** Identify the top 3 risky clauses. For each, provide:
                   - *The Risky Text*
                   - *Why it's dangerous*
                   - *Suggested Redline (New Text)*
                """
                
                try:
                    response = model.generate_content(prompt)
                    report_text = response.text
                    
                    # Display Report
                    st.markdown(report_text)
                    
                    # --- EXPORT TO WORD FEATURE ---
                    doc = Document()
                    doc.add_heading(f'Audit Report: {target.name}', 0)
                    doc.add_paragraph(report_text)
                    
                    # Save to memory buffer
                    bio = BytesIO()
                    doc.save(bio)
                    
                    st.download_button(
                        label="💾 Download Report as Word Doc",
                        data=bio.getvalue(),
                        file_name=f"Audit_Report_{target.name}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
                except Exception as e:
                    st.error(f"Analysis Failed: {e}")

# --- FOOTER ---
st.write("---")
st.caption("⚠️ **Legal Disclaimer:** This tool uses Artificial Intelligence to analyze documents. It is not a lawyer.")
