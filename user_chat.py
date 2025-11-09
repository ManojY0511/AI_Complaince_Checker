# Script : User Upload Doc and Interface 
# Author : Manoj 

import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import requests 

st.set_page_config(page_title="Document Processor", page_icon="📄")

st.title("📄 Document Processor")
st.write("Upload a PDF or Word document to process its content.")

# File uploader (only PDF or DOCX)
uploaded_file = st.file_uploader(
    "Choose a file", 
    type=["pdf", "docx"], 
    help="Only PDF or Word (.docx) files are supported."
)

text=""
if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Process based on file type
    if uploaded_file.type == "application/pdf":
        st.subheader("PDF File Preview")
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
            print(f' value of extracted text is {text}')
        st.text_area("Extracted Text", text, height=300)

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.subheader("Word Document Preview")
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        st.text_area("Extracted Text", text, height=300)

    # Example: Process button
    # if st.button("Process Document"):
    #     st.info("🔄 Processing...")
    #     # API call to AI agent to assess the document against given English guidelines 

    #     st.success("✅ Done processing!")
    # Send text to FastAPI when button is clicked
    if st.button("🚀 Process Document"):
        if not text.strip():
            st.warning("No text found in document.")
        else:
            st.info("🔄 Sending text to FastAPI for processing...")
            try:
                response = requests.post(
                    "http://localhost:8000/complaince_checker",
                    json={"file_text": text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Processing complete!")
                    st.write("### Response from FastAPI:")
                    # st.json(result)

                    '''
                    code added for better view of Results 
                    '''
                    summary = result.get("summary", {})
                    st.subheader("📊 Summary Overview")
                    cols = st.columns(3)
                    cols[0].metric("🧾 Total Sentences", summary.get("total_sentences", 0))
                    cols[1].metric("🕵️ Passive Sentences", summary.get("num_passive_sentences", 0))
                    cols[2].metric("📏 Avg Sentence Length", f"{summary.get('avg_sentence_length', 0):.2f}")

                    cols = st.columns(3)
                    cols[0].metric("✍️ Long Sentences (>25 tokens)", summary.get("num_long_sentences", 0))
                    cols[1].metric("🔍 Grammar Issues", summary.get("num_grammar_issues", 0))

              
                    # Grammar Issues
                    st.subheader("✍️ Grammar & Spelling Issues")
                    issues = result.get("grammar_issues", [])
                    if issues:
                        for issue in issues[:30]:  # limit for large docs
                            st.markdown(f"**⚠️ {issue['message']}**")
                            st.write(f"- Error Text: `{issue['error_text']}`")
                            if issue["suggestions"]:
                                st.write(f"- Suggestions: {', '.join(issue['suggestions'])}")
                            st.caption(f"Rule ID: {issue['rule_id']}")
                            st.divider()
                    else:
                        st.success("🎉 No grammar issues detected!")
                else:
                    st.error(f"❌ FastAPI returned {response.status_code}: {response.text}")

                                # Readability Metrics
                
                    
                            
            
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Error communicating with FastAPI: {e}")

else:
    st.info("Please upload a PDF or DOCX file to begin. File Not Supported!! ")

