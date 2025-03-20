"""Script per riprovare la generazione dello schema da un checkpoint."""
import logging
from schema_engine import SchemaEngine
from database import create_db_engine
from openrouter_llm import OpenRouterLLM
from checkpoint_manager import CheckpointManager

def main():
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/schema_gen.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("SchemaGen")
    
    try:
        logger.info("Inizializzazione componenti...")
        
        # Inizializza checkpoint manager
        checkpoint_mgr = CheckpointManager()
        checkpoint = checkpoint_mgr.load_checkpoint()
        
        # Inizializza LLM
        llm = OpenRouterLLM(requests_per_minute=20)  # Rate limit più conservativo
        
        # Crea connessione database
        db_engine = create_db_engine()
        
        # Inizializza schema engine
        schema_engine = SchemaEngine(
            db_engine,
            llm=llm,
            db_name='timetable2',
            comment_mode='merge'
        )
        
        logger.info("Avvio generazione descrizioni...")
        
        if checkpoint:
            logger.info(f"Ripresa da checkpoint: {len(checkpoint)} tabelle processate")
            # TODO: Implementare ripresa da checkpoint
        
        # Genera descrizioni
        schema_engine.table_and_column_desc_generation()
        
        # Salva schema
        output_file = './timetable2_schema.json'
        schema_engine.mschema.save(output_file)
        logger.info(f"Schema salvato in: {output_file}")
        
        logger.info("Processo completato con successo!")
        return True
        
    except Exception as e:
        logger.error(f"Errore durante la generazione: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)