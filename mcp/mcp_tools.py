import json
from typing import Any

# MCP Tool definitions for agents
# These are helper functions that agents use to call MCP tools

class MCPTools:
    """Helper class for agents to call MCP tools easily"""

    def __init__(self, mcp_client):
        self.client = mcp_client

    async def get_contact(self, phone_number: str) -> dict:
        """Get contact from database by phone number"""
        result = await self.client.call_tool("get_contact", {
            "phone_number": phone_number
        })
        return json.loads(result[0].text) if result else None

    async def save_contact(self, phone_number: str, name: str = None) -> dict:
        """Save new contact to database"""
        result = await self.client.call_tool("save_contact", {
            "phone_number": phone_number,
            "name": name
        })
        return json.loads(result[0].text) if result else None

    async def save_lead(self, contact_id: str, score: int, status: str, notes: str = None) -> dict:
        """Save lead score and status"""
        result = await self.client.call_tool("save_lead", {
            "contact_id": contact_id,
            "score": score,
            "status": status,
            "notes": notes
        })
        return json.loads(result[0].text) if result else None

    async def get_products(self) -> list:
        """Get all active products"""
        result = await self.client.call_tool("get_products", {})
        return json.loads(result[0].text) if result else []

    async def save_conversation(self, contact_id: str, message: str, direction: str) -> dict:
        """Save message to conversation history"""
        result = await self.client.call_tool("save_conversation", {
            "contact_id": contact_id,
            "message": message,
            "direction": direction
        })
        return json.loads(result[0].text) if result else None

    async def schedule_followup(self, contact_id: str, scheduled_at: str, message: str) -> dict:
        """Schedule follow up for customer"""
        result = await self.client.call_tool("schedule_followup", {
            "contact_id": contact_id,
            "scheduled_at": scheduled_at,
            "message": message
        })
        return json.loads(result[0].text) if result else None

    async def send_whatsapp(self, to: str, message: str) -> dict:
        """Send WhatsApp message to customer"""
        result = await self.client.call_tool("send_whatsapp", {
            "to": to,
            "message": message
        })
        return json.loads(result[0].text) if result else None

    async def analyze_lead(self, message: str) -> dict:
        """Analyze customer message and get lead score"""
        result = await self.client.call_tool("analyze_lead", {
            "message": message
        })
        return json.loads(result[0].text) if result else None

    async def generate_response(self, customer_message: str, products: list) -> str:
        """Generate AI response for customer"""
        result = await self.client.call_tool("generate_response", {
            "customer_message": customer_message,
            "products": products
        })
        return result[0].text if result else ""