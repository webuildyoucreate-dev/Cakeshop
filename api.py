from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import sqlite3
from datetime import datetime
import uuid

app = FastAPI(title="Artisan Cakeshop API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

DB_FILE = "quotes.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            date TEXT NOT NULL,
            cart TEXT NOT NULL,
            submitted_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# --- Data Models ---

class CartItem(BaseModel):
    name: str
    imageSrc: str
    note: Optional[str] = None
    options: Optional[dict] = None

class QuoteRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    date: str
    cart: List[CartItem]

# --- Endpoints ---

@app.post("/api/quotes")
async def submit_quote(quote: QuoteRequest):
    quote_id = str(uuid.uuid4())
    submitted_at = datetime.now().isoformat()
    cart_json = json.dumps([item.model_dump() for item in quote.cart])
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quotes (id, name, email, phone, date, cart, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (quote_id, quote.name, quote.email, quote.phone, quote.date, cart_json, submitted_at))
    conn.commit()
    conn.close()
        
    return {"message": "Quote request submitted successfully", "id": quote_id}


@app.get("/api/quotes")
async def get_quotes():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM quotes')
    rows = cursor.fetchall()
    conn.close()
    
    quotes = []
    for row in rows:
        quote = dict(row)
        try:
            quote["cart"] = json.loads(quote["cart"])
        except json.JSONDecodeError:
            quote["cart"] = []
        quotes.append(quote)
        
    return quotes
