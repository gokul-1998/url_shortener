# filename: main.py

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
import sqlite3
import string
import random
from pydantic import BaseModel

app = FastAPI()

# SQLite setup
conn = sqlite3.connect("urls.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT UNIQUE,
        long_url TEXT
    )
""")
conn.commit()

# Model for shortening request
class URLRequest(BaseModel):
    url: str

# Base domain (change this to your custom domain)
BASE_DOMAIN = "http://localhost:8000"

# Function to generate short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        cursor.execute("SELECT * FROM urls WHERE short_code=?", (short_code,))
        if not cursor.fetchone():
            return short_code

# API to shorten URL
@app.post("/shorten")
async def shorten_url(request: URLRequest):
    long_url = request.url
    # Check if URL already exists
    cursor.execute("SELECT short_code FROM urls WHERE long_url=?", (long_url,))
    row = cursor.fetchone()
    if row:
        short_code = row[0]
    else:
        short_code = generate_short_code()
        cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        conn.commit()
    short_url = f"{BASE_DOMAIN}/{short_code}"
    return {"short_url": short_url}

# Redirect handler
@app.get("/{short_code}")
async def redirect_url(short_code: str):
    cursor.execute("SELECT long_url FROM urls WHERE short_code=?", (short_code,))
    row = cursor.fetchone()
    if row:
        return RedirectResponse(row[0])
    raise HTTPException(status_code=404, detail="URL not found")
