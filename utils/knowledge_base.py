"""Knowledge base management for common IT issues."""
import json
import os


class KnowledgeBase:
    """Manages knowledge base articles for IT support."""
    
    def __init__(self, kb_path: str = "data/knowledge_base.json"):
        """Initialize knowledge base."""
        self.kb_path = kb_path
        self._ensure_knowledge_base()
    
    def _ensure_knowledge_base(self):
        """Create default knowledge base if it doesn't exist."""
        if not os.path.exists(self.kb_path):
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            
            default_kb = {
                "Software": [
                    {
                        "title": "Application Won't Launch",
                        "solution": "Try restarting the application, clearing cache, or reinstalling"
                    },
                    {
                        "title": "Software Update Issues",
                        "solution": "Check internet connection, verify admin rights, restart update service"
                    }
                ],
                "Hardware": [
                    {
                        "title": "Computer Won't Turn On",
                        "solution": "Check power cable, try different outlet, inspect power button"
                    },
                    {
                        "title": "Printer Not Working",
                        "solution": "Check connections, restart printer, update drivers, check ink/toner"
                    }
                ],
                "Network": [
                    {
                        "title": "No Internet Connection",
                        "solution": "Restart router, check cables, run network diagnostics, verify Wi-Fi password"
                    },
                    {
                        "title": "Slow Network Speed",
                        "solution": "Check bandwidth usage, restart network equipment, scan for malware"
                    }
                ],
                "Login/Access": [
                    {
                        "title": "Forgot Password",
                        "solution": "Use password reset link, contact IT admin, verify identity"
                    },
                    {
                        "title": "Account Locked",
                        "solution": "Wait 30 minutes for auto-unlock or contact IT security team"
                    }
                ]
            }
            
            with open(self.kb_path, 'w') as f:
                json.dump(default_kb, f, indent=2)
    
    def get_articles_by_category(self, category: str) -> list:
        """Retrieve knowledge base articles for a category."""
        try:
            with open(self.kb_path, 'r') as f:
                kb = json.load(f)
            return kb.get(category, [])
        except Exception:
            return []
