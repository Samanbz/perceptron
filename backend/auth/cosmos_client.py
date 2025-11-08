"""
Azure Cosmos DB client configuration (MongoDB API)
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

load_dotenv()

class CosmosDBClient:
    def __init__(self):
        self.connection_string = os.getenv("COSMOS_CONNECTION_STRING")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME", "perceptron")
        self.users_collection_name = os.getenv("COSMOS_USERS_COLLECTION", "users")
        
        self.client = None
        self.database = None
        self.users_collection = None
        
    def connect(self):
        """Initialize connection to Cosmos DB using MongoDB API"""
        try:
            # Create MongoDB client
            self.client = MongoClient(self.connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[self.database_name]
            
            # Get users collection
            self.users_collection = self.database[self.users_collection_name]
            
            # Create index on email for faster queries
            self.users_collection.create_index("email", unique=True)
            
            print(f"✅ Connected to Cosmos DB (MongoDB API): {self.database_name}")
            return True
            
        except (ConnectionFailure, OperationFailure) as e:
            print(f"❌ Failed to connect to Cosmos DB: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to Cosmos DB: {e}")
            return False
    
    def get_users_collection(self):
        """Get users collection"""
        return self.users_collection

# Global instance
cosmos_client = CosmosDBClient()
