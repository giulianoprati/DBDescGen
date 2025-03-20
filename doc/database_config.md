# Configurazione del Database

## Panoramica
XiYan-DBDescGen supporta la connessione a diversi tipi di database SQL attraverso SQLAlchemy. La configurazione può essere gestita tramite variabili d'ambiente nel file `.env`.

## Configurazione tramite .env

### Parametri Richiesti
```plaintext
# Database Configuration
DB_TYPE=postgresql    # postgresql, mysql, o sqlite
DB_HOST=192.168.1.89
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### URL di Connessione
Il formato dell'URL di connessione viene generato automaticamente:
- PostgreSQL: `postgresql://user:password@host:port/dbname`
- MySQL: `mysql://user:password@host:port/dbname`
- SQLite: `sqlite:///path/to/database.db`

## Utilizzo

### Metodo Base
```python
from database import create_db_engine

# Crea l'engine usando i parametri dal file .env
engine = create_db_engine()

# Inizializza SchemaEngine
schema_engine = SchemaEngine(
    engine, 
    llm=llm,
    db_name='your_db_name'
)
```

### Connessione Manuale
Se preferisci specificare l'URL di connessione manualmente:
```python
from database import create_db_engine

# Specifica l'URL di connessione direttamente
database_url = "postgresql://user:password@host:port/dbname"
engine = create_db_engine(database_url)
```

## Test della Connessione
Puoi testare la connessione al database eseguendo direttamente il modulo database.py:
```bash
python database.py
```

Se la connessione è riuscita, vedrai il messaggio "Connessione al database riuscita!"

## Risoluzione dei Problemi

### Errori Comuni
1. **Parametri Mancanti**
   ```
   ValueError: Mancano alcuni parametri di configurazione del database nel file .env
   ```
   Soluzione: Verifica che tutti i parametri richiesti siano presenti nel file .env

2. **Errore di Connessione**
   ```
   OperationalError: (psycopg2.OperationalError) could not connect to server
   ```
   Possibili soluzioni:
   - Verifica che l'host sia raggiungibile
   - Controlla che le credenziali siano corrette
   - Verifica che il database esista
   - Controlla che il firewall permetta la connessione

3. **Permessi Insufficienti**
   ```
   OperationalError: permission denied for database
   ```
   Soluzione: Verifica che l'utente abbia i permessi necessari per accedere al database

## Note sulla Sicurezza
- Non committare mai il file `.env` nel controllo versione
- Usa `.env.example` come template per la configurazione
- Limita i permessi dell'utente del database al minimo necessario
- Considera l'uso di un vault per le credenziali in produzione