from fastapi import APIRouter
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.supabase_tool import supabase

# Initialize router
router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get main dashboard statistics for business owner"""

    contacts = supabase.table("contacts").select("*", count="exact").execute()
    total_contacts = contacts.count

    hot_leads = supabase.table("leads").select("*", count="exact").eq("status", "hot").execute()
    warm_leads = supabase.table("leads").select("*", count="exact").eq("status", "warm").execute()
    cold_leads = supabase.table("leads").select("*", count="exact").eq("status", "cold").execute()

    orders = supabase.table("orders").select("*", count="exact").execute()
    total_orders = orders.count

    revenue_data = supabase.table("orders").select("total_price").eq("status", "delivered").execute()
    total_revenue = sum([r["total_price"] or 0 for r in revenue_data.data])

    notifications = supabase.table("notifications").select("*", count="exact").eq("is_read", False).execute()
    unread_notifications = notifications.count

    return {
        "total_contacts": total_contacts,
        "leads": {
            "hot": hot_leads.count,
            "warm": warm_leads.count,
            "cold": cold_leads.count
        },
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "unread_notifications": unread_notifications
    }


@router.get("/dashboard/contacts")
async def get_contacts():
    """Get all contacts with their lead scores"""

    response = supabase.table("contacts").select(
        "*, leads(score, status)"
    ).order("created_at", desc=True).execute()

    return {"contacts": response.data}


@router.get("/dashboard/leads")
async def get_leads():
    """Get all leads with contact information"""

    response = supabase.table("leads").select(
        "*, contacts(name, phone_number)"
    ).order("score", desc=True).execute()

    return {"leads": response.data}


@router.get("/dashboard/notifications")
async def get_notifications():
    """Get all unread notifications for business owner"""

    response = supabase.table("notifications").select("*").eq(
        "is_read", False
    ).order("created_at", desc=True).execute()

    return {"notifications": response.data}


@router.put("/dashboard/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""

    supabase.table("notifications").update(
        {"is_read": True}
    ).eq("id", notification_id).execute()

    return {"success": True, "message": "Notification marked as read"}


@router.get("/dashboard/conversations/{contact_id}")
async def get_conversations(contact_id: str):
    """Get conversation history for a specific contact"""

    response = supabase.table("conversations").select("*").eq(
        "contact_id", contact_id
    ).order("created_at", desc=True).execute()

    return {"conversations": response.data}


@router.get("/dashboard/orders")
async def get_orders():
    """Get all orders with contact and product information"""

    response = supabase.table("orders").select(
        "*, contacts(name, phone_number), products(name, price)"
    ).order("created_at", desc=True).execute()

    return {"orders": response.data}


@router.post("/dashboard/send-message")
async def send_message(request: dict):
    """Send manual message to customer from dashboard"""
    from tools.whatsapp_tool import send_whatsapp_message
    from tools.supabase_tool import save_conversation

    phone_number = request.get("phone_number")
    message = request.get("message")
    contact_id = request.get("contact_id")

    result = await send_whatsapp_message(phone_number, message)
    save_conversation(contact_id, message, "outbound")

    return {"success": True, "result": result}


@router.get("/dashboard/generate-report")
async def generate_report():
    """Generate daily PDF report"""
    from report_generator import generate_pdf_report
    from datetime import date

    try:
        file_path = generate_pdf_report(date.today())
        if file_path:
            return {"success": True, "file_path": file_path, "message": "Report generated successfully!"}
        else:
            return {"success": False, "message": "Could not generate report"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/dashboard/download-report")
async def download_report():
    """Download the latest PDF report"""
    from fastapi.responses import FileResponse
    from report_generator import generate_pdf_report
    from datetime import date
    import os

    try:
        file_path = generate_pdf_report(date.today())
        if file_path and os.path.exists(file_path):
            return FileResponse(
                path=file_path,
                filename=f"CRM_Report_{date.today().isoformat()}.pdf",
                media_type="application/pdf"
            )
        else:
            return {"success": False, "message": "Report not found"}
    except Exception as e:
        return {"success": False, "message": str(e)}