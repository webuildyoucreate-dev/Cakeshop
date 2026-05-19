from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import os
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

QUOTES_FILE = "quotes.json"

# --- Data Models ---

class CartItem(BaseModel):
    name: str
    imageSrc: str
    note: Optional[str] = None
    option: Optional[str] = None

class QuoteRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    date: str
    cart: List[CartItem]

# --- Endpoints ---

@app.post("/api/quotes")
async def submit_quote(quote: QuoteRequest):
    # Prepare the quote record
    quote_data = quote.model_dump()
    quote_data["id"] = str(uuid.uuid4())
    quote_data["submitted_at"] = datetime.now().isoformat()
    
    quotes = []
    # Load existing quotes if file exists
    if os.path.exists(QUOTES_FILE):
        try:
            with open(QUOTES_FILE, "r") as f:
                quotes = json.load(f)
        except json.JSONDecodeError:
            pass # File might be empty or corrupted, we'll overwrite it
    
    # Add new quote
    quotes.append(quote_data)
    
    # Save back to file
    with open(QUOTES_FILE, "w") as f:
        json.dump(quotes, f, indent=4)
        
    return {"message": "Quote request submitted successfully", "id": quote_data["id"]}


@app.get("/api/quotes")
async def get_quotes():
    if os.path.exists(QUOTES_FILE):
        try:
            with open(QUOTES_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []
