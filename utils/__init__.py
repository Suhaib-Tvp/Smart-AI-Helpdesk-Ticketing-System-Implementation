"""Utilities package for Smart AI Helpdesk System."""

__all__ = ['GroqClient', 'TicketManager', 'AnalyticsDashboard', 'KnowledgeBase']

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == 'GroqClient':
        from .groq_client import GroqClient
        return GroqClient
    elif name == 'TicketManager':
        from .ticket_manager import TicketManager
        return TicketManager
    elif name == 'AnalyticsDashboard':
        from .analytics import AnalyticsDashboard
        return AnalyticsDashboard
    elif name == 'KnowledgeBase':
        from .knowledge_base import KnowledgeBase
        return KnowledgeBase
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
