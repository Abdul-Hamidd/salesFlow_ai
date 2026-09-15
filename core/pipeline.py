"""
Merged Agent Pipeline
======================
This replaces the 5 separate agent microservices (contact_agent, lead_agent,
response_agent, followup_agent, notification_agent) and the a2a HTTP client.
"""

from datetime import datetime, timedelta

from tools.supabase_tool import (
    get_contact_by_phone,
    create_contact,
    save_lead,
    save_follow_up,
    save_notification,
    save_conversation,
    get_products,
    log_agent_action,
    supabase,
)
from tools.ai_tool import analyze_sentiment, analyze_lead, generate_response
from tools.zoho_tool import (
    create_contact as zoho_create_contact,
    search_contact as zoho_search_contact,
    create_lead as zoho_create_lead,
    update_lead as zoho_update_lead,
    search_lead as zoho_search_lead,
    add_note as zoho_add_note,
)
from tools.whatsapp_tool import send_whatsapp_message


# ---------------------------------------------------------------------------
# Step 1: Contact
# ---------------------------------------------------------------------------
async def contact_step(phone_number: str, name: str, message: str) -> dict:
    existing_contact = get_contact_by_phone(phone_number)

    if existing_contact:
        contact_id = existing_contact["id"]
        is_new = False
        print(f"[Contact] Existing contact found: {contact_id}")
    else:
        new_contact = create_contact(phone_number, name)
        contact_id = new_contact["id"]
        is_new = True
        print(f"[Contact] New contact created: {contact_id}")

    # Sync to Zoho CRM (create-or-update, never duplicate)
    zoho_contact_id = None
    print(f"[Contact] Syncing to Zoho CRM...")
    try:
        zoho_search = await zoho_search_contact(phone_number)

        if not zoho_search.get("found"):
            zoho_result = await zoho_create_contact(name=name or "Unknown", phone=phone_number)
            if zoho_result.get("success"):
                zoho_contact_id = zoho_result.get("zoho_contact_id")
                print(f"[Contact] ✅ Zoho contact created: {zoho_contact_id}")
                await zoho_add_note(zoho_contact_id, f"WhatsApp Message: {message}")
            else:
                print(f"[Contact] ⚠️ Zoho sync failed: {zoho_result}")
        else:
            zoho_contact = zoho_search.get("contact", {})
            zoho_contact_id = zoho_contact.get("id")
            print(f"[Contact] ✅ Zoho contact already exists: {zoho_contact_id}")
            if zoho_contact_id:
                await zoho_add_note(zoho_contact_id, f"WhatsApp Message: {message}")
    except Exception as e:
        print(f"[Contact] ⚠️ Zoho error (non-critical): {str(e)}")

    # Sentiment
    print(f"[Contact] Analyzing sentiment...")
    sentiment_data = await analyze_sentiment(message)
    sentiment = sentiment_data.get("sentiment", "neutral")
    sentiment_emoji = sentiment_data.get("emoji", "😐")
    sentiment_score = sentiment_data.get("score", 50)
    print(f"[Contact] Sentiment: {sentiment} {sentiment_emoji} ({sentiment_score})")

    # Save inbound message
    supabase.table("conversations").insert({
        "contact_id": contact_id,
        "message_text": message,
        "direction": "inbound",
        "sentiment": sentiment,
        "sentiment_emoji": sentiment_emoji,
        "sentiment_score": sentiment_score
    }).execute()

    log_agent_action(
        agent_name="contact_agent",
        contact_id=contact_id,
        action="check_save_contact_zoho_sync",
        result=f"{'New' if is_new else 'Existing'} contact | Zoho synced | Sentiment: {sentiment} {sentiment_emoji}"
    )

    return {
        "contact_id": contact_id,
        "is_new_contact": is_new,
        "zoho_contact_id": zoho_contact_id,
        "sentiment": sentiment,
        "sentiment_emoji": sentiment_emoji,
        "sentiment_score": sentiment_score,
    }


# ---------------------------------------------------------------------------
# Step 2: Lead (FIXED — searches Zoho before creating, updates existing lead)
# ---------------------------------------------------------------------------
async def lead_step(contact_id: str, message: str, phone_number: str, name: str) -> dict:
    print(f"[Lead] Analyzing message: {message}")
    analysis = await analyze_lead(message)

    score = analysis.get("score", 50)
    status = analysis.get("status", "warm")
    reason = analysis.get("reason", "")
    print(f"[Lead] Score: {score} | Status: {status}")

    save_lead(contact_id=contact_id, score=score, status=status, notes=reason)

    print(f"[Lead] Syncing lead to Zoho CRM...")
    try:
        zoho_search = await zoho_search_lead(phone_number or "")

        if zoho_search.get("found"):
            existing_lead = zoho_search["lead"]
            zoho_lead_id = existing_lead.get("id")
            update_result = await zoho_update_lead(
                lead_id=zoho_lead_id,
                lead_score=score,
                lead_status=status,
                message=message
            )
            if update_result.get("success"):
                print(f"[Lead] ✅ Zoho lead updated (no duplicate): {zoho_lead_id}")
            else:
                print(f"[Lead] ⚠️ Zoho lead update failed: {update_result}")
        else:
            zoho_result = await zoho_create_lead(
                name=name or phone_number or "Unknown",
                phone=phone_number or "",
                lead_score=score,
                lead_status=status,
                message=message
            )
            if zoho_result.get("success"):
                print(f"[Lead] ✅ Zoho lead created: {zoho_result.get('zoho_lead_id')}")
            else:
                print(f"[Lead] ⚠️ Zoho lead sync failed: {zoho_result}")
    except Exception as e:
        print(f"[Lead] ⚠️ Zoho error (non-critical): {str(e)}")

    log_agent_action(
        agent_name="lead_agent",
        contact_id=contact_id,
        action="analyze_score_zoho_sync",
        result=f"Score: {score} | Status: {status} | Zoho synced | Reason: {reason}"
    )

    return {"score": score, "status": status, "reason": reason}


