"""
Authentication module initialization
"""
from .routes import router as auth_router
from .cosmos_client import cosmos_client
from .repository import user_repository

__all__ = ["auth_router", "cosmos_client", "user_repository"]
