"""
KALI LINUX INTEGRATION - Native Kali features
Nerd Font icons, desktop notifications, session persistence.
"""
import os
import subprocess
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from engine.logging.logger import get_logger


class KaliIntegration:
    """
    Kali Linux native integration features.
    Icons, notifications, session persistence.
    """
    
    def __init__(self):
        self.logger = get_logger()
        self.db_path = Path("/opt/dengkis/db")
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.session_db = self.db_path / "sessions.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for session persistence."""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                target TEXT,
                attack_mode TEXT,
                findings TEXT,
                state TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                endpoint TEXT,
                parameter TEXT,
                payload TEXT,
                category TEXT,
                confidence TEXT,
                evidence TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_vulnerability_icon(self, category: str) -> str:
        """
        Get Nerd Font icon for vulnerability type.
        Uses tactical icons: Skull, Biohazard, Terminal.
        """
        icons = {
            'sql_injection': '💀',  # Skull
            'xss': '☢',  # Biohazard
            'command_injection': '💻',  # Terminal
            'rce': '💻',
            'ssti': '⚡',
            'lfi': '📁',
            'auth_bypass': '🔓',
            'open_redirect': '↪',
            'prototype_pollution': '🧬',
            'mass_assignment': '⚖',
        }
        return icons.get(category.lower(), '⚠')
    
    def send_notification(self, title: str, message: str, urgency: str = "normal"):
        """
        Send desktop notification using notify-send.
        
        Args:
            title: Notification title
            message: Notification message
            urgency: normal, low, critical
        """
        try:
            subprocess.run([
                'notify-send',
                f'--urgency={urgency}',
                title,
                message
            ], check=False, capture_output=True)
            self.logger.debug(f"[KALI] Notification sent: {title}")
        except Exception as e:
            self.logger.debug(f"[KALI] Failed to send notification: {e}")
    
    def notify_critical_finding(self, finding: Dict):
        """Send critical finding notification."""
        category = finding.get('category', 'unknown')
        endpoint = finding.get('endpoint', 'unknown')
        icon = self.get_vulnerability_icon(category)
        
        title = f"{icon} CRITICAL: {category.upper()}"
        message = f"Endpoint: {endpoint}\nConfidence: {finding.get('confidence', 'unknown')}"
        
        self.send_notification(title, message, urgency="critical")
    
    def save_session(self, session_id: str, target: str, attack_mode: str, 
                    findings: List[Dict], state: Dict):
        """Save session state to SQLite database."""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        import json
        findings_json = json.dumps(findings)
        state_json = json.dumps(state)
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions 
            (session_id, target, attack_mode, findings, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            target,
            attack_mode,
            findings_json,
            state_json,
            datetime.utcnow().isoformat(),
            datetime.utcnow().isoformat()
        ))
        
        # Save individual findings
        for finding in findings:
            cursor.execute("""
                INSERT INTO findings 
                (session_id, endpoint, parameter, payload, category, confidence, evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                finding.get('endpoint'),
                finding.get('parameter'),
                finding.get('payload'),
                finding.get('category'),
                finding.get('confidence'),
                json.dumps(finding.get('evidence', [])),
                datetime.utcnow().isoformat()
            ))
        
        conn.commit()
        conn.close()
        self.logger.info(f"[KALI] Session saved: {session_id}")
    
    def load_session(self, session_id: str) -> Optional[Dict]:
        """Load session state from database."""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT target, attack_mode, findings, state, updated_at
            FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            import json
            return {
                'target': row[0],
                'attack_mode': row[1],
                'findings': json.loads(row[2]),
                'state': json.loads(row[3]),
                'updated_at': row[4]
            }
        return None
    
    def list_sessions(self) -> List[Dict]:
        """List all saved sessions."""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, target, attack_mode, updated_at
            FROM sessions ORDER BY updated_at DESC
        """)
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'target': row[1],
                'attack_mode': row[2],
                'updated_at': row[3]
            })
        
        conn.close()
        return sessions
