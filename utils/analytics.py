"""Analytics and visualization components."""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple


class AnalyticsDashboard:
    """Generate analytics visualizations for helpdesk tickets."""
    
    def __init__(self):
        """Initialize analytics dashboard."""
        sns.set_style("whitegrid")
        sns.set_palette("Set2")
    
    def create_category_distribution(self, df: pd.DataFrame) -> Tuple:
        """Create pie chart for category distribution."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14)
            return fig, ax
        
        category_counts = df['category'].value_counts()
        colors = sns.color_palette('Set2', len(category_counts))
        
        ax.pie(category_counts.values, labels=category_counts.index, 
               autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title('Ticket Distribution by Category', fontsize=14, fontweight='bold')
        
        return fig, ax
    
    def create_urgency_distribution(self, df: pd.DataFrame) -> Tuple:
        """Create bar chart for urgency levels."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14)
            return fig, ax
        
        urgency_counts = df['urgency'].value_counts().reindex(['High', 'Medium', 'Low'], fill_value=0)
        colors = {'High': '#FF6B6B', 'Medium': '#FFA500', 'Low': '#4CAF50'}
        
        bars = ax.bar(urgency_counts.index, urgency_counts.values, 
                     color=[colors[x] for x in urgency_counts.index])
        
        ax.set_xlabel('Urgency Level', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Tickets', fontsize=12, fontweight='bold')
        ax.set_title('Ticket Distribution by Urgency', fontsize=14, fontweight='bold')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        return fig, ax
    
    def create_department_workload(self, df: pd.DataFrame) -> Tuple:
        """Create horizontal bar chart for department workload."""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14)
            return fig, ax
        
        dept_counts = df['department'].value_counts()
        
        ax.barh(dept_counts.index, dept_counts.values, color=sns.color_palette('Set2', len(dept_counts)))
        ax.set_xlabel('Number of Tickets', fontsize=12, fontweight='bold')
        ax.set_ylabel('Department', fontsize=12, fontweight='bold')
        ax.set_title('Ticket Volume by Department', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, v in enumerate(dept_counts.values):
            ax.text(v + 0.1, i, str(v), va='center', fontweight='bold')
        
        return fig, ax
    
    def create_resolution_timeline(self, df: pd.DataFrame) -> Tuple:
        """Create line chart showing tickets over time."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if df.empty:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center', fontsize=14)
            return fig, ax
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        daily_tickets = df.groupby(df['timestamp'].dt.date).size()
        
        ax.plot(daily_tickets.index, daily_tickets.values, marker='o', 
               linewidth=2, markersize=8, color='#4CAF50')
        ax.fill_between(daily_tickets.index, daily_tickets.values, alpha=0.3, color='#4CAF50')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Tickets', fontsize=12, fontweight='bold')
        ax.set_title('Ticket Volume Timeline', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig, ax
