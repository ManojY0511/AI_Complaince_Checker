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
import textstat


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
    # doc = nlp(sentences[0])
    text_results= []
    print("Number of sentences detected:", len(list(doc.sents)))
    print("Processed text:", doc.text)
    for sent in doc.sents:
        print(f' Sent data received is : {sent}')
        sent_info = {
            "sentence": sent.text.strip(),
            "token_count": len(sent),
            "passive_voice": detect_passive(sent),
            "long_sentence": len(sent) > 25,  # flag if > 25 tokens
            "structure": [
                {"text": token.text, "pos": token.pos_, "dep": token.dep_}
                for token in sent
            ],
        }
        text_results.append(sent_info)

    # Aggregate summary
        summary = {
            "total_sentences": len(text_results),
            "avg_sentence_length": sum(r["token_count"] for r in text_results) / len(text_results),
            "num_passive_sentences": sum(1 for r in text_results if r["passive_voice"]),
            "num_long_sentences": sum(1 for r in text_results if r["long_sentence"]),
        }
        return {
        "summary": summary,
        "analysis": text_results
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


