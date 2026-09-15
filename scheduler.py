from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.supabase_tool import supabase
from tools.whatsapp_tool import send_whatsapp_message

# Initialize scheduler
scheduler = AsyncIOScheduler()


async def send_pending_followups():
    """Check and send all pending follow ups"""
    
    print(f"[Scheduler] Checking pending follow ups... {datetime.now()}")
    
    try:
        # Get all pending follow ups that are due
        now = datetime.now().isoformat()
        
        response = supabase.table("follow_ups").select(
            "*, contacts(phone_number, name)"
        ).eq("is_sent", False).lte("scheduled_at", now).execute()
        
        pending = response.data
        print(f"[Scheduler] Found {len(pending)} pending follow ups")
        
        for followup in pending:
            try:
                phone_number = followup["contacts"]["phone_number"]
                name = followup["contacts"]["name"] or "Customer"
                message = followup["message"]
                followup_id = followup["id"]
                contact_id = followup["contact_id"]
                
                print(f"[Scheduler] Sending follow up to {phone_number}...")
                
                # Send WhatsApp message
                result = await send_whatsapp_message(phone_number, message)
                
                # Mark as sent
                supabase.table("follow_ups").update({
                    "is_sent": True
                }).eq("id", followup_id).execute()
                
                # Save to conversations
                supabase.table("conversations").insert({
                    "contact_id": contact_id,
                    "message_text": f"[Auto Follow Up] {message}",
                    "direction": "outbound"
                }).execute()
                
                # Save notification
                supabase.table("notifications").insert({
                    "title": "📨 Follow Up Sent!",
                    "message": f"Auto follow up sent to {name} ({phone_number})",
                    "type": "follow_up"
                }).execute()
                
                print(f"[Scheduler] ✅ Follow up sent to {phone_number}")
                
            except Exception as e:
                print(f"[Scheduler] ❌ Error sending follow up: {str(e)}")
                
    except Exception as e:
        print(f"[Scheduler] ❌ Error checking follow ups: {str(e)}")


def start_scheduler():
    """Start the background scheduler"""
    
    # Check every 1 minute for pending follow ups
    scheduler.add_job(
        send_pending_followups,
        trigger=IntervalTrigger(minutes=1),
        id="followup_checker",
        name="Follow Up Checker",
        replace_existing=True
    )
    
    scheduler.start()
    print("[Scheduler] ✅ Auto Follow Up Scheduler started!")
    print("[Scheduler] Checking every 1 minute for pending follow ups...")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    print("[Scheduler] Stopped!")