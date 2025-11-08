"""
User repository for Cosmos DB operations (MongoDB API)
"""
import uuid
from datetime import datetime
from typing import Optional
from pymongo.errors import DuplicateKeyError
from .cosmos_client import cosmos_client
from .models import UserCreate, UserInDB, User
from .security import get_password_hash

class UserRepository:
    def __init__(self):
        self.collection = None
    
    def initialize(self):
        """Initialize the repository with Cosmos DB collection"""
        self.collection = cosmos_client.get_users_collection()
    
    async def create_user(self, user: UserCreate) -> Optional[UserInDB]:
        """Create a new user in Cosmos DB"""
        if self.collection is None:
            self.initialize()
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(user.email)
        if existing_user:
            return None
        
        # Create user document
        user_id = str(uuid.uuid4())
        user_doc = {
            "_id": user_id,
            "id": user_id,
            "email": user.email,
            "name": user.name,
            "hashed_password": get_password_hash(user.password),
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "is_active": True
        }
        
        try:
            self.collection.insert_one(user_doc)
            return UserInDB(**user_doc)
        except DuplicateKeyError:
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email from Cosmos DB"""
        if self.collection is None:
            self.initialize()
        
        try:
            user_doc = self.collection.find_one({"email": email})
            
            if user_doc:
                # MongoDB returns _id, ensure we have id field
                if "id" not in user_doc and "_id" in user_doc:
                    user_doc["id"] = str(user_doc["_id"])
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def update_last_login(self, email: str) -> bool:
        """Update user's last login timestamp"""
        if self.collection is None:
            self.initialize()
        
        try:
            result = self.collection.update_one(
                {"email": email},
                {"$set": {"last_login": datetime.utcnow().isoformat()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str, email: str) -> Optional[User]:
        """Get user by ID from Cosmos DB"""
        if self.collection is None:
            self.initialize()
        
        try:
            user_doc = self.collection.find_one({"id": user_id, "email": email})
            
            if user_doc:
                # MongoDB returns _id, ensure we have id field
                if "id" not in user_doc and "_id" in user_doc:
                    user_doc["id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

# Global repository instance
user_repository = UserRepository()
