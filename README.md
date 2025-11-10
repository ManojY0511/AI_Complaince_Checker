### Run below steps for this project : 

`uv add     "fastapi>=0.121.1"  `
`uv add     "language-tool-python>=2.9.5" `
`uv add     "pip>=25.3" `
`uv add     "pypdf2>=3.0.1" `
`uv add     "python-docx>=1.2.0" `
`uv add     "spacy>=3.8.8" `
`uv add     "streamlit>=1.51.0" `
`uv add     "textstat>=0.7.11" `
`uv add spacy language-tool-python textstat `
`uv run python -m spacy download en_core_web_sm  `


### Start the Streamlit Server 
` uv run streamlit run user_chat.py `

### Start the FastAPI Server
` uv run main.py  `
