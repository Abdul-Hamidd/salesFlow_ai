import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WhatsApp Business API configuration
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
BASE_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


async def send_whatsapp_message(to: str, message: str) -> dict:
    """Send a text message via WhatsApp Business API"""
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=payload, headers=headers)
        return response.json()


async def send_template_message(to: str, template_name: str) -> dict:
    """Send a WhatsApp template message"""
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": "en_US"
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(BASE_URL, json=payload, headers=headers)
        return response.json()


def extract_message_data(webhook_data: dict) -> dict:
    """Extract message details from WhatsApp webhook payload"""
    
    try:
        entry = webhook_data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        # Extract message info
        message = value["messages"][0]
        contact = value["contacts"][0]
        
        return {
            "phone_number": message["from"],
            "name": contact["profile"]["name"],
            "message": message["text"]["body"],
            "message_id": message["id"],
            "timestamp": message["timestamp"]
        }
    except Exception as e:
        return None