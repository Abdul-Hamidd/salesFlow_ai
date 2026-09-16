import httpx
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# WhatsApp credentials
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# Groq hosted Whisper (replaces local openai-whisper — no PyTorch/CUDA needed,
# no heavy model to load into memory, avoids the OOM crash on deployment)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_WHISPER_MODEL = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo")


async def download_voice_message(media_id: str) -> str:
    """Download voice message from WhatsApp and save to temp file"""

    try:
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://graph.facebook.com/v18.0/{media_id}",
                headers=headers
            )
            media_data = response.json()
            media_url = media_data.get("url")

            if not media_url:
                print(f"[Voice Tool] Could not get media URL: {media_data}")
                return None

            audio_response = await client.get(media_url, headers=headers)

            with tempfile.NamedTemporaryFile(
                suffix=".ogg",
                delete=False,
                dir=tempfile.gettempdir()
            ) as tmp_file:
                tmp_file.write(audio_response.content)
                tmp_path = tmp_file.name

            print(f"[Voice Tool] Audio saved to: {tmp_path}")
            return tmp_path

    except Exception as e:
        print(f"[Voice Tool] Error downloading voice: {str(e)}")
        return None


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using Groq's hosted Whisper API"""

    try:
        print(f"[Voice Tool] Transcribing via Groq: {audio_path}")

        with open(audio_path, "rb") as audio_file:
            file_bytes = audio_file.read()

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": (os.path.basename(audio_path), file_bytes, "audio/ogg")},
                data={"model": GROQ_WHISPER_MODEL}
            )
            result = response.json()

        if "text" in result:
            transcript = result["text"].strip()
            print(f"[Voice Tool] ✅ Transcribed: {transcript}")
        else:
            print(f"[Voice Tool] ⚠️ Groq transcription error: {result}")
            transcript = None

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return transcript

    except Exception as e:
        print(f"[Voice Tool] Error transcribing: {str(e)}")
        return None


async def process_voice_message(media_id: str) -> str:
    """Complete pipeline: Download → Transcribe → Return text"""

    print(f"[Voice Tool] Processing voice message: {media_id}")

    audio_path = await download_voice_message(media_id)

    if not audio_path:
        return "Sorry, could not download voice message."

    transcript = await transcribe_audio(audio_path)

    if not transcript:
        return "Sorry, could not transcribe voice message."

    return transcript