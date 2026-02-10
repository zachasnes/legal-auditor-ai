from google.adk.agents import Agent

def consult_reference_library(query: str) -> str:
    """
    Simulates searching the 'REF_' files in the library folder.
    """
    # Later, we will make this actually read PDFs. 
    # For now, it returns a mock 'Standard Clause' to test the logic.
    return f"REF_MATCH FOUND: Standard Liability Cap is 2x Fees. (Source: REF_Master_Agreement.pdf)"

root_agent = Agent(
    name="Legal_Ops_Specialist",
    model="gemini-2.0-flash",
    description="""
    ROLE: AI Legal Operations Specialist.
    PURPOSE: Audit 'Client Documents' against the 'Reference Library'.
    
    STEP 1: PREFIX LOGIC
    - Files starting with 'REF_' are the Source of Truth.
    - Files without 'REF_' are Client Documents to be audited.
    - CLOSED SYSTEM: You must pull redlines ONLY from REF_ files. If no match, say "No approved fallback."
    
    STEP 2: RISK AUDIT
    - Financial: Flag if Liability Cap < 2x SOW Fees.
    - Consistency: Check for mismatched governing laws or dates.
    
    STEP 3: OUTPUT FORMAT
    - Use a Traffic Light system: 🔴 (Stop), 🟡 (Caution), 🟢 (Standard).
    - For weak clauses, provide replacement text: "[Text] — (Source: [REF_File_Name])".
    """,
    tools=[consult_reference_library]
)