# auth.py

import getpass
import hashlib
from typing import Optional, Tuple

class Auth:
    """Authentication manager for TMC API application."""
    
    def __init__(self, app_password: str = "youcantseeme"):
        """
        Initialize the authentication manager.
        
        Args:
            app_password: Password for accessing the application
        """
        # In a real application, this should be stored securely
        self.app_password_hash = self._hash_password(app_password)
        self.auth_token = None
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_app_password(self, password: str) -> bool:
        """
        Verify the application password.
        
        Args:
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        return self._hash_password(password) == self.app_password_hash
    
    def authenticate_app(self, max_attempts: int = 3) -> bool:
        """
        Authenticate the user to access the application.
        
        Args:
            max_attempts: Maximum number of password attempts
            
        Returns:
            True if authentication successful, False otherwise
        """
        attempts = 0
        
        while attempts < max_attempts:
            password = getpass.getpass("Enter password: ")
            
            if self.verify_app_password(password):
                print("Authentication successful. Starting the application...")
                return True
            else:
                attempts += 1
                remaining_attempts = max_attempts - attempts
                print(f"Authentication failed. {remaining_attempts} attempt(s) remaining.")
            
            if attempts >= max_attempts:
                print("Maximum attempts exceeded. Exiting application...")
                return False
        
        return False
    
    def set_auth_token(self, token: str) -> None:
        """
        Set the authentication token.
        
        Args:
            token: Authentication token
        """
        self.auth_token = token
    
    def get_auth_token(self) -> Optional[str]:
        """
        Get the current authentication token.
        
        Returns:
            Authentication token or None if not set
        """
        return self.auth_token
    
    def prompt_for_auth_token(self) -> str:
        """
        Prompt the user for an authentication token.
        
        Returns:
            Authentication token
        """
        token = input("Enter your authorization token: ")
        self.set_auth_token(token)
        return token
