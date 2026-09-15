from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio
import json

# Initialize MCP Server
app = Server("whatsapp-crm-mcp")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available MCP tools"""
    return [
        types.Tool(
            name="get_contact",
            description="Get contact information by phone number",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Customer phone number"
                    }
                },
                "required": ["phone_number"]
            }
        ),
        types.Tool(
            name="save_contact",
            description="Save new contact to database",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string"},
                    "name": {"type": "string"}
                },
                "required": ["phone_number"]
            }
        ),
        types.Tool(
            name="save_lead",
            description="Save lead score and status",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string"},
                    "score": {"type": "integer"},
                    "status": {"type": "string"},
                    "notes": {"type": "string"}
                },
                "required": ["contact_id", "score", "status"]
            }
        ),
        types.Tool(
            name="get_products",
            description="Get all active products from database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="save_conversation",
            description="Save message to conversation history",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string"},
                    "message": {"type": "string"},
                    "direction": {"type": "string"}
                },
                "required": ["contact_id", "message", "direction"]
            }
        ),
        types.Tool(
            name="schedule_followup",
            description="Schedule a follow up for customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string"},
                    "scheduled_at": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["contact_id", "scheduled_at", "message"]
            }
        ),
        types.Tool(
            name="send_whatsapp",
            description="Send WhatsApp message to customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["to", "message"]
            }
        ),
        types.Tool(
            name="analyze_lead",
            description="Analyze customer message and get lead score using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="generate_response",
            description="Generate AI response for customer message",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_message": {"type": "string"},
                    "products": {"type": "array"}
                },
                "required": ["customer_message", "products"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Execute MCP tool when called by agent"""

    from tools.supabase_tool import (
        get_contact_by_phone, create_contact,
        save_conversation, save_lead,
        get_products, save_follow_up
    )
    from tools.whatsapp_tool import send_whatsapp_message
    from tools.ollama_tool import analyze_lead, generate_response

    # Get contact by phone number
    if name == "get_contact":
        result = get_contact_by_phone(arguments["phone_number"])
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Save new contact
    elif name == "save_contact":
        result = create_contact(
            arguments["phone_number"],
            arguments.get("name")
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Save lead score
    elif name == "save_lead":
        result = save_lead(
            arguments["contact_id"],
            arguments["score"],
            arguments["status"],
            arguments.get("notes")
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Get all products
    elif name == "get_products":
        result = get_products()
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Save conversation
    elif name == "save_conversation":
        result = save_conversation(
            arguments["contact_id"],
            arguments["message"],
            arguments["direction"]
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Schedule follow up
    elif name == "schedule_followup":
        result = save_follow_up(
            arguments["contact_id"],
            arguments["scheduled_at"],
            arguments["message"]
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Send WhatsApp message
    elif name == "send_whatsapp":
        result = await send_whatsapp_message(
            arguments["to"],
            arguments["message"]
        )
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Analyze lead with AI
    elif name == "analyze_lead":
        result = await analyze_lead(arguments["message"])
        return [types.TextContent(type="text", text=json.dumps(result))]

    # Generate AI response
    elif name == "generate_response":
        result = await generate_response(
            arguments["customer_message"],
            arguments["products"]
        )
        return [types.TextContent(type="text", text=result)]


async def main():
    """Start MCP Server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())