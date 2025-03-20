from typing import Optional
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def get_database_url() -> str:
    """
    Costruisce l'URL di connessione al database dai parametri nel file .env
    """
    load_dotenv()
    
    db_type = os.getenv('DB_TYPE', 'postgresql')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Mancano alcuni parametri di configurazione del database nel file .env")
    
    return f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def create_db_engine(database_url: Optional[str] = None) -> Engine:
    """
    Crea e restituisce un'istanza del database engine
    
    Args:
        database_url: URL di connessione opzionale. Se non fornito, usa i parametri dal file .env
        
    Returns:
        SQLAlchemy Engine instance
    """
    if database_url is None:
        database_url = get_database_url()
        
    return create_engine(database_url)

# Esempio di utilizzo
if __name__ == "__main__":
    # Crea l'engine usando i parametri dal file .env
    engine = create_db_engine()
    
    # Test della connessione
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("Connessione al database riuscita!")