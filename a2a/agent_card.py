# Agent Card — Every agent's identity in A2A Protocol
# This tells other agents WHO this agent is and WHAT it can do

from dataclasses import dataclass
from typing import List


@dataclass
class AgentCard:
    """Defines an agent's identity and capabilities"""
    name: str
    description: str
    url: str
    version: str
    skills: List[str]

    def to_dict(self) -> dict:
        """Convert agent card to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "skills": self.skills
        }


# Define all agent cards for our system
CONTACT_AGENT_CARD = AgentCard(
    name="Contact Agent",
    description="Checks if customer exists in database, creates new contact if not",
    url="http://localhost:8001",
    version="1.0.0",
    skills=["check_contact", "create_contact", "get_history"]
)

LEAD_AGENT_CARD = AgentCard(
    name="Lead Agent",
    description="Analyzes customer message and assigns lead score using AI",
    url="http://localhost:8002",
    version="1.0.0",
    skills=["analyze_message", "score_lead", "classify_lead"]
)

RESPONSE_AGENT_CARD = AgentCard(
    name="Response Agent",
    description="Generates personalized WhatsApp reply using AI and product database",
    url="http://localhost:8003",
    version="1.0.0",
    skills=["generate_reply", "fetch_products", "send_message"]
)

FOLLOWUP_AGENT_CARD = AgentCard(
    name="Follow Up Agent",
    description="Schedules automatic follow ups based on lead score",
    url="http://localhost:8004",
    version="1.0.0",
    skills=["schedule_followup", "send_followup", "manage_reminders"]
)

NOTIFICATION_AGENT_CARD = AgentCard(
    name="Notification Agent",
    description="Sends alerts and daily reports to business owner",
    url="http://localhost:8005",
    version="1.0.0",
    skills=["send_alert", "generate_report", "update_dashboard"]
)

# All agents registry
ALL_AGENTS = {
    "contact_agent": CONTACT_AGENT_CARD,
    "lead_agent": LEAD_AGENT_CARD,
    "response_agent": RESPONSE_AGENT_CARD,
    "followup_agent": FOLLOWUP_AGENT_CARD,
    "notification_agent": NOTIFICATION_AGENT_CARD
}