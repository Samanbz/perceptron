"""
Simple user repository - just Cosmos DB operations
"""
from typing import Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os

from .security_v2 import hash_password
from .models import UserInDB


class UserRepository:
    def __init__(self):
        """Initialize connection to Cosmos DB"""
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to Cosmos DB MongoDB API"""
        # Load from .env file
        from dotenv import load_dotenv
        load_dotenv()
        
        connection_string = os.getenv("COSMOS_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("COSMOS_CONNECTION_STRING not found in environment variables")
        
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client["futurydb"]
            self.collection = self.db["users"]
            print("✅ Connected to Cosmos DB")
        except Exception as e:
            print(f"❌ Failed to connect to Cosmos DB: {e}")
            raise
    
    def create_user(self, email: str, password: str, full_name: str) -> UserInDB:
        """Create new user"""
        user_dict = {
            "email": email,
            "hashed_password": hash_password(password),
            "full_name": full_name,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        try:
            result = self.collection.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
            return UserInDB(**user_dict)
        except DuplicateKeyError:
            raise ValueError("Email already registered")
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_dict = self.collection.find_one({"email": email})
        if user_dict:
            return UserInDB(**user_dict)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        from bson import ObjectId
        user_dict = self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            return UserInDB(**user_dict)
        return None
    
    def update_last_login(self, email: str):
        """Update user's last login timestamp"""
        self.collection.update_one(
            {"email": email},
            {"$set": {"last_login": datetime.utcnow()}}
        )


# Global instance
user_repository = UserRepository()
