"""
API Key Management for SkyTrail Desktop
Supports Nemotron (NVIDIA) API keys with secure local storage
"""

import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class APIKeyManager:
    """Secure API key storage and management"""
    
    def __init__(self):
        self.app_dir = Path(os.path.expanduser("~/.skytrail"))
        self.app_dir.mkdir(exist_ok=True)
        self.keys_file = self.app_dir / "api_keys.json"
        self.master_key_file = self.app_dir / ".master.key"
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize encryption for secure storage"""
        if not self.master_key_file.exists():
            # Generate a new master key
            key = Fernet.generate_key()
            with open(self.master_key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.master_key_file, 0o600)  # Read/write for owner only
        else:
            with open(self.master_key_file, 'rb') as f:
                key = f.read()
        self.cipher = Fernet(key)
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def save_key(self, service: str, api_key: str):
        """Save API key for a service"""
        if not api_key or len(api_key.strip()) < 10:
            raise ValueError("Invalid API key format")
        
        # Load existing keys
        keys = self._load_keys()
        
        # Encrypt and save
        encrypted_key = self._encrypt(api_key)
        keys[service] = encrypted_key
        
        # Save to file
        with open(self.keys_file, 'w') as f:
            json.dump(keys, f, indent=2)
        os.chmod(self.keys_file, 0o600)
        
        return True
    
    def get_key(self, service: str) -> str:
        """Retrieve API key for a service"""
        keys = self._load_keys()
        if service not in keys:
            return None
        try:
            return self._decrypt(keys[service])
        except:
            return None
    
    def delete_key(self, service: str):
        """Delete API key for a service"""
        keys = self._load_keys()
        if service in keys:
            del keys[service]
            with open(self.keys_file, 'w') as f:
                json.dump(keys, f, indent=2)
            return True
        return False
    
    def _load_keys(self) -> dict:
        """Load keys from file"""
        if not self.keys_file.exists():
            return {}
        try:
            with open(self.keys_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def has_key(self, service: str) -> bool:
        """Check if a service has an API key"""
        return self.get_key(service) is not None
    
    def get_nemotron_key(self) -> str:
        """Get Nemotron API key specifically"""
        return self.get_key("nemotron")
    
    def save_nemotron_key(self, api_key: str):
        """Save Nemotron API key"""
        return self.save_key("nemotron", api_key)
    
    def delete_nemotron_key(self):
        """Delete Nemotron API key"""
        return self.delete_key("nemotron")

# Singleton instance
key_manager = APIKeyManager()