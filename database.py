"""
MongoDB database connection and operations
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDB:
    client: MongoClient = None
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(settings.mongodb_url)
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[settings.database_name]
            self.collection = self.db[settings.collection_name]
            
            logger.info(f"Successfully connected to MongoDB database: {settings.database_name}")
            logger.info(f"Using collection: {settings.collection_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def insert_evaluation(self, evaluation_data: dict):
        """Insert evaluation data into MongoDB"""
        try:
            result = self.collection.insert_one(evaluation_data)
            logger.info(f"Evaluation inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting evaluation: {e}")
            raise


# Global database instance
mongodb = MongoDB()