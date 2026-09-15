from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import save_lead, log_agent_action
from tools.ollama_tool import analyze_lead
from tools.zoho_tool import create_lead as zoho_create_lead

# Initialize Lead Agent as FastAPI app
app = FastAPI(title="Lead Agent", version="1.0.0")


# Request model
class LeadTask(BaseModel):
    contact_id: str
    message: str
    phone_number: str = None
    name: str = None


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "online", "agent": "Lead Agent"}


@app.get("/agent-card")
async def agent_card():
    """Return agent identity"""
    return {
        "name": "Lead Agent",
        "description": "Analyzes customer message, assigns lead score, syncs to Zoho CRM",
        "url": "http://localhost:8002",
        "version": "1.0.0",
        "skills": ["analyze_message", "score_lead", "classify_lead", "zoho_sync"]
    }


@app.post("/task")
async def process_task(task: LeadTask):
    """
    Main task handler:
    1. Analyze message with Ollama AI
    2. Get lead score and status
    3. Save to Supabase
    4. Sync lead to Zoho CRM
    5. Return score to pipeline
    """

    contact_id = task.contact_id
    message = task.message
    phone_number = task.phone_number
    name = task.name

    # Step 1: Analyze message with Ollama AI
    print(f"[Lead Agent] Analyzing message: {message}")
    analysis = await analyze_lead(message)

    score = analysis.get("score", 50)
    status = analysis.get("status", "warm")
    reason = analysis.get("reason", "")

    print(f"[Lead Agent] Score: {score} | Status: {status}")

    # Step 2: Save lead to Supabase
    save_lead(
        contact_id=contact_id,
        score=score,
        status=status,
        notes=reason
    )

    # Step 3: Sync to Zoho CRM
    print(f"[Lead Agent] Syncing lead to Zoho CRM...")
    try:
        zoho_result = await zoho_create_lead(
            name=name or phone_number or "Unknown",
            phone=phone_number or "",
            lead_score=score,
            lead_status=status,
            message=message
        )
        if zoho_result.get("success"):
            print(f"[Lead Agent] ✅ Zoho lead created: {zoho_result.get('zoho_lead_id')}")
        else:
            print(f"[Lead Agent] ⚠️ Zoho lead sync failed: {zoho_result}")
    except Exception as e:
        print(f"[Lead Agent] ⚠️ Zoho error (non-critical): {str(e)}")

    # Step 4: Log agent action
    log_agent_action(
        agent_name="lead_agent",
        contact_id=contact_id,
        action="analyze_score_zoho_sync",
        result=f"Score: {score} | Status: {status} | Zoho synced | Reason: {reason}"
    )

    # Step 5: Return result to pipeline
    return {
        "success": True,
        "contact_id": contact_id,
        "score": score,
        "status": status,
        "reason": reason
    }