from fastapi import FastAPI, responses, Form
import requests

app = FastAPI()


@app.get("/", response_class=responses.HTMLResponse)
def home():
    return """
	<html>
        <body>
            <h1>Hello FastAPI</h1>
            <form method="post" action="/ask">
                <input name="query" />
                <button type="submit">Send</button>
            </form>
        </body>
    </html>
"""

@app.post("/ask")
def ask(query: str = Form()):
	webhook = f"http://localhost:5678/webhook/ask?query={query}"
	r = requests.post(webhook)
	return responses.JSONResponse(content=r.json())
