"""
Scheduler for recurring security assessments.
"""
import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from pathlib import Path
import uuid

from engine.batch.scanner import BatchScanner
from engine.logging.logger import get_logger


@dataclass
class ScheduleConfig:
    """Configuration for scheduled scan."""
    target: str
    schedule_type: str  # 'daily', 'weekly', 'monthly', 'once'
    time: str  # HH:MM format
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    enabled: bool = True


class ScanScheduler:
    """
    Scheduler for recurring security assessments.
    """
    
    def __init__(self, storage_dir: str = 'storage'):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.schedules_file = self.storage_dir / 'schedules.json'
        self.schedules: Dict[str, ScheduleConfig] = {}
        self.running = False
        self.logger = get_logger()
        self.scanner = BatchScanner()
        self.load_schedules()
    
    def add_schedule(self, config: ScheduleConfig) -> str:
        """
        Add a new schedule.
        
        Args:
            config: Schedule configuration
            
        Returns:
            Schedule ID
        """
        schedule_id = str(uuid.uuid4())
        self.schedules[schedule_id] = config
        self.save_schedules()
        self.logger.info(f"Added schedule {schedule_id} for {config.target}")
        return schedule_id
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a schedule.
        
        Args:
            schedule_id: Schedule ID to remove
            
        Returns:
            True if removed, False otherwise
        """
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            self.save_schedules()
            self.logger.info(f"Removed schedule {schedule_id}")
            return True
        return False
    
    def get_schedules(self) -> Dict[str, ScheduleConfig]:
        """Get all schedules."""
        return self.schedules.copy()
    
    def save_schedules(self):
        """Save schedules to file."""
        schedules_data = {}
        for schedule_id, config in self.schedules.items():
            schedules_data[schedule_id] = {
                'target': config.target,
                'schedule_type': config.schedule_type,
                'time': config.time,
                'day_of_week': config.day_of_week,
                'day_of_month': config.day_of_month,
                'enabled': config.enabled
            }
        
        with open(self.schedules_file, 'w') as f:
            json.dump(schedules_data, f, indent=2)
    
    def load_schedules(self):
        """Load schedules from file."""
        if self.schedules_file.exists():
            try:
                with open(self.schedules_file, 'r') as f:
                    schedules_data = json.load(f)
                
                for schedule_id, data in schedules_data.items():
                    self.schedules[schedule_id] = ScheduleConfig(**data)
            except Exception as e:
                self.logger.error(f"Failed to load schedules: {e}")
    
    async def start(self):
        """Start scheduler."""
        self.running = True
        self.logger.info("Scheduler started")
        
        while self.running:
            await self._check_and_execute()
            await asyncio.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        self.logger.info("Scheduler stopped")
    
    async def _check_and_execute(self):
        """Check schedules and execute due scans."""
        now = datetime.now()
        
        for schedule_id, config in self.schedules.items():
            if not config.enabled:
                continue
            
            if self._should_execute(config, now):
                self.logger.info(f"Executing scheduled scan {schedule_id} for {config.target}")
                await self._execute_scan(config)
    
    def _should_execute(self, config: ScheduleConfig, now: datetime) -> bool:
        """Check if schedule should execute now."""
        # Parse time
        try:
            hour, minute = map(int, config.time.split(':'))
        except Exception:
            return False
        
        # Check if current time matches
        if now.hour != hour or now.minute != minute:
            return False
        
        if config.schedule_type == 'daily':
            return True
        elif config.schedule_type == 'weekly':
            return now.weekday() == (config.day_of_week or 0)
        elif config.schedule_type == 'monthly':
            return now.day == (config.day_of_month or 1)
        elif config.schedule_type == 'once':
            # Execute once, then disable
            config.enabled = False
            self.save_schedules()
            return True
        
        return False
    
    async def _execute_scan(self, config: ScheduleConfig):
        """Execute scheduled scan."""
        try:
            result = await self.scanner.scan_targets([config.target], authorized=True)
            self.logger.info(f"Scheduled scan completed: {result}")
        except Exception as e:
            self.logger.error(f"Scheduled scan failed: {e}")
