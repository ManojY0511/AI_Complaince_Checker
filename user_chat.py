###################################################################################
# Script : user_chat.py 
# Author : Manoj 
# Date : 09/11/2025
# Description : User Upload Doc and Interface 
# Version : 1.0 
##################################################################################### 

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import requests
from collections import defaultdict
import io 
import os  

st.set_page_config(page_title="AI Powered English Compliance Checker", page_icon="📄")
st.title("📄 AI Powered Compliance Checker")
st.write("Upload a PDF or Word Document Only For Processing Its Content.")

# -------------------STREAMLITE SESSION STATE INITIALIZATION -------------------
if "text" not in st.session_state:
    st.session_state.text = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "processed" not in st.session_state:
    st.session_state.processed = False
# -------------------------------------------------------------------

uploaded_file = st.file_uploader(
    "Choose a file", 
    type=["pdf", "docx"], 
    help="Only PDF or Word (.docx) files are supported."
)

# Uploading the file 
if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Extract text only once per file
    if st.session_state.text == "":
        if uploaded_file.type == "application/pdf":
            pdf_reader = PdfReader(uploaded_file)
            st.session_state.text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            st.session_state.text = "\n".join(p.text for p in doc.paragraphs)

    st.text_area("Extracted Text", st.session_state.text, height=300)

    # ------------------ PROCESS DOCUMENT BUTTON ------------------
    if st.button("🚀 Process Document"):
        if not st.session_state.text.strip():
            st.warning("No text found in document.")
        else:
            st.info("🔄 Processing the Document .....")
            try:
                response = requests.post(
                    "http://localhost:8000/complaince_checker",
                    json={"file_text": st.session_state.text},
                    timeout=240
                )
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    st.session_state.processed = True
                    st.success("✅ Processing completed! Please Check Below Reports ")
                else:
                    st.error(f"❌ FastAPI returned {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Error communicating with FastAPI: {e}")
    # --------------------------------------------------------------

    # ------------------ DISPLAY RESULTS (if processed) ------------------
    # ----  Result Summary For Document Here 
    if st.session_state.processed and st.session_state.result:
        result = st.session_state.result
        summary = result.get("summary", {})
        st.subheader("📊 Summary Overview")
        cols = st.columns(3)
        cols[0].metric("🧾 Total Sentences", summary.get("total_sentences", 0))
        cols[1].metric("🕵️ Passive Sentences", summary.get("num_passive_sentences", 0))
        cols[2].metric("📏 Avg Sentence Length", f"{summary.get('avg_sentence_length', 0):.2f}")
        cols = st.columns(3)
        cols[0].metric("✍️ Long Sentences (>25 tokens)", summary.get("num_long_sentences", 0))
        cols[1].metric("🔍 Grammar Issues", summary.get("num_grammar_issues", 0))

        # Grammar issues grouped
        st.subheader("✍️ Grammar & Spelling Issues")
        issues = result.get("grammar_issues", [])
        if issues:
            grouped = defaultdict(list)
            for issue in issues:
                grouped[issue["rule_id"]].append(issue)

            st.write(f"Detected **{len(issues)}** issues across **{len(grouped)}** grammar rules.")
            for rule_id, rule_issues in grouped.items():
                with st.expander(f"📘 Rule: {rule_id} ({len(rule_issues)} issues)"):
                    for i, issue in enumerate(rule_issues, 1):
                        st.markdown(f"**{i}. {issue['message']}**")
                        st.write(f"- Error Text: `{issue['error_text']}`")
                        if issue["suggestions"]:
                            st.write(f"- Suggestions: {', '.join(issue['suggestions'])}")
        else:
            st.success("🎉 No grammar issues detected!")

# -----------  Generate Corrected Document For Download Here ----------------------

        st.divider()
        st.subheader("🛠 Modify Document to Comply with English Guidelines")
        if st.button("✍️ Generate Corrected Document"):
            st.info("Requesting corrections from FastAPI...")
            try:
                file_base, _ = os.path.splitext(uploaded_file.name)
                corrected_filename = f"corrected_{file_base}.docx"  # clean filename
                response = requests.post(
                    'http://localhost:8000/correct_document',
                    json={
                        "file_text": st.session_state.text,
                        "filename": f"corrected_{uploaded_file.name}"
                    }
                )
                if response.status_code == 200:
                    st.success("✅ Corrected document ready!")
                    corrected_bytes = io.BytesIO(response.content)
                    st.download_button(
                        label="📥 Download Corrected File",
                        data=corrected_bytes,
                        file_name=corrected_filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                else:
                    st.error(f"❌ Error: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Error communicating with FastAPI: {e}")
# ---------------------------------------------------------------------

else:
    st.info("Please upload a PDF or DOCX file to begin.")

###  End of Document 
