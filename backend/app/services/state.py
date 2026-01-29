"""
State Management Service for IntelliBin Simulation.
Manages in-memory state without database dependencies.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import copy


class StateManager:
    """
    Manages in-memory state for the simulation.
    Loads initial data from JSON files and tracks all changes.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.data_path = Path(__file__).parent.parent / "data"
        self.substances: dict = {}
        self.containers: dict = {}
        self.rules: dict = {}
        self.disposal_log: list = []
        self.alerts: list = []
        self.simulated_time: datetime = datetime.now()
        self._initial_containers: dict = {}  # Store initial state for reset
        
        self._load_data()
        self._initialized = True
    
    def _load_data(self):
        """Load all JSON data files"""
        # Load substances
        substances_path = self.data_path / "substances.json"
        if substances_path.exists():
            with open(substances_path) as f:
                data = json.load(f)
                for s in data.get("substances", []):
                    self.substances[s["id"]] = s
        
        # Load containers
        containers_path = self.data_path / "containers.json"
        if containers_path.exists():
            with open(containers_path) as f:
                data = json.load(f)
                for c in data.get("containers", []):
                    self.containers[c["container_id"]] = c
                # Store deep copy for reset
                self._initial_containers = copy.deepcopy(self.containers)
        
        # Load rules
        rules_path = self.data_path / "rules.json"
        if rules_path.exists():
            with open(rules_path) as f:
                self.rules = json.load(f)
        
        print(f"[StateManager] Loaded {len(self.substances)} substances")
        print(f"[StateManager] Loaded {len(self.containers)} containers")
    
    def reset(self):
        """Reset state to initial values"""
        self.containers = copy.deepcopy(self._initial_containers)
        self.disposal_log = []
        self.alerts = []
        self.simulated_time = datetime.now()
        print("[StateManager] Simulation reset to initial state")
    
    def get_substance(self, substance_id: str) -> Optional[dict]:
        """Get substance by ID"""
        return self.substances.get(substance_id)
    
    def get_all_substances(self) -> list[dict]:
        """Get all substances"""
        return list(self.substances.values())
    
    def get_container(self, container_id: str) -> Optional[dict]:
        """Get container by ID"""
        return self.containers.get(container_id)
    
    def get_all_containers(self) -> list[dict]:
        """Get all containers"""
        return list(self.containers.values())
    
    def get_containers_by_stream(self, waste_stream: str) -> list[dict]:
        """Get all containers for a specific waste stream"""
        return [c for c in self.containers.values() 
                if c["waste_stream"] == waste_stream]
    
    def update_container(self, container_id: str, 
                         substance_name: str,
                         category: str,
                         quantity_ml: float,
                         concentration: str) -> dict:
        """Add substance to container and update state"""
        container = self.containers[container_id]
        
        # Create content entry
        content = {
            "substance": substance_name,
            "category": category,
            "quantity_ml": quantity_ml,
            "concentration": concentration,
            "added_at": self.simulated_time.isoformat() + "Z"
        }
        
        container["contents"].append(content)
        container["current_fill_ml"] += quantity_ml
        
        # Set accumulation start if first disposal
        if container["accumulation_start"] is None:
            container["accumulation_start"] = self.simulated_time.isoformat() + "Z"
            # Set 90-day deadline
            deadline = self.simulated_time + timedelta(days=90)
            container["pickup_deadline"] = deadline.isoformat() + "Z"
            container["status"] = "Active"
        
        # Check if full
        fill_percent = (container["current_fill_ml"] / container["capacity_ml"]) * 100
        if fill_percent >= 95:
            container["status"] = "Full"
        
        # Log disposal
        log_entry = {
            "id": f"disp-{len(self.disposal_log) + 1:04d}",
            "timestamp": self.simulated_time.isoformat() + "Z",
            "container_id": container_id,
            "substance": substance_name,
            "category": category,
            "quantity_ml": quantity_ml,
            "concentration": concentration
        }
        self.disposal_log.append(log_entry)
        
        return container
    
    def add_alert(self, container_id: str, alert_type: str, 
                  severity: str, title: str, message: str) -> dict:
        """Add an alert"""
        alert = {
            "id": f"alert-{len(self.alerts) + 1:04d}",
            "container_id": container_id,
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "created_at": self.simulated_time.isoformat() + "Z",
            "acknowledged": False
        }
        self.alerts.append(alert)
        return alert
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False
    
    def get_alerts(self, include_acknowledged: bool = False) -> list[dict]:
        """Get alerts"""
        if include_acknowledged:
            return self.alerts
        return [a for a in self.alerts if not a["acknowledged"]]
    
    def get_disposal_log(self, limit: int = 50) -> list[dict]:
        """Get recent disposal log entries"""
        return list(reversed(self.disposal_log[-limit:]))
    
    def advance_time(self, days: int) -> int:
        """
        Advance simulated time and check for deadline alerts.
        Returns number of new alerts generated.
        """
        self.simulated_time += timedelta(days=days)
        return self._check_deadlines()
    
    def _check_deadlines(self) -> int:
        """Check for deadline alerts, returns count of new alerts"""
        new_alerts = 0
        
        for container in self.containers.values():
            if container.get("pickup_deadline"):
                deadline = datetime.fromisoformat(
                    container["pickup_deadline"].replace("Z", "")
                )
                days_remaining = (deadline - self.simulated_time).days
                
                # Check if alert already exists for this container
                existing = any(
                    a["container_id"] == container["container_id"] 
                    and a["alert_type"] == "Deadline"
                    and not a["acknowledged"]
                    for a in self.alerts
                )
                
                if not existing:
                    if days_remaining <= 7 and days_remaining > 0:
                        self.add_alert(
                            container["container_id"],
                            "Deadline",
                            "Caution",
                            "Pickup deadline approaching",
                            f"Container {container['container_id']} must be picked up within {days_remaining} days."
                        )
                        new_alerts += 1
                    elif days_remaining <= 0:
                        self.add_alert(
                            container["container_id"],
                            "Deadline",
                            "Danger",
                            "Pickup deadline exceeded",
                            f"Container {container['container_id']} has exceeded its pickup deadline!"
                        )
                        new_alerts += 1
        
        return new_alerts
    
    def get_simulated_time(self) -> datetime:
        """Get the current simulated time"""
        return self.simulated_time


# Singleton instance
state_manager = StateManager()
