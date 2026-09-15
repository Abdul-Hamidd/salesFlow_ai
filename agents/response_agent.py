from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import get_products, save_conversation, log_agent_action
from tools.ollama_tool import generate_response
from tools.whatsapp_tool import send_whatsapp_message

# Initialize Response Agent as FastAPI app
app = FastAPI(title="Response Agent", version="1.0.0")


# Request model
class ResponseTask(BaseModel):
    contact_id: str
    phone_number: str
    message: str
    lead_score: int = 50


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "online", "agent": "Response Agent"}


@app.get("/agent-card")
async def agent_card():
    """Return agent identity"""
    return {
        "name": "Response Agent",
        "description": "Generates personalized WhatsApp reply using AI and product database",
        "url": "http://localhost:8003",
        "version": "1.0.0",
        "skills": ["generate_reply", "fetch_products", "send_message"]
    }


@app.post("/task")
async def process_task(task: ResponseTask):
    """
    Main task handler:
    1. Get products from database
    2. Generate AI response using Ollama
    3. Send reply via WhatsApp
    4. Save outbound message to conversation history
    5. Return result to pipeline
    """

    contact_id = task.contact_id
    phone_number = task.phone_number
    message = task.message
    lead_score = task.lead_score

    # Step 1: Get products from database
    print(f"[Response Agent] Fetching products...")
    products = get_products()

    # Step 2: Generate AI response using Ollama
    print(f"[Response Agent] Generating AI response...")
    ai_response = await generate_response(
        customer_message=message,
        products=products
    )
    print(f"[Response Agent] AI Response: {ai_response}") 

    # Step 3: Add urgency message for hot leads
    if lead_score >= 71:
        ai_response += "\n\n🔥 Special offer for you! Contact us now for exclusive deal!"

    # Step 4: Send reply via WhatsApp
    print(f"[Response Agent] Sending reply to {phone_number}...")
    await send_whatsapp_message(
        to=phone_number,
        message=ai_response
    )

    # Step 5: Save outbound message to conversation history
    save_conversation(contact_id, ai_response, "outbound")

    # Step 6: Log agent action
    log_agent_action(
        agent_name="response_agent",
        contact_id=contact_id,
        action="generate_and_send_response",
        result=f"Response sent to {phone_number} | Lead Score: {lead_score}"
    )

    # Step 7: Return result to pipeline
    return {
        "success": True,
        "contact_id": contact_id,
        "phone_number": phone_number,
        "response_sent": ai_response,
        "lead_score": lead_score
    }