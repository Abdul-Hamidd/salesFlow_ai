from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import (
    get_contact_by_phone,
    create_contact,
    log_agent_action
)
from tools.ollama_tool import analyze_sentiment
from tools.zoho_tool import create_contact as zoho_create_contact, search_contact as zoho_search_contact, add_note as zoho_add_note

# Initialize Contact Agent as FastAPI app
app = FastAPI(title="Contact Agent", version="1.0.0")


# Request model
class ContactTask(BaseModel):
    phone_number: str
    name: str = None
    message: str


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "online", "agent": "Contact Agent"}


@app.get("/agent-card")
async def agent_card():
    """Return agent identity"""
    return {
        "name": "Contact Agent",
        "description": "Checks if customer exists, creates new contact in Supabase + Zoho CRM",
        "url": "http://localhost:8001",
        "version": "1.0.0",
        "skills": ["check_contact", "create_contact", "zoho_sync", "analyze_sentiment"]
    }


@app.post("/task")
async def process_task(task: ContactTask):
    """
    Main task handler:
    1. Check if contact exists in Supabase
    2. Create new contact if not found
    3. Sync contact to Zoho CRM
    4. Analyze sentiment of message
    5. Save incoming message to conversation history
    6. Return contact ID for next agent
    """

    phone_number = task.phone_number
    name = task.name
    message = task.message

    # Step 1: Check if contact already exists in Supabase
    existing_contact = get_contact_by_phone(phone_number)

    if existing_contact:
        contact_id = existing_contact["id"]
        is_new = False
        print(f"[Contact Agent] Existing contact found: {contact_id}")
    else:
        # Step 2: Create new contact in Supabase
        new_contact = create_contact(phone_number, name)
        contact_id = new_contact["id"]
        is_new = True
        print(f"[Contact Agent] New contact created: {contact_id}")

    # Step 3: Sync to Zoho CRM
    print(f"[Contact Agent] Syncing to Zoho CRM...")
    try:
        # Check if contact exists in Zoho
        zoho_search = await zoho_search_contact(phone_number)
        
        if not zoho_search.get("found"):
            # Create in Zoho
            zoho_result = await zoho_create_contact(
                name=name or "Unknown",
                phone=phone_number
            )
            if zoho_result.get("success"):
                zoho_contact_id = zoho_result.get("zoho_contact_id")
                print(f"[Contact Agent] ✅ Zoho contact created: {zoho_contact_id}")
                
                # Add message as note in Zoho
                await zoho_add_note(zoho_contact_id, f"WhatsApp Message: {message}")
            else:
                print(f"[Contact Agent] ⚠️ Zoho sync failed: {zoho_result}")
        else:
            zoho_contact = zoho_search.get("contact", {})
            zoho_contact_id = zoho_contact.get("id")
            print(f"[Contact Agent] ✅ Zoho contact already exists: {zoho_contact_id}")
            
            # Add message as note
            if zoho_contact_id:
                await zoho_add_note(zoho_contact_id, f"WhatsApp Message: {message}")
                
    except Exception as e:
        print(f"[Contact Agent] ⚠️ Zoho error (non-critical): {str(e)}")

    # Step 4: Analyze sentiment
    print(f"[Contact Agent] Analyzing sentiment...")
    sentiment_data = await analyze_sentiment(message)
    sentiment = sentiment_data.get("sentiment", "neutral")
    sentiment_emoji = sentiment_data.get("emoji", "😐")
    sentiment_score = sentiment_data.get("score", 50)
    print(f"[Contact Agent] Sentiment: {sentiment} {sentiment_emoji} ({sentiment_score})")

    # Step 5: Save incoming message with sentiment
    from tools.supabase_tool import supabase
    supabase.table("conversations").insert({
        "contact_id": contact_id,
        "message_text": message,
        "direction": "inbound",
        "sentiment": sentiment,
        "sentiment_emoji": sentiment_emoji,
        "sentiment_score": sentiment_score
    }).execute()

    # Step 6: Log agent action
    log_agent_action(
        agent_name="contact_agent",
        contact_id=contact_id,
        action="check_save_contact_zoho_sync",
        result=f"{'New' if is_new else 'Existing'} contact | Zoho synced | Sentiment: {sentiment} {sentiment_emoji}"
    )

    # Step 7: Return result to pipeline
    return {
        "success": True,
        "contact_id": contact_id,
        "is_new_contact": is_new,
        "phone_number": phone_number,
        "name": name,
        "sentiment": sentiment,
        "sentiment_emoji": sentiment_emoji,
        "sentiment_score": sentiment_score
    }