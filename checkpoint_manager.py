# Funzione: Gestisce i checkpoint durante l'analisi del database.
# Il checkpoint è un file JSON che memorizza i campi già processati durante l'analisi del database.
# Questo permette di riprendere l'analisi da dove si era interrotta in caso di interruzione del processo.



import json
from pathlib import Path
from typing import Dict, Any
import logging

class CheckpointManager:
    """Gestisce i checkpoint durante l'analisi del database."""
    
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.current_checkpoint = {}
        
    def save_checkpoint(self, table_name: str, field_name: str, data: Dict[str, Any]):
        """Salva un checkpoint per una specifica tabella e campo."""
        try:
            checkpoint_file = self.checkpoint_dir / "analysis_checkpoint.json"
            
            # Carica checkpoint esistente se presente
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    self.current_checkpoint = json.load(f)
            
            # Aggiorna il checkpoint
            if table_name not in self.current_checkpoint:
                self.current_checkpoint[table_name] = {}
            self.current_checkpoint[table_name][field_name] = data
            
            # Salva il checkpoint aggiornato
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_checkpoint, f, indent=2)
                
            logging.debug(f"Checkpoint salvato per {table_name}.{field_name}")
            
        except Exception as e:
            logging.error(f"Errore nel salvataggio del checkpoint: {str(e)}")
    
    def load_checkpoint(self) -> Dict[str, Any]:
        """Carica l'ultimo checkpoint salvato."""
        try:
            checkpoint_file = self.checkpoint_dir / "analysis_checkpoint.json"
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    self.current_checkpoint = json.load(f)
                logging.info(f"Checkpoint caricato: {len(self.current_checkpoint)} tabelle")
            return self.current_checkpoint
        except Exception as e:
            logging.error(f"Errore nel caricamento del checkpoint: {str(e)}")
            return {}
    
    def is_field_processed(self, table_name: str, field_name: str) -> bool:
        """Verifica se un campo è già stato processato."""
        return (table_name in self.current_checkpoint and 
                field_name in self.current_checkpoint[table_name])
    
    def get_progress(self) -> tuple:
        """Restituisce il progresso corrente."""
        total_tables = len(self.current_checkpoint)
        total_fields = sum(len(fields) for fields in self.current_checkpoint.values())
        return total_tables, total_fields