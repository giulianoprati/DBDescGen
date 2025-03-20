from database import create_db_engine
from openrouter_llm import OpenRouterLLM
from schema_engine import SchemaEngine
from checkpoint_manager import CheckpointManager
from logger_config import setup_logger
from tqdm import tqdm
import signal
import sys
import time
import logging

# Flag per gestire l'interruzione
stop_processing = False

def signal_handler(signum, frame):
    """Gestisce l'interruzione del processo."""
    global stop_processing
    if not stop_processing:
        print("\n⚠️ Richiesta interruzione. Completamento dell'operazione corrente...")
        stop_processing = True
    else:
        print("\n⚠️ Forzatura interruzione...")
        sys.exit(1)

def main():
    logger = None
    try:
        # Configura logging e gestione interruzioni
        logger = setup_logger()
        signal.signal(signal.SIGINT, signal_handler)
        
        # Inizializza checkpoint manager
        checkpoint_mgr = CheckpointManager()
        
        print("\n=== XiYan-DBDescGen: Generazione Descrizioni Database ===\n")
        
        # Inizializza il client OpenRouter (carica configurazione da .env)
        print("1. Inizializzazione OpenRouter LLM...")
        llm = OpenRouterLLM()
        print("✓ LLM inizializzato")
        
        # Crea la connessione al database (carica configurazione da .env)
        print("\n2. Connessione al database...")
        db_engine = create_db_engine()
        print("✓ Connessione stabilita")
        
        # Inizializza e configura lo SchemaEngine
        print("\n3. Configurazione SchemaEngine...")
        schema_engine = SchemaEngine(
            db_engine,
            llm=llm,
            db_name='timetable2',
            comment_mode='merge'  # 'generation', 'merge', 'origin', o 'no_comment'
        )
        print("✓ SchemaEngine configurato")
        
        # Analisi dei campi
        print("\n4. Analisi dei campi...")
        total_tables = len(schema_engine._usable_tables)
        
        # Carica l'ultimo checkpoint
        checkpoint = checkpoint_mgr.load_checkpoint()
        if checkpoint:
            print(f"ℹ️ Ripresa da checkpoint: {len(checkpoint)} tabelle già processate")
        
        for i, table_name in enumerate(schema_engine._usable_tables, 1):
            if stop_processing:
                print("\n🛑 Interruzione richiesta. Salvataggio stato corrente...")
                break
                
            print(f"\nProcesso tabella {i}/{total_tables}: {table_name}")
            fields = schema_engine._mschema.tables[table_name]['fields']
            
            for field_name in tqdm(fields.keys(), desc="Campi analizzati"):
                if stop_processing:
                    break
                    
                # Salta i campi già processati
                if checkpoint_mgr.is_field_processed(table_name, field_name):
                    continue
                    
                print(f"\n  - Analisi campo: {field_name}")
                try:
                    field_info = schema_engine.get_single_field_info_str(table_name, field_name)
                    print(f"    Tipo: {fields[field_name].get('type', 'N/A')}")
                    
                    # Salva il checkpoint dopo ogni campo
                    checkpoint_mgr.save_checkpoint(
                        table_name, 
                        field_name, 
                        {
                            "type": fields[field_name].get('type', ''),
                            "info": field_info
                        }
                    )
                except Exception as e:
                    if logger:
                        logger.error(f"Errore nell'analisi del campo {table_name}.{field_name}: {str(e)}")
                    else:
                        print(f"Errore nell'analisi del campo {table_name}.{field_name}: {str(e)}")
                    continue
                
                time.sleep(0.1)  # Breve pausa per leggibilità
        
        if not stop_processing:
            # Generazione descrizioni
            print("\n5. Generazione descrizioni...")
            schema_engine.table_and_column_desc_generation()
            
            # Salva lo schema generato
            print("\n6. Salvataggio schema...")
            mschema = schema_engine.mschema
            output_file = './timetable2_schema.json'
            mschema.save(output_file)
            print(f"✓ Schema salvato in: {output_file}")
            
            # Stampa lo schema in formato leggibile
            print("\n7. Schema generato:")
            print(mschema.to_mschema())
            
            print("\n✅ Processo completato con successo!")
        else:
            print("\n⏸️ Processo interrotto. Lo stato è stato salvato nei checkpoint.")
        
    except Exception as e:
        error_msg = f"Errore durante l'esecuzione: {str(e)}"
        if logger:
            logger.error(error_msg)
        else:
            print(f"\n❌ {error_msg}")
        raise

if __name__ == "__main__":
    main()