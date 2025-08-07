from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import string, random

from database import database, URL

app = FastAPI()

# Connect to DB on startup and shutdown
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Request model
class URLRequest(BaseModel):
    url: str

BASE_DOMAIN = "http://localhost:8000"

# Generate short code
async def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(random.choices(characters, k=length))
        query = URL.__table__.select().where(URL.short_code == short_code)
        existing = await database.fetch_one(query)
        if not existing:
            return short_code

# Shorten API
@app.post("/shorten")
async def shorten_url(request: URLRequest):
    long_url = request.url

    # Check if URL already exists
    query = URL.__table__.select().where(URL.long_url == long_url)
    existing = await database.fetch_one(query)

    if existing:
        short_code = existing["short_code"]
    else:
        short_code = await generate_short_code()
        insert_query = URL.__table__.insert().values(short_code=short_code, long_url=long_url)
        await database.execute(insert_query)

    short_url = f"{BASE_DOMAIN}/{short_code}"
    return {"short_url": short_url}

# Redirect handler
@app.get("/{short_code}")
async def redirect_url(short_code: str):
    query = URL.__table__.select().where(URL.short_code == short_code)
    row = await database.fetch_one(query)

    if row:
        return RedirectResponse(url=row["long_url"])
    raise HTTPException(status_code=404, detail="URL not found")
