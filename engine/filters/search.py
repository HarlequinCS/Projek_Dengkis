"""
Advanced filtering and search functionality for PROJEK DENGKIS.
Provides filtering for sessions, reports, and findings.
"""
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from functools import partial
import re


class FilterManager:
    """Manager for filtering and searching assessment data."""
    
    def __init__(self):
        self.filter_functions: Dict[str, Callable] = {
            'date_range': self._filter_by_date_range,
            'target': self._filter_by_target,
            'status': self._filter_by_status,
            'severity': self._filter_by_severity,
            'category': self._filter_by_category,
            'risk_score': self._filter_by_risk_score,
            'fuzzy_search': self._fuzzy_search
        }
    
    def filter_sessions(self, sessions: List[Dict], filters: Dict) -> List[Dict]:
        """
        Filter sessions based on criteria.
        
        Args:
            sessions: List of session dictionaries
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of sessions
        """
        filtered = sessions.copy()
        
        for filter_type, filter_value in filters.items():
            if filter_type in self.filter_functions and filter_value is not None:
                filter_func = self.filter_functions[filter_type]
                filtered = filter_func(filtered, filter_value, entity_type='session')
        
        return filtered
    
    def filter_findings(self, findings: List[Dict], filters: Dict) -> List[Dict]:
        """
        Filter findings based on criteria.
        
        Args:
            findings: List of finding dictionaries
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of findings
        """
        filtered = findings.copy()
        
        for filter_type, filter_value in filters.items():
            if filter_type in self.filter_functions and filter_value is not None:
                filter_func = self.filter_functions[filter_type]
                filtered = filter_func(filtered, filter_value, entity_type='finding')
        
        return filtered
    
    def search(self, items: List[Dict], query: str, fields: Optional[List[str]] = None) -> List[Dict]:
        """
        Fuzzy search across items.
        
        Args:
            items: List of items to search
            query: Search query string
            fields: Optional list of fields to search (searches all if None)
            
        Returns:
            List of matching items
        """
        if not query:
            return items
        
        query_lower = query.lower()
        results = []
        
        for item in items:
            if fields:
                search_fields = fields
            else:
                # Default fields to search
                search_fields = ['title', 'description', 'target', 'session_id']
            
            for field in search_fields:
                if field in item:
                    value = str(item[field]).lower()
                    if query_lower in value:
                        results.append(item)
                        break
        
        return results
    
    def _filter_by_date_range(self, items: List[Dict], value: Dict, entity_type: str) -> List[Dict]:
        """Filter by date range."""
        start_date = value.get('start')
        end_date = value.get('end')
        
        if not start_date and not end_date:
            return items
        
        filtered = []
        
        for item in items:
            date_field = 'started_at' if entity_type == 'session' else 'timestamp'
            item_date_str = item.get(date_field)
            
            if not item_date_str:
                continue
            
            try:
                item_date = datetime.fromisoformat(item_date_str.replace('Z', '+00:00'))
                
                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue
                
                filtered.append(item)
            except Exception:
                continue
        
        return filtered
    
    def _filter_by_target(self, items: List[Dict], value: str, entity_type: str) -> List[Dict]:
        """Filter by target."""
        if entity_type == 'session':
            return [item for item in items if item.get('target', '').lower() == value.lower()]
        return items
    
    def _filter_by_status(self, items: List[Dict], value: str, entity_type: str) -> List[Dict]:
        """Filter by status."""
        if entity_type == 'session':
            return [item for item in items if item.get('status', '').lower() == value.lower()]
        return items
    
    def _filter_by_severity(self, items: List[Dict], value: str, entity_type: str) -> List[Dict]:
        """Filter by severity."""
        if entity_type == 'finding':
            return [item for item in items if item.get('severity', '').lower() == value.lower()]
        return items
    
    def _filter_by_category(self, items: List[Dict], value: str, entity_type: str) -> List[Dict]:
        """Filter by category."""
        if entity_type == 'finding':
            return [item for item in items if item.get('category', '').lower() == value.lower()]
        return items
    
    def _filter_by_risk_score(self, items: List[Dict], value: Dict, entity_type: str) -> List[Dict]:
        """Filter by risk score range."""
        min_score = value.get('min', 0.0)
        max_score = value.get('max', 1.0)
        
        filtered = []
        for item in items:
            score = item.get('risk_score', 0.0)
            if min_score <= score <= max_score:
                filtered.append(item)
        
        return filtered
    
    def _fuzzy_search(self, items: List[Dict], value: str, entity_type: str) -> List[Dict]:
        """Fuzzy search filter."""
        return self.search(items, value)


def create_filter(
    date_range: Optional[Dict] = None,
    target: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    risk_score: Optional[Dict] = None,
    search_query: Optional[str] = None
) -> Dict:
    """
    Create filter dictionary.
    
    Args:
        date_range: Dict with 'start' and 'end' datetime objects
        target: Target filter string
        status: Status filter string
        severity: Severity filter string
        category: Category filter string
        risk_score: Dict with 'min' and 'max' risk scores
        search_query: Fuzzy search query string
        
    Returns:
        Filter dictionary
    """
    filter_dict = {}
    
    if date_range:
        filter_dict['date_range'] = date_range
    if target:
        filter_dict['target'] = target
    if status:
        filter_dict['status'] = status
    if severity:
        filter_dict['severity'] = severity
    if category:
        filter_dict['category'] = category
    if risk_score:
        filter_dict['risk_score'] = risk_score
    if search_query:
        filter_dict['fuzzy_search'] = search_query
    
    return filter_dict