# ---------------------------------------------------------------------------
# Step 3: Response
# ---------------------------------------------------------------------------
async def response_step(contact_id: str, phone_number: str, message: str, lead_score: int) -> dict:
    print(f"[Response] Fetching products...")
    products = get_products()

    print(f"[Response] Generating AI response...")
    ai_response = await generate_response(customer_message=message, products=products)
    print(f"[Response] AI Response: {ai_response}")

    if lead_score >= 71:
        ai_response += "\n\n🔥 Special offer for you! Contact us now for exclusive deal!"

    print(f"[Response] Sending reply to {phone_number}...")
    await send_whatsapp_message(to=phone_number, message=ai_response)

    save_conversation(contact_id, ai_response, "outbound")

    log_agent_action(
        agent_name="response_agent",
        contact_id=contact_id,
        action="generate_and_send_response",
        result=f"Response sent to {phone_number} | Lead Score: {lead_score}"
    )

    return {"response_sent": ai_response}


# ---------------------------------------------------------------------------
# Step 4: Follow Up (FIXED — skips if a pending follow-up already exists)
# ---------------------------------------------------------------------------
async def followup_step(contact_id: str, phone_number: str, lead_score: int, lead_status: str) -> dict:
    existing = supabase.table("follow_ups").select("id").eq(
        "contact_id", contact_id
    ).eq("is_sent", False).execute()

    if existing.data and len(existing.data) > 0:
        print(f"[FollowUp] Pending follow-up already exists for {phone_number} — skipping duplicate")
        return {
            "follow_up_scheduled_at": None,
            "follow_up_message": None,
            "skipped": True,
        }

    if lead_score >= 71:
        follow_up_time = datetime.now() + timedelta(hours=2)
        follow_up_message = "Hi! Just checking in — are you ready to move forward? We have a special offer waiting for you! 🔥"
    elif lead_score >= 41:
        follow_up_time = datetime.now() + timedelta(hours=24)
        follow_up_message = "Hi! Hope you had time to think about our products. Any questions I can help with? 😊"
    else:
        follow_up_time = datetime.now() + timedelta(days=3)
        follow_up_message = "Hi! We have some exciting new products you might be interested in. Would you like to know more?"

    print(f"[FollowUp] Scheduling follow up for {phone_number} at {follow_up_time}")

    save_follow_up(
        contact_id=contact_id,
        scheduled_at=follow_up_time.isoformat(),
        message=follow_up_message
    )

    log_agent_action(
        agent_name="followup_agent",
        contact_id=contact_id,
        action="schedule_follow_up",
        result=f"Follow up scheduled at {follow_up_time} | Status: {lead_status}"
    )

    return {
        "follow_up_scheduled_at": follow_up_time.isoformat(),
        "follow_up_message": follow_up_message,
        "skipped": False,
    }


# ---------------------------------------------------------------------------
# Step 5: Notification
# ---------------------------------------------------------------------------
async def notification_step(contact_id: str, phone_number: str, lead_score: int, lead_status: str) -> dict:
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

    print(f"[Notification] Saving notification: {title}")

    save_notification(title=title, message=message, type=notification_type)

    log_agent_action(
        agent_name="notification_agent",
        contact_id=contact_id,
        action="send_owner_notification",
        result=f"Notification saved: {title}"
    )

    return {"notification_title": title, "notification_message": message}


# ---------------------------------------------------------------------------
# Full pipeline — same public interface as the old AgentPipeline class
# ---------------------------------------------------------------------------
async def process_whatsapp_message(phone_number: str, message: str, name: str = None) -> dict:
    print(f"[Pipeline] Processing message from {phone_number}")

    print("[Step 1] Running Contact step...")
    contact_result = await contact_step(phone_number, name, message)
    contact_id = contact_result["contact_id"]
    print(f"[Step 1] Contact ID: {contact_id}")

    print("[Step 2] Running Lead step...")
    lead_result = await lead_step(contact_id, message, phone_number, name)
    lead_score = lead_result.get("score", 50)
    lead_status = lead_result.get("status", "warm")
    print(f"[Step 2] Lead Score: {lead_score} | Status: {lead_status}")

    print("[Step 3] Running Response step...")
    await response_step(contact_id, phone_number, message, lead_score)
    print(f"[Step 3] Response sent to {phone_number}")

    print("[Step 4] Running Follow Up step...")
    await followup_step(contact_id, phone_number, lead_score, lead_status)
    print(f"[Step 4] Follow up handled")

    print("[Step 5] Running Notification step...")
    await notification_step(contact_id, phone_number, lead_score, lead_status)
    print(f"[Step 5] Owner notified")

    return {
        "success": True,
        "contact_id": contact_id,
        "lead_score": lead_score,
        "lead_status": lead_status,
        "message": "Pipeline completed successfully"
    }