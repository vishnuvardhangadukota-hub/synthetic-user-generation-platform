import os
import json
import logging
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Generates structured JSON output from LLM"""
        pass

    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generates raw text response from LLM"""
        pass

class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()


class DeterministicFallbackGenerator(LLMProvider):
    """
    Development fallback generator used when LLM API keys are unavailable or API calls fail.
    Generates realistic, varied synthetic personas and consistent conversation responses.
    """

    SAMPLE_PERSONAS_POOL = [
        {
            "name": "Rahul Sharma",
            "age": 21,
            "occupation": "Engineering Student",
            "location": "Hyderabad",
            "demographics": {"education": "Undergraduate", "income_level": "Low (Student Allowance)"},
            "personality_traits": ["Budget conscious", "Social", "Impatient"],
            "behavioral_patterns": [
                "Orders food 3-4 times per week",
                "Checks discounts before ordering",
                "Prefers fast delivery under 30 mins"
            ],
            "psychological_profile": {
                "decision_style": "Price-driven",
                "risk_tolerance": "Moderate",
                "motivation": "Convenience and affordability"
            },
            "preferences": {"delivery_speed": "Very important", "discounts": "Very important", "subscription_limit": "Low"},
            "opinions": {},
            "memory_summary": ""
        },
        {
            "name": "Priya Verma",
            "age": 27,
            "occupation": "Software Engineer",
            "location": "Hyderabad",
            "demographics": {"education": "Bachelor's Degree", "income_level": "Moderate-High"},
            "personality_traits": ["Convenience seeker", "Tech-savvy", "Health conscious"],
            "behavioral_patterns": [
                "Orders late-night meals during work sprints",
                "Values reliable delivery tracking",
                "Prefers healthy meal options"
            ],
            "psychological_profile": {
                "decision_style": "Quality & Convenience-driven",
                "risk_tolerance": "High",
                "motivation": "Time-saving and quality food"
            },
            "preferences": {"delivery_speed": "Crucial", "quality": "High", "discounts": "Nice to have"},
            "opinions": {},
            "memory_summary": ""
        },
        {
            "name": "Ananya Reddy",
            "age": 24,
            "occupation": "Marketing Executive",
            "location": "Hyderabad",
            "demographics": {"education": "Master's Degree", "income_level": "Moderate"},
            "personality_traits": ["Trend-conscious", "Socializer", "Value seeker"],
            "behavioral_patterns": [
                "Orders group meals with colleagues",
                "Shares referral codes with friends",
                "Tries newly listed restaurants"
            ],
            "psychological_profile": {
                "decision_style": "Socially influenced",
                "risk_tolerance": "Moderate",
                "motivation": "Social connection and variety"
            },
            "preferences": {"group_discounts": "High", "variety": "High"},
            "opinions": {},
            "memory_summary": ""
        },
        {
            "name": "Vikram Rao",
            "age": 34,
            "occupation": "Product Manager",
            "location": "Hyderabad",
            "demographics": {"education": "MBA", "income_level": "High"},
            "personality_traits": ["Pragmatic", "Efficiency focused", "Loyal customer"],
            "behavioral_patterns": [
                "Subscribes to monthly premium delivery passes if value is clear",
                "Orders breakfast and dinner regularly",
                "Expects zero delivery delays"
            ],
            "psychological_profile": {
                "decision_style": "ROI & Efficiency driven",
                "risk_tolerance": "Low for poor service",
                "motivation": "Uninterrupted focus and reliability"
            },
            "preferences": {"priority_delivery": "Must have", "subscription": "Willing if >3 orders/week"},
            "opinions": {},
            "memory_summary": ""
        },
        {
            "name": "Sneha Kulkarni",
            "age": 22,
            "occupation": "Design Intern",
            "location": "Hyderabad",
            "demographics": {"education": "Undergraduate", "income_level": "Low"},
            "personality_traits": ["Frugal", "Detail-oriented", "Cautious"],
            "behavioral_patterns": [
                "Compares delivery fees across 3 apps before ordering",
                "Uses discount coupons exclusively",
                "Avoids premium delivery surcharges"
            ],
            "psychological_profile": {
                "decision_style": "Highly price-sensitive",
                "risk_tolerance": "Low",
                "motivation": "Maximum value for minimal cost"
            },
            "preferences": {"price": "Lowest priority cost", "delivery_fee": "Zero preferred"},
            "opinions": {},
            "memory_summary": ""
        }
    ]

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Returns realistic fallback personas generated deterministically."""
        logger.info("Using DeterministicFallbackGenerator for JSON generation")
        
        # Try to parse number of personas requested from user prompt
        num = 5
        import re
        match = re.search(r'generate exactly (\d+)', user_prompt, re.IGNORECASE)
        if match:
            num = int(match.group(1))

        personas = []
        for i in range(num):
            base = self.SAMPLE_PERSONAS_POOL[i % len(self.SAMPLE_PERSONAS_POOL)].copy()
            # Slight modification for index variation if num > len pool
            if i >= len(self.SAMPLE_PERSONAS_POOL):
                base["name"] = f"{base['name']} ({i+1})"
                base["age"] = base["age"] + (i % 3)
            
            # Deep copy dicts/lists
            p = json.loads(json.dumps(base))
            personas.append(p)

        return {"personas": personas}

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Generates consistent fallback text response based on persona constraints."""
        logger.info("Using DeterministicFallbackGenerator for text response")
        
        # Check if conversation or memory extraction
        if "Extract any new opinions" in system_prompt or "Extract any new opinions" in user_prompt:
            # Memory extraction simulation
            if "299" in user_prompt or "expensive" in user_prompt or "pay" in user_prompt:
                return json.dumps([
                    {
                        "topic": "subscription_pricing",
                        "opinion": "₹299 per month feels expensive",
                        "reason": "Limited budget and high price relative to student allowance",
                        "importance": 1.0
                    }
                ])
            return json.dumps([])

        # Conversation simulation
        user_msg = ""
        for line in user_prompt.split("\n"):
            if line.startswith("User:") or "Would you pay" in line or "Why" in line:
                user_msg += line + " "

        user_prompt_lower = user_prompt.lower()
        
        # Check persona traits in system prompt
        is_student = "student" in system_prompt.lower() or "intern" in system_prompt.lower()
        is_budget_conscious = "budget conscious" in system_prompt.lower() or "price-driven" in system_prompt.lower() or "low" in system_prompt.lower()

        if "299" in user_prompt_lower or ("subscription" in user_prompt_lower and "pay" in user_prompt_lower):
            if is_budget_conscious or is_student:
                return "As a student with a limited budget, ₹299 per month feels expensive to me."
            else:
                return "₹299 per month sounds reasonable if it includes free delivery on all orders, as I order quite frequently."

        if "why" in user_prompt_lower and ("expensive" in user_prompt_lower or "think" in user_prompt_lower):
            if is_budget_conscious or is_student:
                return "Like I mentioned, as an engineering student, my monthly allowance is tight. Spending ₹299 just for a subscription passes my threshold unless I order every single day."
            else:
                return "It depends on the delivery frequency. If I'm ordering less than 5 times a month, the break-even doesn't make sense."

        # Default fallback persona response
        return "That's an interesting question regarding the product. Based on my daily routine and financial considerations, I evaluate whether it genuinely saves me time and money before committing."


def get_llm_provider() -> LLMProvider:
    """Factory to get configured LLM provider or fallback generator"""
    if settings.LLM_API_KEY and settings.LLM_API_KEY.strip():
        logger.info(f"Initializing {settings.LLM_PROVIDER} LLM provider with model {settings.LLM_MODEL}")
        return OpenAILLMProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
    else:
        logger.warning("No LLM_API_KEY set. Falling back to DeterministicFallbackGenerator.")
        return DeterministicFallbackGenerator()
