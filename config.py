"""
Configuration settings for the LLM Evaluation API
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB Configuration
    mongodb_url: str = "mongodb+srv://dayal700007:1Knarn5D8gQQ7cx4@kaotic.nzqedtt.mongodb.net/"
    database_name: str = "citrust"
    collection_name: str = "evaluations"
    
    # API Configuration
    app_name: str = "LLM Evaluation API"
    app_version: str = "1.0.0"
    
    gemini_api_key: str = "AIzaSyAu5Aq3qZhw_J1ocO-qhrhNACW1-Rxkf4Y"

    class Config:
        env_file = ".env"


settings = Settings()