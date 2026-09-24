import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================

# No Render, esta variável receberá a URL
# do PostgreSQL.
#
# No Codespaces/local, se DATABASE_URL não
# existir, continuará usando o SQLite atual.

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./devshowcase.db"
)


# ==========================================
# COMPATIBILIDADE COM POSTGRESQL
# ==========================================

# Alguns serviços podem fornecer a URL antiga
# começando com postgres://
# SQLAlchemy utiliza postgresql://

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# ==========================================
# ENGINE
# ==========================================

if DATABASE_URL.startswith("sqlite"):

    # Configuração para SQLite
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False
        }
    )

else:

    # Configuração para PostgreSQL
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


# ==========================================
# SESSÃO
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# BASE DOS MODELOS
# ==========================================

Base = declarative_base()


# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()