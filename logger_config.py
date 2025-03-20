import logging
import sys
from pathlib import Path

def setup_logger(log_file: str = "dbdescgen.log"):
    """
    Configura il logger per salvare l'output sia su file che su console.
    
    Args:
        log_file: Nome del file di log
    """
    # Crea la directory logs se non esiste
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file
    
    # Configurazione logger
    logger = logging.getLogger("DBDescGen")
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler per il file
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler per la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger