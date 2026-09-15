from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import save_follow_up, log_agent_action
from tools.whatsapp_tool import send_whatsapp_message

# Initialize Follow Up Agent as FastAPI app
app = FastAPI(title="Follow Up Agent", version="1.0.0")


# Request model
class FollowUpTask(BaseModel):
    contact_id: str
    phone_number: str
    lead_score: int
    lead_status: str


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "online", "agent": "Follow Up Agent"}


@app.get("/agent-card")
async def agent_card():
    """Return agent identity"""
    return {
        "name": "Follow Up Agent",
        "description": "Schedules automatic follow ups based on lead score",
        "url": "http://localhost:8004",
        "version": "1.0.0",
        "skills": ["schedule_followup", "send_followup", "manage_reminders"]
    }


@app.post("/task")
async def process_task(task: FollowUpTask):
    """
    Main task handler:
    1. Check lead score to decide follow up timing
    2. Create follow up message based on status
    3. Schedule follow up in database
    4. Return result to pipeline
    """

    contact_id = task.contact_id
    phone_number = task.phone_number
    lead_score = task.lead_score
    lead_status = task.lead_status

    # Step 1: Decide follow up timing based on lead score
    if lead_score >= 71:
        # Hot lead — follow up in 2 hours
        follow_up_time = datetime.now() + timedelta(hours=2)
        follow_up_message = "Hi! Just checking in — are you ready to move forward? We have a special offer waiting for you! 🔥"
    elif lead_score >= 41:
        # Warm lead — follow up in 24 hours
        follow_up_time = datetime.now() + timedelta(hours=24)
        follow_up_message = "Hi! Hope you had time to think about our products. Any questions I can help with? 😊"
    else:
        # Cold lead — follow up in 3 days
        follow_up_time = datetime.now() + timedelta(days=3)
        follow_up_message = "Hi! We have some exciting new products you might be interested in. Would you like to know more?"

    print(f"[Follow Up Agent] Scheduling follow up for {phone_number} at {follow_up_time}")

    # Step 2: Save follow up to database
    save_follow_up(
        contact_id=contact_id,
        scheduled_at=follow_up_time.isoformat(),
        message=follow_up_message
    )

    # Step 3: Log agent action
    log_agent_action(
        agent_name="followup_agent",
        contact_id=contact_id,
        action="schedule_follow_up",
        result=f"Follow up scheduled at {follow_up_time} | Status: {lead_status}"
    )

    # Step 4: Return result to pipeline
    return {
        "success": True,
        "contact_id": contact_id,
        "phone_number": phone_number,
        "follow_up_scheduled_at": follow_up_time.isoformat(),
        "follow_up_message": follow_up_message,
        "lead_status": lead_status
    }