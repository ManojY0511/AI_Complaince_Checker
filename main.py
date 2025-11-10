###################################################################################
# Script : main.py 
# Author : Manoj 
# Date : 09/11/2025
# Description :   Main file for processing the data . To develop an AI-powered 
#                  system that processes document files and checks compliance against English guidelines and 
#                  corrected doc available for download.
# Version : 1.0 
##################################################################################

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from spacy.pipeline import Sentencizer  # noqa: F401
import spacy
import en_core_web_sm
import language_tool_python

from fastapi.responses import FileResponse
import tempfile
from docx import Document
import os


app = FastAPI(title='AI Powered English Complaince Checker',version='1.0.0')

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

router = APIRouter()
router.include_router(router, tags=["home"])

class TextRequest(BaseModel):
    file_text: str
    filename: str = "eng_complaince_document.docx"  # optional

  # ----nlp processing here ----
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')
nlp = en_core_web_sm.load()
    
@app.post("/complaince_checker")
def complaince_check(request : TextRequest):
    '''
    arg : request text (pdf/doc text extracted)
    This method will check the text for english language complaince using Spacy and language tool python 
    and generate a report based on sentence , grammer errors , long sentences etc .. 
    '''
    print(' Have a fun calling the fastapi endpoint from streamlit ')

    request_text = request.file_text.strip()
    if not request_text:
        return {"error": "Empty text received"}
    
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")  # added since a single sentence was read only 
    doc = nlp(request_text)

    # --- spaCy Analysis ---
    sentence_results = []
    passive_count = 0
    long_sent_count = 0

    # Looping over documents to detect passive wording in sentences
    for sent in doc.sents:
        sent_text = sent.text.strip()
        is_passive = detect_passive(sent)
        is_long = len(sent) > 25
        if is_passive:
            passive_count += 1
        if is_long:
            long_sent_count += 1

        sentence_results.append({
            "sentence": sent_text,
            "token_count": len(sent),
            "passive_voice": is_passive,
            "long_sentence": is_long,
            "structure": [
                {"text": token.text, "pos": token.pos_, "dep": token.dep_}
                for token in sent
            ],
        })

    # --- Grammar & Spelling Check ---
    matches = tool.check(request_text)
    grammar_issues = [
        {
            "message": match.message,
            "suggestions": match.replacements,
            "error_text": request_text[match.offset: match.offset + match.errorLength],
            "rule_id": match.ruleId
        }
        for match in matches
    ]

    # --- Summary Report Generation ---
    summary = {
        "total_sentences": len(sentence_results),
        "avg_sentence_length": sum(s["token_count"] for s in sentence_results) / max(1, len(sentence_results)),
        "num_passive_sentences": passive_count,
        "num_long_sentences": long_sent_count,
        "num_grammar_issues": len(grammar_issues),
    }

    return {
        "summary": summary,
        "grammar_issues": grammar_issues
    }


def detect_passive(sentence):
    """
    Detect passive voice using dependency tags.
    Looks for 'auxpass' (passive auxiliaries) and 'nsubjpass' (passive subjects)
    """
    for token in sentence:
        if token.dep_ in ("auxpass", "nsubjpass"):
            return True
    return False

@app.post("/correct_document")
def correct_document(request: TextRequest):
    """
    Automatically correct grammar issues and return a corrected document for download.
    """
    print(' Calling the corrected grammer .... ')
    text = request.file_text.strip()
    if not text:
        return {"error": "Empty text received"}
    
    # Apply grammar corrections using LanguageTool
    corrected_text = tool.correct(text)

    # Create a temporary corrected DOCX file
    temp_dir = tempfile.mkdtemp()
    corrected_path = os.path.join(temp_dir, request.filename)

    doc = Document()
    for paragraph in corrected_text.split("\n"):
        doc.add_paragraph(paragraph.strip())
    doc.save(corrected_path)

    return FileResponse(
        corrected_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=request.filename
    )

if __name__=='__main__':
    import uvicorn
    uvicorn.run("main:app",host="127.0.0.1",port=8000)


