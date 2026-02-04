"""
VortexL2 Configuration Management

Handles loading/saving configuration from /etc/vortexl2/config.yaml
with secure file permissions.
"""

import os
import uuid
import socket
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any


CONFIG_DIR = Path("/etc/vortexl2")
CONFIG_FILE = CONFIG_DIR / "config.yaml"


class Config:
    """Configuration manager for VortexL2."""
    
    # Default values
    DEFAULTS = {
        "version": "1.0.0",
        "role": None,  # "IRAN" or "KHAREJ"
        "ip_iran": None,
        "ip_kharej": None,
        "iran_iface_ip": "10.30.30.1",
        "kharej_iface_ip": "10.30.30.2",
        "remote_forward_ip": "10.30.30.2",
        "forwarded_ports": [],
        # Tunnel IDs (role-based defaults applied at runtime)
        "tunnel_id": None,
        "peer_tunnel_id": None,
        "session_id": None,
        "peer_session_id": None,
    }
    
    # Role-based default tunnel IDs
    ROLE_TUNNEL_DEFAULTS = {
        "IRAN": {
            "tunnel_id": 1000,
            "peer_tunnel_id": 2000,
            "session_id": 10,
            "peer_session_id": 20,
        },
        "KHAREJ": {
            "tunnel_id": 2000,
            "peer_tunnel_id": 1000,
            "session_id": 20,
            "peer_session_id": 10,
        },
    }
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load()
    
    def _load(self) -> None:
        """Load configuration from file or create defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception:
                self._config = {}
        
        # Apply defaults for missing keys
        for key, default in self.DEFAULTS.items():
            if key not in self._config:
                self._config[key] = default

    
    def _save(self) -> None:
        """Save configuration to file with secure permissions."""
        # Create config directory if not exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write config
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)
        
        # Set secure permissions (owner read/write only)
        os.chmod(CONFIG_FILE, 0o600)
    
    def save(self) -> None:
        """Public method to save configuration."""
        self._save()
    
    @property
    def role(self) -> Optional[str]:
        return self._config.get("role")
    
    @role.setter
    def role(self, value: str) -> None:
        if value not in ("IRAN", "KHAREJ", None):
            raise ValueError("Role must be 'IRAN' or 'KHAREJ'")
        self._config["role"]  = value
        self._save()
    
    @property
    def ip_iran(self) -> Optional[str]:
        return self._config.get("ip_iran")
    
    @ip_iran.setter
    def ip_iran(self, value: str) -> None:
        self._config["ip_iran"] = value
        self._save()
    
    @property
    def ip_kharej(self) -> Optional[str]:
        return self._config.get("ip_kharej")
    
    @ip_kharej.setter
    def ip_kharej(self, value: str) -> None:
        self._config["ip_kharej"] = value
        self._save()
    
    @property
    def iran_iface_ip(self) -> str:
        return self._config.get("iran_iface_ip", "10.30.30.1")
    
    @iran_iface_ip.setter
    def iran_iface_ip(self, value: str) -> None:
        self._config["iran_iface_ip"] = value
        self._save()
    
    @property
    def kharej_iface_ip(self) -> str:
        return self._config.get("kharej_iface_ip", "10.30.30.2")
    
    @kharej_iface_ip.setter
    def kharej_iface_ip(self, value: str) -> None:
        self._config["kharej_iface_ip"] = value
        self._save()
    
    @property
    def remote_forward_ip(self) -> str:
        return self._config.get("remote_forward_ip", "10.30.30.2")
    
    @remote_forward_ip.setter
    def remote_forward_ip(self, value: str) -> None:
        self._config["remote_forward_ip"] = value
        self._save()
    
    @property
    def forwarded_ports(self) -> List[int]:
        return self._config.get("forwarded_ports", [])
    
    @forwarded_ports.setter
    def forwarded_ports(self, value: List[int]) -> None:
        self._config["forwarded_ports"] = value
        self._save()
    
    @property
    def tunnel_id(self) -> int:
        """Get tunnel_id, falling back to role default if not set."""
        val = self._config.get("tunnel_id")
        if val is not None:
            return val
        role = self.role
        if role and role in self.ROLE_TUNNEL_DEFAULTS:
            return self.ROLE_TUNNEL_DEFAULTS[role]["tunnel_id"]
        return 1000  # Ultimate fallback
    
    @tunnel_id.setter
    def tunnel_id(self, value: int) -> None:
        self._config["tunnel_id"] = value
        self._save()
    
    @property
    def peer_tunnel_id(self) -> int:
        """Get peer_tunnel_id, falling back to role default if not set."""
        val = self._config.get("peer_tunnel_id")
        if val is not None:
            return val
        role = self.role
        if role and role in self.ROLE_TUNNEL_DEFAULTS:
            return self.ROLE_TUNNEL_DEFAULTS[role]["peer_tunnel_id"]
        return 2000  # Ultimate fallback
    
    @peer_tunnel_id.setter
    def peer_tunnel_id(self, value: int) -> None:
        self._config["peer_tunnel_id"] = value
        self._save()
    
    @property
    def session_id(self) -> int:
        """Get session_id, falling back to role default if not set."""
        val = self._config.get("session_id")
        if val is not None:
            return val
        role = self.role
        if role and role in self.ROLE_TUNNEL_DEFAULTS:
            return self.ROLE_TUNNEL_DEFAULTS[role]["session_id"]
        return 10  # Ultimate fallback
    
    @session_id.setter
    def session_id(self, value: int) -> None:
        self._config["session_id"] = value
        self._save()
    
    @property
    def peer_session_id(self) -> int:
        """Get peer_session_id, falling back to role default if not set."""
        val = self._config.get("peer_session_id")
        if val is not None:
            return val
        role = self.role
        if role and role in self.ROLE_TUNNEL_DEFAULTS:
            return self.ROLE_TUNNEL_DEFAULTS[role]["peer_session_id"]
        return 20  # Ultimate fallback
    
    @peer_session_id.setter
    def peer_session_id(self, value: int) -> None:
        self._config["peer_session_id"] = value
        self._save()
    
    def get_tunnel_ids(self) -> Dict[str, int]:
        """Get all tunnel IDs as a dictionary."""
        return {
            "tunnel_id": self.tunnel_id,
            "peer_tunnel_id": self.peer_tunnel_id,
            "session_id": self.session_id,
            "peer_session_id": self.peer_session_id,
        }
    
    def add_port(self, port: int) -> None:
        """Add a port to forwarded ports list."""
        ports = self.forwarded_ports
        if port not in ports:
            ports.append(port)
            self.forwarded_ports = ports
    
    def remove_port(self, port: int) -> None:
        """Remove a port from forwarded ports list."""
        ports = self.forwarded_ports
        if port in ports:
            ports.remove(port)
            self.forwarded_ports = ports
    
    def clear_all(self) -> None:
        """Clear all configuration values (used when deleting tunnel)."""
        self._config["role"] = None
        self._config["ip_iran"] = None
        self._config["ip_kharej"] = None
        self._config["forwarded_ports"] = []
        self._save()
    
    def is_configured(self) -> bool:
        """Check if basic configuration is complete."""
        return bool(
            self.role and 
            self.ip_iran and 
            self.ip_kharej
        )
    
    def get_local_ip(self) -> Optional[str]:
        """Get local IP based on role."""
        if self.role == "IRAN":
            return self.ip_iran
        elif self.role == "KHAREJ":
            return self.ip_kharej
        return None
    
    def get_remote_ip(self) -> Optional[str]:
        """Get remote IP based on role."""
        if self.role == "IRAN":
            return self.ip_kharej
        elif self.role == "KHAREJ":
            return self.ip_iran
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
