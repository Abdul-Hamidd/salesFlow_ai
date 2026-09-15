from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import process_whatsapp_message

from dotenv import load_dotenv
load_dotenv()

WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "hamzah@786")

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    """WhatsApp webhook verification"""
    params = dict(request.query_params)

    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        print("[Webhook] Webhook verified successfully!")
        return PlainTextResponse(content=challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


async def process_message_background(phone_number: str, message_text: str, name: str):
    """
    Runs the full pipeline (contact -> lead -> response -> followup ->
    notification) in the background so the webhook endpoint itself can
    return 200 OK to Meta immediately. This prevents Meta from retrying
    (and duplicating) the webhook when processing takes longer than a
    few seconds.
    """
    try:
        print(f"[Webhook] (background) Processing: {phone_number}: {message_text}")
        result = await process_whatsapp_message(
            phone_number=phone_number,
            message=message_text,
            name=name
        )
        print(f"[Webhook] (background) Done: {result}")
    except Exception as e:
        print(f"[Webhook] (background) Error: {str(e)}")


@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """Receive incoming WhatsApp messages including voice and image"""
    try:
        webhook_data = await request.json()
        print(f"[Webhook] Received data: {webhook_data}")

        entry = webhook_data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return {"status": "no message found"}

        message = messages[0]
        contact = value.get("contacts", [{}])[0]

        phone_number = message.get("from")
        name = contact.get("profile", {}).get("name", "Unknown")
        message_type = message.get("type", "text")

        print(f"[Webhook] Message type: {message_type} from {phone_number}")

        if message_type == "text":
            message_text = message.get("text", {}).get("body", "")

        elif message_type == "audio":
            print(f"[Webhook] 🎤 Voice message received!")
            from tools.voice_tool import process_voice_message

            media_id = message.get("audio", {}).get("id")
            if media_id:
                message_text = await process_voice_message(media_id)
                message_text = f"[Voice Message] {message_text}"
                print(f"[Webhook] Voice transcribed: {message_text}")
            else:
                message_text = "Voice message received but could not process"

        elif message_type == "image":
            print(f"[Webhook] 📷 Image received!")
            from tools.image_tool import process_image_message

            media_id = message.get("image", {}).get("id")
            if media_id:
                message_text = await process_image_message(media_id)
                print(f"[Webhook] Image analyzed: {message_text}")
            else:
                message_text = "[Image] Customer sent an image"

        elif message_type == "document":
            message_text = "[Document] Customer sent a document"

        elif message_type == "location":
            location = message.get("location", {})
            message_text = f"[Location] Lat: {location.get('latitude')}, Long: {location.get('longitude')}"

        else:
            message_text = f"[{message_type}] Unsupported message type"

        # KEY FIX: schedule the pipeline to run AFTER this response is sent,
        # instead of awaiting it here, so Meta gets 200 OK within milliseconds.
        background_tasks.add_task(
            process_message_background, phone_number, message_text, name
        )

        return {"status": "received"}

    except Exception as e:
        print(f"[Webhook] Error: {str(e)}")
        return {"status": "error", "message": str(e)}