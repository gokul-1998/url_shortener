# filename: main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import string, random

app = FastAPI()

# Store shortened URLs in memory
url_mapping = {}

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten")
async def shorten_url(request: Request):
    data = await request.json()
    original_url = data.get("url")

    if not original_url:
        raise HTTPException(status_code=400, detail="URL is required")

    code = generate_short_code()
    url_mapping[code] = original_url

    # Replace 'go.gokul.dev' with your actual domain (once deployed)
    short_url = f"https://go.gokul.dev/{code}"
    return {"short_url": short_url}

@app.get("/{code}")
async def redirect(code: str):
    original_url = url_mapping.get(code)
    if original_url:
        return RedirectResponse(original_url)
    raise HTTPException(status_code=404, detail="URL not found")
