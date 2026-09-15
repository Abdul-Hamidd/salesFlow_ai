import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Zoho CRM configuration
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_API_DOMAIN = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")

# Current token (will be refreshed automatically)
current_token = ZOHO_ACCESS_TOKEN


async def refresh_access_token() -> str:
    """Refresh Zoho access token when expired"""
    global current_token

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.zoho.com/oauth/v2/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": ZOHO_CLIENT_ID,
                    "client_secret": ZOHO_CLIENT_SECRET,
                    "refresh_token": ZOHO_REFRESH_TOKEN
                }
            )
            data = response.json()

            if "access_token" in data:
                current_token = data["access_token"]
                print(f"[Zoho] ✅ Token refreshed!")
                return current_token
            else:
                print(f"[Zoho] ❌ Token refresh failed: {data}")
                return None

    except Exception as e:
        print(f"[Zoho] Error refreshing token: {str(e)}")
        return None


async def get_headers() -> dict:
    """Get authorization headers"""
    return {
        "Authorization": f"Zoho-oauthtoken {current_token}",
        "Content-Type": "application/json"
    }


async def create_contact(name: str, phone: str, email: str = None) -> dict:
    """Create a new contact in Zoho CRM"""

    try:
        print(f"[Zoho] Connecting to: {ZOHO_API_DOMAIN}")
        headers = await get_headers()

        data = {
            "data": [{
                "Last_Name": name or phone,
                "First_Name": "",
                "Phone": phone,
                "Email": email or "",
                "Lead_Source": "WhatsApp"
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ZOHO_API_DOMAIN}/crm/v2/Contacts",
                json=data,
                headers=headers
            )

            result = response.json()

            if response.status_code == 401:
                print("[Zoho] Token expired, refreshing...")
                await refresh_access_token()
                headers = await get_headers()
                response = await client.post(
                    f"{ZOHO_API_DOMAIN}/crm/v2/Contacts",
                    json=data,
                    headers=headers
                )
                result = response.json()

            if result.get("data"):
                contact_id = result["data"][0]["details"]["id"]
                print(f"[Zoho] ✅ Contact created: {contact_id}")
                return {"success": True, "zoho_contact_id": contact_id}
            else:
                print(f"[Zoho] ❌ Contact creation failed: {result}")
                return {"success": False, "error": str(result)}

    except Exception as e:
        print(f"[Zoho] Error creating contact: {str(e)}")
        return {"success": False, "error": str(e)}


async def create_lead(name: str, phone: str, lead_score: int, lead_status: str, message: str = None) -> dict:
    """Create a new lead in Zoho CRM"""

    try:
        headers = await get_headers()

        zoho_status_map = {
            "hot": "Hot",
            "warm": "Warm",
            "cold": "Cold"
        }

        data = {
            "data": [{
                "Last_Name": name or phone,
                "Phone": phone,
                "Lead_Source": "WhatsApp",
                "Lead_Status": zoho_status_map.get(lead_status, "New"),
                "Rating": "Hot" if lead_score >= 71 else "Warm" if lead_score >= 41 else "Cold",
                "Description": f"WhatsApp Lead | Score: {lead_score}/100 | Message: {message or 'N/A'}"
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ZOHO_API_DOMAIN}/crm/v2/Leads",
                json=data,
                headers=headers
            )

            result = response.json()

            if response.status_code == 401:
                await refresh_access_token()
                headers = await get_headers()
                response = await client.post(
                    f"{ZOHO_API_DOMAIN}/crm/v2/Leads",
                    json=data,
                    headers=headers
                )
                result = response.json()

            if result.get("data"):
                lead_id = result["data"][0]["details"]["id"]
                print(f"[Zoho] ✅ Lead created: {lead_id}")
                return {"success": True, "zoho_lead_id": lead_id}
            else:
                print(f"[Zoho] ❌ Lead creation failed: {result}")
                return {"success": False, "error": str(result)}

    except Exception as e:
        print(f"[Zoho] Error creating lead: {str(e)}")
        return {"success": False, "error": str(e)}


async def update_lead(lead_id: str, lead_score: int, lead_status: str, message: str = None) -> dict:
    """Update an existing lead in Zoho CRM instead of creating a duplicate"""

    try:
        headers = await get_headers()

        zoho_status_map = {
            "hot": "Hot",
            "warm": "Warm",
            "cold": "Cold"
        }

        data = {
            "data": [{
                "id": lead_id,
                "Lead_Status": zoho_status_map.get(lead_status, "New"),
                "Rating": "Hot" if lead_score >= 71 else "Warm" if lead_score >= 41 else "Cold",
                "Description": f"WhatsApp Lead | Score: {lead_score}/100 | Latest message: {message or 'N/A'}"
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{ZOHO_API_DOMAIN}/crm/v2/Leads",
                json=data,
                headers=headers
            )

            result = response.json()

            if response.status_code == 401:
                await refresh_access_token()
                headers = await get_headers()
                response = await client.put(
                    f"{ZOHO_API_DOMAIN}/crm/v2/Leads",
                    json=data,
                    headers=headers
                )
                result = response.json()

            if result.get("data"):
                print(f"[Zoho] ✅ Lead updated: {lead_id}")
                return {"success": True, "zoho_lead_id": lead_id}
            else:
                print(f"[Zoho] ❌ Lead update failed: {result}")
                return {"success": False, "error": str(result)}

    except Exception as e:
        print(f"[Zoho] Error updating lead: {str(e)}")
        return {"success": False, "error": str(e)}


async def search_lead(phone: str) -> dict:
    """Search for an existing lead by phone number (prevents duplicate leads)"""

    try:
        headers = await get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{ZOHO_API_DOMAIN}/crm/v2/Leads/search?phone={phone}",
                headers=headers
            )

            if response.status_code == 401:
                await refresh_access_token()
                headers = await get_headers()
                response = await client.get(
                    f"{ZOHO_API_DOMAIN}/crm/v2/Leads/search?phone={phone}",
                    headers=headers
                )

            result = response.json()

            if result.get("data"):
                return {"found": True, "lead": result["data"][0]}
            else:
                return {"found": False}

    except Exception as e:
        print(f"[Zoho] Error searching lead: {str(e)}")
        return {"found": False}


async def add_note(contact_id: str, note: str) -> dict:
    """Add a note to a contact in Zoho CRM"""

    try:
        headers = await get_headers()

        data = {
            "data": [{
                "Note_Title": "WhatsApp Message",
                "Note_Content": note,
                "Parent_Id": contact_id,
                "se_module": "Contacts"
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ZOHO_API_DOMAIN}/crm/v2/Notes",
                json=data,
                headers=headers
            )

            result = response.json()
            print(f"[Zoho] Note added: {result}")
            return {"success": True}

    except Exception as e:
        print(f"[Zoho] Error adding note: {str(e)}")
        return {"success": False, "error": str(e)}


async def search_contact(phone: str) -> dict:
    """Search for existing contact by phone number"""

    try:
        headers = await get_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{ZOHO_API_DOMAIN}/crm/v2/Contacts/search?phone={phone}",
                headers=headers
            )

            result = response.json()

            if result.get("data"):
                return {"found": True, "contact": result["data"][0]}
            else:
                return {"found": False}

    except Exception as e:
        print(f"[Zoho] Error searching contact: {str(e)}")
        return {"found": False}