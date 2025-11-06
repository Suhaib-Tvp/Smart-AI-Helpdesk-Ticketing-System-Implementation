"""Ticket management and CSV persistence."""
import pandas as pd
import os
from datetime import datetime
from typing import Optional


class TicketManager:
    """Manages ticket data with CSV persistence."""
    
    def __init__(self, csv_path: str = "data/tickets.csv"):
        """Initialize ticket manager with CSV file path."""
        self.csv_path = csv_path
        self._ensure_data_directory()
        self._initialize_csv()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
    
    def _initialize_csv(self):
        """Create CSV with headers if it doesn't exist."""
        if not os.path.exists(self.csv_path):
            df = pd.DataFrame(columns=[
                'ticket_id', 'timestamp', 'user_query', 'category', 
                'urgency', 'solution', 'department', 'status', 
                'resolved_by', 'confidence'
            ])
            df.to_csv(self.csv_path, index=False)
    
    def generate_ticket_id(self) -> str:
        """Generate unique ticket ID."""
        df = self.load_tickets()
        count = len(df) + 1
        return f"TKT-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
    
    def save_ticket(self, ticket_data: dict) -> str:
        """
        Save new ticket to CSV.
        
        Args:
            ticket_data: Dictionary containing ticket information
            
        Returns:
            Generated ticket ID
        """
        ticket_id = self.generate_ticket_id()
        
        new_ticket = {
            'ticket_id': ticket_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_query': ticket_data.get('user_query', ''),
            'category': ticket_data.get('category', 'Other'),
            'urgency': ticket_data.get('urgency', 'Low'),
            'solution': ticket_data.get('solution', ''),
            'department': ticket_data.get('department', 'General Support'),
            'status': ticket_data.get('status', 'Resolved'),
            'resolved_by': ticket_data.get('resolved_by', 'AI'),
            'confidence': ticket_data.get('confidence', 0.0)
        }
        
        df = self.load_tickets()
        df = pd.concat([df, pd.DataFrame([new_ticket])], ignore_index=True)
        df.to_csv(self.csv_path, index=False)
        
        return ticket_id
    
    def load_tickets(self) -> pd.DataFrame:
        """Load all tickets from CSV."""
        try:
            return pd.read_csv(self.csv_path)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return pd.DataFrame(columns=[
                'ticket_id', 'timestamp', 'user_query', 'category', 
                'urgency', 'solution', 'department', 'status', 
                'resolved_by', 'confidence'
            ])
    
    def get_ticket_by_id(self, ticket_id: str) -> Optional[dict]:
        """Retrieve specific ticket by ID."""
        df = self.load_tickets()
        ticket = df[df['ticket_id'] == ticket_id]
        if not ticket.empty:
            return ticket.iloc[0].to_dict()
        return None
    
    def update_ticket_status(self, ticket_id: str, status: str, department: str = None):
        """Update ticket status and optionally reassign department."""
        df = self.load_tickets()
        mask = df['ticket_id'] == ticket_id
        df.loc[mask, 'status'] = status
        if department:
            df.loc[mask, 'department'] = department
            df.loc[mask, 'resolved_by'] = 'Escalated'
        df.to_csv(self.csv_path, index=False)
    
    def get_statistics(self) -> dict:
        """Calculate key statistics from tickets."""
        df = self.load_tickets()
        
        if df.empty:
            return {
                'total_tickets': 0,
                'ai_resolved': 0,
                'escalated': 0,
                'resolution_rate': 0.0,
                'avg_confidence': 0.0
            }
        
        stats = {
            'total_tickets': len(df),
            'ai_resolved': len(df[df['resolved_by'] == 'AI']),
            'escalated': len(df[df['resolved_by'] == 'Escalated']),
            'resolution_rate': (len(df[df['resolved_by'] == 'AI']) / len(df) * 100) if len(df) > 0 else 0,
            'avg_confidence': df['confidence'].mean() if 'confidence' in df.columns else 0.0
        }
        
        return stats
