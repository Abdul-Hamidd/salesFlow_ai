from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import save_notification, log_agent_action

# Initialize Notification Agent as FastAPI app
app = FastAPI(title="Notification Agent", version="1.0.0")


# Request model
class NotificationTask(BaseModel):
    contact_id: str
    phone_number: str
    lead_score: int
    lead_status: str


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "online", "agent": "Notification Agent"}


@app.get("/agent-card")
async def agent_card():
    """Return agent identity"""
    return {
        "name": "Notification Agent",
        "description": "Sends alerts and daily reports to business owner",
        "url": "http://localhost:8005",
        "version": "1.0.0",
        "skills": ["send_alert", "generate_report", "update_dashboard"]
    }


@app.post("/task")
async def process_task(task: NotificationTask):
    """
    Main task handler:
    1. Check lead status
    2. Create appropriate notification
    3. Save notification to database
    4. Return result to pipeline
    """

    contact_id = task.contact_id
    phone_number = task.phone_number
    lead_score = task.lead_score
    lead_status = task.lead_status

    # Step 1: Create notification based on lead status
    if lead_status == "hot":
        title = "🔥 Hot Lead Alert!"
        message = f"New hot lead from {phone_number} with score {lead_score}/100 — Take action now!"
        notification_type = "hot_lead"

    elif lead_status == "warm":
        title = "⚡ New Warm Lead"
        message = f"New warm lead from {phone_number} with score {lead_score}/100"
        notification_type = "new_lead"

    else:
        title = "📩 New Message Received"
        message = f"New message from {phone_number} with score {lead_score}/100"
        notification_type = "new_lead"

    print(f"[Notification Agent] Saving notification: {title}")

    # Step 2: Save notification to database
    save_notification(
        title=title,
        message=message,
        type=notification_type
    )

    # Step 3: Log agent action
    log_agent_action(
        agent_name="notification_agent",
        contact_id=contact_id,
        action="send_owner_notification",
        result=f"Notification saved: {title}"
    )

    # Step 4: Return result to pipeline
    return {
        "success": True,
        "contact_id": contact_id,
        "notification_title": title,
        "notification_message": message,
        "notification_type": notification_type
    }