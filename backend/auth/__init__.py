"""
Authentication module initialization - using clean v2 files
"""
from .routes_v2 import router as auth_router
from .repository_v2 import user_repository

__all__ = ["auth_router", "user_repository"]

