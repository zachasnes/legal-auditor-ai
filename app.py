import streamlit as st
import os

# Import modular enterprise logic
from core.document_processor import extract_text_from_pdfs, chunk_pdf_document
from core.llm_engine import setup_llm, get_best_model, generate_audit_report
from core.report_generator import create_word_report

# --- PAGE CONFIG ---
st.set_page_config(page_title="SafeShip Legal Auditor", page_icon="⚖️", layout="wide")

# --- CUSTOM CSS FOR PREMIUM UI ---
st.markdown("""
<style>
    /* Minimalist Uber Typography */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Login Card */
    .login-container {
        display: flex;
        justify-content: center;
        margin-top: 10vh;
    }
    .login-card {
        background: #111111;
        padding: 40px;
        border-radius: 4px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 1px solid #333333;
        max-width: 450px;
        text-align: center;
    }
    
    /* Subtext enhancements */
    .secure-subtext {
        font-size: 0.85rem;
        color: #A0AEC0;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    /* File uploader enhancements */
    .stFileUploader > div > div {
        background-color: #0A0A0A !important;
        border: 2px dashed #333333 !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- AUTHENTICATION ---
if "auth" not in st.session_state:
    st.session_state.auth = False

SECURE_PASSWORD = os.environ.get("APP_PASSWORD") 

# Dev Override: Automatically bypass auth if no password exists in environment
if SECURE_PASSWORD is None: 
    st.session_state.auth = True

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container"><div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h1>⚖️ SafeShip Legal Auditor</h1>", unsafe_allow_html=True)
        st.markdown('<p class="secure-subtext">🔒 Secure Access Portal: Client data is encrypted and deleted immediately after processing.</p>', unsafe_allow_html=True)
        
        entered_password = st.text_input("Enter Attorney Access Password", type="password")
        if st.button("Secure Login", use_container_width=True):
            if entered_password == SECURE_PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop()

# --- ENGINE SETUP (AUTO-DISCOVERY) ---
setup_llm()

@st.cache_resource
def cached_best_model():
    return get_best_model()

model, model_name = cached_best_model()

# --- MAIN HEADER (UBER STYLE) ---
st.title("⚖️ SafeShip Auditor")
st.markdown("Upload your controlling playbook and the counterparty draft to instantly generate a deviation matrix.")
st.divider()

# --- STEP 1 & 2: UPLOAD DOCUMENTS (UBER STYLE - VERTICAL) ---
st.subheader("1. Your Source of Truth")
source_files = st.file_uploader("Upload Playbook or Master Agreement (.pdf)", type="pdf", accept_multiple_files=True, key="source")
source_text = ""
if source_files:
    st.success(f"✅ Loaded {len(source_files)} Source Document(s)")
    source_text = extract_text_from_pdfs(source_files)

st.write("") # Spacer

st.subheader("2. The Counterparty Draft")
target_files = st.file_uploader("Upload Incoming Draft for Review (.pdf)", type="pdf", accept_multiple_files=True, key="target")
if target_files:
    st.success(f"✅ Loaded {len(target_files)} Target Document(s)")

st.divider()

# --- STEP 3: SETTINGS (MOVED FROM SIDEBAR) ---
st.subheader("3. Audit Configuration")
c1, c2 = st.columns(2)

with c1:
    client_type = st.selectbox("I represent the:", ["Landlord", "Tenant", "Buyer", "Seller", "Lender", "Borrower"])
    
with c2:
    review_mode = st.radio(
        "Review Logic:",
        ["Playbook Match (Concept Search)", "Literal Redline (Word-for-Word)"],
        horizontal=True
    )

# --- TRIGGER ACTIONS ---
st.divider()

# Determine if button should be disabled
can_run = bool(source_files and target_files)

# Helper function to parse LLM Markdown table into Dicts for Streamlit Dataframe
def parse_markdown_to_data(markdown_text):
    lines = markdown_text.strip().split('\\n')
    table_lines = [line.strip() for line in lines if line.strip().startswith('|')]
    if len(table_lines) <= 2:
        return None
    headers = [c.strip() for c in table_lines[0].split('|')][1:-1]
    data = []
    for row_line in table_lines[2:]:
        cols = [c.strip() for c in row_line.split('|')][1:-1]
        if len(cols) == len(headers):
            data.append({headers[i]: cols[i] for i in range(len(headers))})
    return data

if st.button("🚀 Run Comparison Audit", type="primary", disabled=not can_run, use_container_width=True):
    for target in target_files:
        st.subheader(f"🔍 Deviation Report: {target.name}")
        
        # 1. Chunk the Target PDF
        chunks = chunk_pdf_document(target, chunk_size=5)

        try:
            all_responses = []
            
            # Contextual progress text
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            # 2. Process Each Chunk
            for idx, chunk in enumerate(chunks):
                status_messages = [
                    f"Extracting Playbook standards (Part {idx + 1}/{len(chunks)})...",
                    f"Scanning Counterparty Draft for risks (Part {idx + 1}/{len(chunks)})...",
                    f"Cross-referencing liability clauses (Part {idx + 1}/{len(chunks)})..."
                ]
                status_text.caption(f"⏳ {status_messages[idx % len(status_messages)]}")
                
                response_text = generate_audit_report(
                    model=model,
                    client_type=client_type,
                    review_mode=review_mode,
                    source_text=source_text,
                    chunk_text=chunk,
                    current_part=idx + 1,
                    total_parts=len(chunks)
                )
                all_responses.append(response_text)
                
                progress_bar.progress((idx + 1) / len(chunks))
            
            status_text.empty()
            progress_bar.empty()
            st.success("✅ Analysis Complete!")
            
            combined_response_text = "\\n".join(all_responses)
            
            # 3. Rich Data Display in tabs
            tab1, tab2 = st.tabs(["📊 Interactive Data Table", "📄 Raw Audit Matrix"])
            
            with tab1:
                # Try parsing the combined markdown into a clean dataframe
                parsed_data = parse_markdown_to_data(combined_response_text)
                if parsed_data:
                    st.dataframe(parsed_data, use_container_width=True)
                else:
                    st.info("The AI did not find any tabular deviations, or returned pure text.")
                    st.write(combined_response_text)
            
            with tab2:
                st.markdown(combined_response_text)

            # 4. Generate the Final Report
            bio = create_word_report(
                target_name=target.name,
                review_mode=review_mode,
                client_type=client_type,
                combined_markdown_text=combined_response_text
            )
            
            st.download_button(
                label="💾 Download Professional Word Report",
                data=bio.getvalue(),
                file_name=f"Audit_{target.name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        except Exception as e:
            st.error(f"AI Engine Error: {str(e)}")