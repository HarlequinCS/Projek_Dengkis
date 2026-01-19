"""
Session persistence system for PROJEK DENGKIS.
Provides save/load functionality for assessment sessions.
"""
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class SessionStore:
    """
    Session persistence system with JSON and Optional SQLite support.
    """
    
    def __init__(self, storage_dir: str = 'storage'):
        """
        Initialize session store.
        
        Args:
            storage_dir: Directory for storing session data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.json_dir = self.storage_dir / 'json'
        self.json_dir.mkdir(exist_ok=True)
        self.db_path = self.storage_dir / 'sessions.db'
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for session storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT,
                summary TEXT,
                data_path TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_session(self, session_data: Dict, session_id: Optional[str] = None) -> str:
        """
        Save session data to JSON file.
        
        Args:
            session_data: Session data dictionary
            session_id: Optional session ID (generated if not provided)
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = session_data.get('session_id', str(uuid.uuid4()))
        
        # Save to JSON
        json_file = self.json_dir / f"{session_id}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        # Save metadata to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (session_id, target, started_at, completed_at, status, summary, data_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_data.get('target', 'Unknown'),
            session_data.get('started_at', datetime.utcnow().isoformat()),
            session_data.get('completed_at'),
            session_data.get('status', 'active'),
            json.dumps(session_data.get('summary', {})),
            str(json_file)
        ))
        conn.commit()
        conn.close()
        
        return session_id
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """
        Load session data by session ID.
        
        Args:
            session_id: Session ID to load
            
        Returns:
            Session data dictionary or None if not found
        """
        json_file = self.json_dir / f"{session_id}.json"
        
        if not json_file.exists():
            return None
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def list_sessions(self, target: Optional[str] = None) -> List[Dict]:
        """
        List all saved sessions, Optional, nally filtered by target.
        
        Args:
            target: Optional target filter
            
        Returns:
            List of session metadata dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if target:
            cursor.execute(
                'SELECT * FROM sessions WHERE target = ? ORDER BY started_at DESC',
                (target,)
            )
        else:
            cursor.execute('SELECT * FROM sessions ORDER BY started_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['session_id', 'target', 'started_at', 'completed_at', 'status', 'summary', 'data_path']
        sessions = []
        
        for row in rows:
            session_dict = dict(zip(columns, row))
            if session_dict['summary']:
                try:
                    session_dict['summary'] = json.loads(session_dict['summary'])
                except Exception:
                    pass
            sessions.append(session_dict)
        
        return sessions
    
    def compare_sessions(self, session_id1: str, session_id2: str) -> Dict:
        """
        Compare two sessions and return differences.
        
        Args:
            session_id1: First session ID
            session_id2: Second session ID
            
        Returns:
            Dictionary containing comparison results
        """
        session1 = self.load_session(session_id1)
        session2 = self.load_session(session_id2)
        
        if not session1 or not session2:
            return {'error': 'One or both sessions not found'}
        
        comparison = {
            'session1_id': session_id1,
            'session2_id': session_id2,
            'target': session1.get('target'),
            'differences': {}
        }
        
        # Compare findings
        findings1 = session1.get('findings', [])
        findings2 = session2.get('findings', [])
        
        comparison['differences']['findings_count'] = {
            'session1': len(findings1),
            'session2': len(findings2),
            'delta': len(findings2) - len(findings1)
        }
        
        # Compare risk scores
        risk1 = session1.get('risk_score', 0.0)
        risk2 = session2.get('risk_score', 0.0)
        
        comparison['differences']['risk_score'] = {
            'session1': risk1,
            'session2': risk2,
            'delta': risk2 - risk1
        }
        
        return comparison
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        json_file = self.json_dir / f"{session_id}.json"
        
        # Delete from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        # Delete JSON file
        if json_file.exists():
            json_file.unlink()
        
        return deleted
