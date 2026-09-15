import whisper
import httpx
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

# WhatsApp credentials
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# Load Whisper model (small = accurate)
print("[Voice Tool] Loading Whisper model...")
whisper_model = whisper.load_model("small")
print("[Voice Tool] ✅ Whisper model loaded!")


async def download_voice_message(media_id: str) -> str:
    """Download voice message from WhatsApp and save to temp file"""
    
    try:
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        # Step 1: Get media URL
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
            
            # Step 2: Download audio file
            audio_response = await client.get(media_url, headers=headers)
            
            # Step 3: Save to temp file
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


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using Whisper"""
    
    try:
        print(f"[Voice Tool] Transcribing: {audio_path}")
        
        # Transcribe with Whisper
        result = whisper_model.transcribe(
            audio_path,
            language=None,  # Auto detect language
            fp16=False       # Use CPU
        )
        
        transcript = result["text"].strip()
        print(f"[Voice Tool] ✅ Transcribed: {transcript}")
        
        # Clean up temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return transcript
        
    except Exception as e:
        print(f"[Voice Tool] Error transcribing: {str(e)}")
        return None


async def process_voice_message(media_id: str) -> str:
    """Complete pipeline: Download → Transcribe → Return text"""
    
    print(f"[Voice Tool] Processing voice message: {media_id}")
    
    # Download audio
    audio_path = await download_voice_message(media_id)
    
    if not audio_path:
        return "Sorry, could not download voice message."
    
    # Transcribe audio
    transcript = transcribe_audio(audio_path)
    
    if not transcript:
        return "Sorry, could not transcribe voice message."
    
    return transcript