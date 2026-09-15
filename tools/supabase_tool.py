from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)


def get_contact_by_phone(phone_number: str):
    """Check if contact already exists in database"""
    response = supabase.table("contacts").select("*").eq("phone_number", phone_number).execute()
    return response.data[0] if response.data else None


def create_contact(phone_number: str, name: str = None):
    """Save new contact to database"""
    response = supabase.table("contacts").insert({
        "phone_number": phone_number,
        "name": name
    }).execute()
    return response.data[0] if response.data else None


def save_conversation(contact_id: str, message: str, direction: str):
    """Save message to conversation history"""
    response = supabase.table("conversations").insert({
        "contact_id": contact_id,
        "message_text": message,
        "direction": direction
    }).execute()
    return response.data[0] if response.data else None


def save_lead(contact_id: str, score: int, status: str, notes: str = None):
    """Save lead score and status to database"""
    response = supabase.table("leads").insert({
        "contact_id": contact_id,
        "score": score,
        "status": status,
        "notes": notes
    }).execute()
    return response.data[0] if response.data else None


def get_products():
    """Get all active products from database"""
    response = supabase.table("products").select("*").eq("is_active", True).execute()
    return response.data if response.data else []


def save_follow_up(contact_id: str, scheduled_at: str, message: str):
    """Schedule a follow up for a contact"""
    response = supabase.table("follow_ups").insert({
        "contact_id": contact_id,
        "scheduled_at": scheduled_at,
        "message": message
    }).execute()
    return response.data[0] if response.data else None


def save_notification(title: str, message: str, type: str):
    """Save notification for business owner"""
    response = supabase.table("notifications").insert({
        "title": title,
        "message": message,
        "type": type
    }).execute()
    return response.data[0] if response.data else None


def log_agent_action(agent_name: str, contact_id: str, action: str, result: str):
    """Log every AI agent action for tracking"""
    response = supabase.table("agent_logs").insert({
        "agent_name": agent_name,
        "contact_id": contact_id,
        "action": action,
        "result": result
    }).execute()
    return response.data[0] if response.data else None