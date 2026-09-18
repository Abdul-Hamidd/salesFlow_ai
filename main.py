from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Import routers
from webhooks.whatsapp_webhook import router as webhook_router
from routes.dashboard_routes import router as dashboard_router

# Import scheduler
from scheduler import start_scheduler, stop_scheduler

# Initialize FastAPI application
app = FastAPI(title="WhatsApp AI CRM", version="2.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://sales-flow-ai-mu.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(webhook_router)
app.include_router(dashboard_router)


# Start scheduler when app starts
@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print("[Main] ✅ WhatsApp AI CRM Started! (single-service architecture)")


# Stop scheduler when app stops
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()
    print("[Main] Shutting down...")


# Root endpoint
@app.get("/")
def root():
    return {"message": "WhatsApp AI CRM Backend Running! ✅"}


# Simple health/status endpoint.
# The 5 old agents are no longer separate services — they're plain
# functions inside core/pipeline.py, running in this same process.
@app.get("/agents/status")
async def agents_status():
    """Confirm the pipeline module loaded correctly (replaces old per-agent HTTP health checks)"""
    try:
        from core import pipeline  # noqa: F401
        return {
            "status": "ok",
            "architecture": "merged-single-service",
            "steps": ["contact", "lead", "response", "followup", "notification"],
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# Follow ups status endpoint
@app.get("/followups/pending")
async def get_pending_followups():
    """Get all pending follow ups"""
    from tools.supabase_tool import supabase
    from datetime import datetime

    now = datetime.now().isoformat()
    response = supabase.table("follow_ups").select(
        "*, contacts(phone_number, name)"
    ).eq("is_sent", False).execute()

    return {
        "pending_count": len(response.data),
        "follow_ups": response.data
    }