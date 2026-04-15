"""
Configurações para diferentes ambientes do Conversor de Arquivos AM.
"""

import os
from typing import Dict, Any

class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get("FLASK_SECRET", "dev-secret")
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    PER_FILE_LIMIT_MB = 50
    PER_FILE_LIMIT = PER_FILE_LIMIT_MB * 1024 * 1024

    # Diretórios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento local."""
    DEBUG = True
    HOST = "0.0.0.0"
    PORT = 5000

    # Diretórios locais
    UPLOAD_FOLDER = os.path.join(Config.BASE_DIR, "uploads")
    EXPORTS_DIR = os.path.join(Config.BASE_DIR, "exports")

class ProductionConfig(Config):
    """Configuração para ambiente de produção."""
    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 5000))

    # Diretórios de produção (persistentes dentro do container)
    UPLOAD_FOLDER = os.path.join(Config.BASE_DIR, "uploads")
    EXPORTS_DIR = os.path.join(Config.BASE_DIR, "exports")

class RDSConfig(Config):
    """Configuração para ambiente RDS (farm de máquinas)."""

    DEBUG = False
    HOST = "0.0.0.0"
    PORT = int(os.environ.get("PORT", 8000))

    # Diretórios compartilhados no RDS
    UPLOAD_FOLDER = "/rds/shared/uploads"
    EXPORTS_DIR = "/rds/shared/exports"
    LOG_DIR = "/rds/shared/logs"

    # Configurações de segurança RDS
    SECRET_KEY = os.environ.get("FLASK_SECRET")
    # Validação será feita no método get_config se necessário

    # Limites mais altos para infraestrutura robusta
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2GB
    PER_FILE_LIMIT_MB = 500  # 500MB por arquivo
    PER_FILE_LIMIT = PER_FILE_LIMIT_MB * 1024 * 1024

    # Configurações de logging
    LOG_LEVEL = "INFO"
    LOG_FILE = os.path.join(LOG_DIR, "conversor_am.log")

class DataCenterConfig(RDSConfig):
    """Configuração específica para data center."""

    # Múltiplos servidores
    SERVER_ID = os.environ.get("SERVER_ID", "server-01")

    # Load balancer
    LOAD_BALANCER_URL = os.environ.get("LOAD_BALANCER_URL")

    # Database para auditoria (futuro)
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = int(os.environ.get("DB_PORT", 5432))
    DB_NAME = os.environ.get("DB_NAME", "conversor_am")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

# Mapeamento de configurações
config_map: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
    "rds": RDSConfig,
    "datacenter": DataCenterConfig,
}

def get_config(env: str = None) -> Config:
    """Retorna configuração baseada no ambiente."""
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")

    config_class = config_map.get(env.lower())
    if not config_class:
        raise ValueError(f"Ambiente desconhecido: {env}")

    config_instance = config_class()

    # Validações específicas por ambiente
    if isinstance(config_instance, RDSConfig) and not config_instance.SECRET_KEY:
        raise ValueError("FLASK_SECRET environment variable required in RDS environment")

    return config_instance

# Exemplo de uso:
# from config import get_config
# config = get_config("rds")
# app.config.from_object(config)