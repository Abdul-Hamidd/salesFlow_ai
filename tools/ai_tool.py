import httpx
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq configuration (replaces Ollama for production — no local model server needed)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


async def ask_ai(prompt: str, system_prompt: str = None) -> str:
    """Send a prompt to Groq and get AI response (drop-in replacement for ask_ollama)"""

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": messages,
                    "temperature": 0.7
                }
            )

            result = response.json()
            print(f"[Groq] Raw response: {result}")

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            elif "error" in result:
                print(f"[Groq] Error: {result['error']}")
                return "Sorry, I could not generate a response right now."
            else:
                return "Sorry, unexpected response from AI."

    except httpx.TimeoutException:
        print("[Groq] Timeout! Model taking too long.")
        return "Sorry, AI response timed out. Please try again."
    except Exception as e:
        print(f"[Groq] Exception: {str(e)}")
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

    response = await ask_ai(message, system_prompt)
    print(f"[Groq] Lead analysis response: {response}")

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
        print(f"[Groq] JSON parse error: {e}")
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

    return await ask_ai(customer_message, system_prompt)


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

    response = await ask_ai(message, system_prompt)
    print(f"[Groq] Sentiment response: {response}")

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
        print(f"[Groq] Sentiment parse error: {e}")
        return {"sentiment": "neutral", "emoji": "😐", "score": 50, "reason": "Could not analyze"}