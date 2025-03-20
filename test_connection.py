from database import create_db_engine
from sqlalchemy import text
import sys

def test_connection():
    """Test della connessione al database e funzionalità base"""
    try:
        print("Inizializzazione connessione al database...")
        engine = create_db_engine()
        
        print("\nTest #1: Verifica connessione base")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Connessione stabilita con successo")
            
        print("\nTest #2: Verifica versione PostgreSQL")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✓ Versione PostgreSQL: {version}")
            
        print("\nTest #3: Elenco schemi disponibili")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            """))
            schemas = [row[0] for row in result]
            print("✓ Schemi trovati:")
            for schema in schemas:
                print(f"  - {schema}")
            
        print("\nTest #4: Elenco tabelle nello schema pubblico")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """))
            tables = [row[0] for row in result]
            print("✓ Tabelle trovate:")
            for table in tables:
                print(f"  - {table}")
                
        print("\nTest #5: Verifica privilegi utente")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT grantee, privilege_type, table_schema, table_name
                FROM information_schema.table_privileges 
                WHERE grantee = current_user
                AND table_schema = 'public'
                LIMIT 5
            """))
            privileges = [row for row in result]
            print("✓ Privilegi dell'utente (primi 5):")
            for priv in privileges:
                print(f"  - {priv[0]} ha {priv[1]} su {priv[2]}.{priv[3]}")
        
        print("\n✅ Tutti i test completati con successo!")
        return True
        
    except Exception as e:
        print(f"\n❌ Errore durante il test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test Connessione Database ===\n")
    success = test_connection()
    sys.exit(0 if success else 1)