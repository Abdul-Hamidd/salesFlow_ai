import httpx
import json
from typing import Any
from a2a.agent_card import ALL_AGENTS, AgentCard

# A2A Protocol Client
class A2AClient:
    """Client for Agent to Agent communication"""

    def __init__(self):
        self.agents = ALL_AGENTS
        self.timeout = 30.0

    async def send_task(self, agent_name: str, task: dict) -> dict:
        """Send a task to another agent and get result"""
        agent_card = self.agents.get(agent_name)
        if not agent_card:
            return {"error": f"Agent {agent_name} not found"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{agent_card.url}/task",
                    json=task,
                    headers={"Content-Type": "application/json"}
                )
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_agent_info(self, agent_name: str) -> dict:
        """Get agent card information"""
        agent_card = self.agents.get(agent_name)
        if not agent_card:
            return {"error": f"Agent {agent_name} not found"}
        return agent_card.to_dict()

    async def check_agent_health(self, agent_name: str) -> bool:
        """Check if agent is online and healthy"""
        agent_card = self.agents.get(agent_name)
        if not agent_card:
            return False

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{agent_card.url}/health")
                return response.status_code == 200
            except:
                return False

    async def broadcast_task(self, task: dict, exclude: list = []) -> dict:
        """Send task to all agents simultaneously"""
        results = {}
        for agent_name, agent_card in self.agents.items():
            if agent_name not in exclude:
                results[agent_name] = await self.send_task(agent_name, task)
        return results


# Pipeline — Main workflow that connects all agents
class AgentPipeline:
    """Orchestrates the complete multi-agent workflow"""

    def __init__(self):
        self.a2a = A2AClient()

    async def process_whatsapp_message(self, phone_number: str, message: str, name: str = None) -> dict:
        """
        Complete pipeline for processing incoming WhatsApp message:
        Step 1: Contact Agent — Check/create contact
        Step 2: Lead Agent — Analyze and score lead
        Step 3: Response Agent — Generate and send reply
        Step 4: Follow Up Agent — Schedule follow up
        Step 5: Notification Agent — Alert business owner
        """

        print(f"[Pipeline] Processing message from {phone_number}")

        # Step 1: Contact Agent
        print("[Step 1] Running Contact Agent...")
        contact_result = await self.a2a.send_task("contact_agent", {
            "phone_number": phone_number,
            "name": name,
            "message": message
        })
        contact_id = contact_result.get("contact_id")
        print(f"[Step 1] Contact ID: {contact_id}")

        # Step 2: Lead Agent
        print("[Step 2] Running Lead Agent...")
        lead_result = await self.a2a.send_task("lead_agent", {
            "contact_id": contact_id,
            "message": message,
            "phone_number": phone_number,
            "name": name
        })
        lead_score = lead_result.get("score", 50)
        lead_status = lead_result.get("status", "warm")
        print(f"[Step 2] Lead Score: {lead_score} | Status: {lead_status}")

        # Step 3: Response Agent
        print("[Step 3] Running Response Agent...")
        response_result = await self.a2a.send_task("response_agent", {
            "contact_id": contact_id,
            "phone_number": phone_number,
            "message": message,
            "lead_score": lead_score
        })
        print(f"[Step 3] Response sent to {phone_number}")

        # Step 4: Follow Up Agent
        print("[Step 4] Running Follow Up Agent...")
        followup_result = await self.a2a.send_task("followup_agent", {
            "contact_id": contact_id,
            "phone_number": phone_number,
            "lead_score": lead_score,
            "lead_status": lead_status
        })
        print(f"[Step 4] Follow up scheduled")

        # Step 5: Notification Agent
        print("[Step 5] Running Notification Agent...")
        notification_result = await self.a2a.send_task("notification_agent", {
            "contact_id": contact_id,
            "phone_number": phone_number,
            "lead_score": lead_score,
            "lead_status": lead_status
        })
        print(f"[Step 5] Owner notified")

        return {
            "success": True,
            "contact_id": contact_id,
            "lead_score": lead_score,
            "lead_status": lead_status,
            "message": "Pipeline completed successfully"
        }


# Global pipeline instance
pipeline = AgentPipeline()