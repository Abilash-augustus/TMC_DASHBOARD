# config.py

import os
from typing import Dict, Any, Optional
import json

class Config:
    """Configuration manager for TMC API application."""
    
    def __init__(self, config_file: str = "tmc_config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file if it exists.
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._get_default_config()
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "base_url": "https://api.us-west.cloud.talend.com/tmc/v2.6",
            "engines": {
                "REMOTE_ENGINE_CLUSTER": "60648f88dd425803e84ad87b",
                "REMOTE_ENGINE": "606adda8f104ab77c2ecb751"
            },
            "recent_tokens": [],
            "recent_workspaces": []
        }
    
    def save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Failed to save configuration: {e}")
    
    def get_base_url(self) -> str:
        """
        Get the base URL for the TMC API.
        
        Returns:
            Base URL string
        """
        return self.config.get("base_url", "https://api.us-west.cloud.talend.com/tmc/v2.6")
    
    def get_engines(self) -> Dict[str, str]:
        """
        Get available engines.
        
        Returns:
            Dictionary of engine types and IDs
        """
        return self.config.get("engines", {})
    
    def get_recent_tokens(self) -> list:
        """
        Get recently used tokens (masked).
        
        Returns:
            List of recent tokens
        """
        return self.config.get("recent_tokens", [])
    
    def add_recent_token(self, token: str) -> None:
        """
        Add a token to the recent tokens list.
        
        Args:
            token: Authentication token
        """
        # Store only a masked version of the token for security
        masked_token = token[:5] + "..." + token[-5:]
        
        recent_tokens = self.get_recent_tokens()
        if masked_token in recent_tokens:
            recent_tokens.remove(masked_token)
        
        recent_tokens.insert(0, masked_token)
        
        # Keep only the 5 most recent tokens
        self.config["recent_tokens"] = recent_tokens[:5]
        self.save_config()
    
    def add_recent_workspace(self, workspace_id: str, workspace_name: str, 
                            environment_id: str, environment_name: str) -> None:
        """
        Add a workspace to the recent workspaces list.
        
        Args:
            workspace_id: ID of the workspace
            workspace_name: Name of the workspace
            environment_id: ID of the environment
            environment_name: Name of the environment
        """
        workspace_info = {
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "environment_id": environment_id,
            "environment_name": environment_name
        }
        
        recent_workspaces = self.config.get("recent_workspaces", [])
        
        # Remove if already exists
        recent_workspaces = [w for w in recent_workspaces 
                           if not (w["workspace_id"] == workspace_id and 
                                  w["environment_id"] == environment_id)]
        
        # Add to the beginning
        recent_workspaces.insert(0, workspace_info)
        
        # Keep only the 5 most recent workspaces
        self.config["recent_workspaces"] = recent_workspaces[:5]
        self.save_config()
    
    def get_recent_workspaces(self) -> list:
        """
        Get recently used workspaces.
        
        Returns:
            List of recent workspace information
        """
        return self.config.get("recent_workspaces", [])
