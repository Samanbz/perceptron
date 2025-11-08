"""
Setup script for Azure Cosmos DB (MongoDB API)
Run this script to initialize your Cosmos DB database and collection
"""
import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.cosmos_client import cosmos_client

def setup_cosmos_db():
    """Initialize Cosmos DB database and collections"""
    print("🔧 Setting up Azure Cosmos DB (MongoDB API)...")
    print("-" * 50)
    
    # Load environment variables
    load_dotenv()
    
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    database_name = os.getenv("COSMOS_DATABASE_NAME", "perceptron")
    
    if not connection_string or connection_string == "":
        print("❌ Error: Please configure your Cosmos DB connection string in .env file")
        print("\nUpdate the following variable in backend/.env:")
        print("  - COSMOS_CONNECTION_STRING")
        return False
    
    # Connect to Cosmos DB
    success = cosmos_client.connect()
    
    if success:
        print("\n✅ Cosmos DB setup completed successfully!")
        print(f"   Database: {database_name}")
        print(f"   Collections: users")
        print("\nYou can now start the FastAPI server.")
        return True
    else:
        print("\n❌ Failed to setup Cosmos DB")
        print("   Please check your connection string and try again.")
        return False

if __name__ == "__main__":
    setup_cosmos_db()
