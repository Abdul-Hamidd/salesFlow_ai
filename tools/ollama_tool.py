import httpx
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud")


async def ask_ollama(prompt: str, system_prompt: str = None) -> str:
    """Send a prompt to Ollama and get AI response"""
    
    messages = []
    
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    messages.append({
        "role": "user",
        "content": prompt
    })
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False
                }
            )
            
            result = response.json()
            print(f"[Ollama] Raw response: {result}")
            
            if "message" in result:
                return result["message"]["content"]
            elif "error" in result:
                print(f"[Ollama] Error: {result['error']}")
                return "Sorry, I could not generate a response right now."
            else:
                return "Sorry, unexpected response from AI."
                
    except httpx.TimeoutException:
        print("[Ollama] Timeout! Model taking too long.")
        return "Sorry, AI response timed out. Please try again."
    except Exception as e:
        print(f"[Ollama] Exception: {str(e)}")
        return "Sorry, AI is not available right now."


async def analyze_lead(message: str, history: list = []) -> dict:
    """Analyze customer message and return lead score"""
    
    system_prompt = """You are a CRM lead analysis expert.
    Analyze the customer message and return ONLY a JSON response like this:
    {
        "score": 85,
        "status": "hot",
        "reason": "Customer is asking about pricing and ready to buy"
    }
    Score rules:
    - 0-40: cold lead
    - 41-70: warm lead  
    - 71-100: hot lead
    Return ONLY valid JSON, nothing else.
    """
    
    response = await ask_ollama(message, system_prompt)
    print(f"[Ollama] Lead analysis response: {response}")
    
    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1].replace("json", "").strip()
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end != 0:
            clean = clean[start:end]
        return json.loads(clean)
    except Exception as e:
        print(f"[Ollama] JSON parse error: {e}")
        return {"score": 50, "status": "warm", "reason": "Could not analyze"}


async def generate_response(customer_message: str, products: list, history: list = []) -> str:
    """Generate personalized response for customer"""
    
    products_text = "\n".join([
        f"- {p['name']}: {p['description']} (Price: Rs. {p['price']})"
        for p in products
    ]) if products else "No products available"
    
    system_prompt = f"""You are a helpful WhatsApp sales assistant.
    
    Available products:
    {products_text}
    
    Rules:
    - Be friendly and professional
    - Keep responses short (max 3-4 lines)
    - If customer asks about a product, provide details
    - If customer wants to buy, ask for their details
    - Always respond in the same language as customer
    """
    
    return await ask_ollama(customer_message, system_prompt)


async def analyze_sentiment(message: str) -> dict:
    """Analyze customer message sentiment"""
    
    system_prompt = """You are a sentiment analysis expert.
    Analyze the customer message and return ONLY a JSON response like this:
    {
        "sentiment": "positive",
        "emoji": "😊",
        "score": 85,
        "reason": "Customer is happy and interested"
    }
    Sentiment options: positive, neutral, negative, urgent
    Score: 0-100 (100 = most positive)
    Return ONLY valid JSON, nothing else.
    """
    
    response = await ask_ollama(message, system_prompt)
    print(f"[Ollama] Sentiment response: {response}")
    
    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1].replace("json", "").strip()
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start != -1 and end != 0:
            clean = clean[start:end]
        return json.loads(clean)
    except Exception as e:
        print(f"[Ollama] Sentiment parse error: {e}")
        return {"sentiment": "neutral", "emoji": "😐", "score": 50, "reason": "Could not analyze"}