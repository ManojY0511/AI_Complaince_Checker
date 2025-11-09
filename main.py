# Script : main.py 
# Author : manoj 
# Date : 09/11/2025
#   Main file for processing the data . To evaluate the candidate’s ability to develop an AI-powered 
#   system that processes document files and checks compliance against English guidelines


from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel 
from spacy.pipeline import Sentencizer  # noqa: F401
import spacy
import en_core_web_sm
import language_tool_python


app = FastAPI(title='AI Powered Complaince Checker',version='1.0.0')

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

@app.post("/complaince_checker")
def complaince_check(request : TextRequest):
    # return {"exists": os.path.exists(image_path)}
    print(' have a fun calling the fastapi endpoint from streamlit ')
    # same mean for both lines here
    request_text = request.file_text.strip()
    if not request_text:
        return {"error": "Empty text received"}
    
    nlp = spacy.load("en_core_web_sm")
    tool = language_tool_python.LanguageTool('en-US')
    # nlp = spacy.load("en_core_web_sm", disable=[])
    nlp = en_core_web_sm.load()
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")  # added since a single sentence was read only 
    doc = nlp(request_text)

    # --- spaCy Analysis ---
    sentence_results = []
    passive_count = 0
    long_sent_count = 0

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

    # --- Readability Metrics ---
    # readability = {
    #     "flesch_reading_ease": textstat.flesch_reading_ease(request_text),
    #     "flesch_kincaid_grade": textstat.flesch_kincaid_grade(request_text),
    #     "smog_index": textstat.smog_index(request_text),
    #     "automated_readability_index": textstat.automated_readability_index(request_text),
    #     "dale_chall_score": textstat.dale_chall_readability_score(request_text),
    # }

    # --- Summary ---
    summary = {
        "total_sentences": len(sentence_results),
        "avg_sentence_length": sum(s["token_count"] for s in sentence_results) / max(1, len(sentence_results)),
        "num_passive_sentences": passive_count,
        "num_long_sentences": long_sent_count,
        "num_grammar_issues": len(grammar_issues),
    }

    return {
        "summary": summary,
        # "readability": readability,
        "grammar_issues": grammar_issues
        #"analysis": sentence_results
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

    # for token in doc:
    #     print(token.text, token.pos_, token.dep_)
    # tokens = [
    #     {"text": token.text, "pos": token.pos_, "dep": token.dep_}
    #     for token in doc
    # ]
        
    # return {"message": "NLP processing complete", "tokens": tokens}
    # return {
    #     "exists": "You are at a good point here for API Endpoint",
    #     "received_length": len(request.file_text)
    # }

if __name__=='__main__':
    import uvicorn
    uvicorn.run("main:app",host="0.0.0.0",port=8000)


