# ⚖️ Legal Auditor AI

### AI-Powered Contract Risk Analysis & Redlining Tool

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Run-4285F4)
![Gemini](https://img.shields.io/badge/AI-Gemini_1.5_Flash-8E75B2)

**Legal Auditor AI** is a serverless application designed to automate the review of legal contracts (NDAs, MSAs, SaaS Agreements). It utilizes Google's **Gemini 1.5 Flash** LLM to score risk, identify dangerous clauses, and generate redlined reports in real-time.

---

## 🚀 Live Demo
**Production URL:** [https://legal-auditor-v5-222062225028.us-central1.run.app](https://legal-auditor-v5-222062225028.us-central1.run.app)  
*(Access requires authorized credentials. Contact owner for demo access.)*

---

## 🛠️ Technical Architecture

### 1. The Engine (Generative AI)
* **Model:** Google Gemini 1.5 Flash (chosen for low latency and high token context).
* **Context Injection:** Uses a "Gold Standard" knowledge base to benchmark incoming contracts against preferred legal standards (RAG-lite architecture).
* **Prompt Engineering:** Specialized "Senior Counsel" persona prompts to enforce strict risk scoring (1-10).

### 2. The Infrastructure (Serverless Cloud)
* **Backend:** Python (Streamlit) containerized via Docker.
* **Deployment:** Google Cloud Run (fully managed serverless environment).
* **DevOps:** Automated deployment pipeline via Google Cloud Shell.

### 3. Security & FinOps
* **Authentication:** Application-level password protection (`st.session_state` management).
* **Cost Control:** Hard-coded `max-instances=1` limits to prevent runaway scaling costs.
* **Budgeting:** Integrated Google Cloud Budget Alerts for cost monitoring.

---

## ✨ Key Features
* **Risk Scoring:** Instantly grades contracts on a 1-10 safety scale.
* **Automated Redlining:** Identifies specific clauses (Indemnification, Termination) and rewrites them.
* **Docx Export:** One-click generation of a Word document report for legal counsel review.
* **Multi-File Processing:** Handles multiple PDF contracts simultaneously.

---

## 💻 Local Installation

To run this tool locally:

```bash
# 1. Clone the repo
git clone [https://github.com/zachasnes/legal-auditor-ai.git](https://github.com/zachasnes/legal-auditor-ai.git)
cd legal-auditor-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API Key
export GOOGLE_API_KEY="your_gemini_key_here"

# 4. Run the app
streamlit run app.py
