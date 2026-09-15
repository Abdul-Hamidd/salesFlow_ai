import httpx
import base64
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

client = Groq(api_key=GROQ_API_KEY)


async def download_image(media_id: str) -> str:
    """Download image from WhatsApp and convert to base64"""
    
    try:
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        
        async with httpx.AsyncClient(timeout=30.0) as http:
            # Get media URL
            response = await http.get(
                f"https://graph.facebook.com/v18.0/{media_id}",
                headers=headers
            )
            media_data = response.json()
            media_url = media_data.get("url")
            
            if not media_url:
                print(f"[Image Tool] Could not get URL: {media_data}")
                return None
            
            # Download image
            img_response = await http.get(media_url, headers=headers)
            
            # Convert to base64
            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
            print(f"[Image Tool] ✅ Image downloaded and converted to base64")
            return img_base64
            
    except Exception as e:
        print(f"[Image Tool] Error downloading image: {str(e)}")
        return None


def analyze_image_with_groq(image_base64: str, question: str = None) -> str:
    """Analyze image using Groq Vision API"""
    
    try:
        if not question:
            question = "What is in this image? Describe it in detail. If it's a product, mention the brand, model, and any relevant details."
        
        print(f"[Image Tool] Analyzing image with Groq...")
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        print(f"[Image Tool] ✅ Analysis: {result}")
        return result
        
    except Exception as e:
        print(f"[Image Tool] Error analyzing image: {str(e)}")
        return "Could not analyze image"


async def process_image_message(media_id: str) -> str:
    """Complete pipeline: Download → Analyze → Return description"""
    
    print(f"[Image Tool] Processing image: {media_id}")
    
    # Download image
    image_base64 = await download_image(media_id)
    
    if not image_base64:
        return "Customer sent an image but could not process it"
    
    # Analyze with Groq
    description = analyze_image_with_groq(image_base64)
    
    return f"[Image] {description}"