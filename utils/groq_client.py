"""Groq API client for AI-powered ticket analysis."""
import json
import os
from typing import Dict, Optional
from groq import Groq
import streamlit as st


class GroqClient:
    """Client for interacting with Groq API using Llama 3.3 70B."""
    
    def __init__(self):
        """Initialize Groq client with API key from environment or secrets."""
        try:
            # Try Streamlit secrets first (for deployment)
            api_key = st.secrets.get("GROQ_API_KEY")
        except:
            # Fall back to environment variable (for local development)
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment or Streamlit secrets")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_ticket(self, user_query: str) -> Optional[Dict]:
        """
        Analyze IT support ticket using Llama 3.3 70B.
        
        Args:
            user_query: User's IT issue description
            
        Returns:
            Dictionary containing category, urgency, solution, and routing info
        """
        system_prompt = """You are an expert IT helpdesk AI assistant. Analyze the user's IT issue and provide a structured response.

Response must be valid JSON with this exact structure:
{
    "category": "one of: Software, Hardware, Network, Login/Access, Other",
    "urgency": "one of: High, Medium, Low",
    "solution": "detailed troubleshooting steps in 3-5 bullet points",
    "department": "one of: Software Team, Hardware Team, Network Team, IT Security, General Support",
    "knowledge_base_articles": ["relevant article 1", "relevant article 2"],
    "confidence": 0.95
}

Classification rules:
- High urgency: System down, security breach, critical data loss, many users affected
- Medium urgency: Single user unable to work, performance issues, software crashes
- Low urgency: Enhancement requests, questions, minor inconveniences

Provide practical, actionable solutions."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"IT Issue: {user_query}"}
                ],
                temperature=0.3,
                max_tokens=1024,
                top_p=0.9,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
            return None
        except Exception as e:
            st.error(f"Error analyzing ticket: {e}")
            return None
    
    def get_token_usage(self) -> Dict:
        """Get token usage statistics (if available in response)."""
        # Placeholder for token tracking
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
