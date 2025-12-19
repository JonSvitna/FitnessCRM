"""
AI Orchestrator Configuration Settings
"""
import os
from typing import Optional


class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database (Shared with main app)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    
    # LangChain
    LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
    
    # Main App Integration
    MAIN_APP_URL = os.getenv('MAIN_APP_URL', 'http://localhost:5000')
    MAIN_APP_API_KEY = os.getenv('MAIN_APP_API_KEY')
    
    # Agent Features
    ENABLE_SELF_HEALING = os.getenv('ENABLE_SELF_HEALING', 'true').lower() == 'true'
    ENABLE_CODE_MONITORING = os.getenv('ENABLE_CODE_MONITORING', 'true').lower() == 'true'
    ENABLE_WORKOUT_OPTIMIZATION = os.getenv('ENABLE_WORKOUT_OPTIMIZATION', 'true').lower() == 'true'
    ENABLE_PROGRESS_MONITORING = os.getenv('ENABLE_PROGRESS_MONITORING', 'true').lower() == 'true'
    ENABLE_SCHEDULING_INTELLIGENCE = os.getenv('ENABLE_SCHEDULING_INTELLIGENCE', 'true').lower() == 'true'
    
    # Monitoring
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
