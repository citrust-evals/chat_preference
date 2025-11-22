"""
Configuration settings for the LLM Evaluation API
"""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    # MongoDB Configuration

    mongodb_url: str
    database_name: str = "citrust"
    collection_name: str = "evaluations"
    
    # API Configuration
    app_name: str = "LLM Evaluation API"
    app_version: str = "1.0.0"
    
    gemini_api_key: str 

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()