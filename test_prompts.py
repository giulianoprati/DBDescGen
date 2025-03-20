from openrouter_llm import OpenRouterLLM
from llama_index.core.llms import ChatMessage
import logging
from default_prompts import (
    DEFAULT_COLUMN_DESC_GEN_CHINESE_PROMPT,
    DEFAULT_TABLE_DESC_GEN_CHINESE_PROMPT
)

def test_description_prompts():
    """Test dei prompt per la generazione delle descrizioni."""
    
    # Configura logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("PromptTest")
    
    try:
        # Inizializza il client
        llm = OpenRouterLLM()
        
        # Test prompt descrizione colonna
        logger.info("\nTest prompt descrizione colonna...")
        test_column_prompt = DEFAULT_COLUMN_DESC_GEN_CHINESE_PROMPT.format(
            table_mschema="""
            Table: users
            Fields:
              - id_utente (INTEGER): Primary key
              - username (VARCHAR): User login name
              - email (VARCHAR): User email address
            """,
            sql="SELECT * FROM users LIMIT 5;",
            sql_res="""
            | id_utente | username | email |
            |-----------|----------|-------|
            | 1 | john.doe | john@example.com |
            | 2 | jane.smith | jane@example.com |
            """,
            field_name="username",
            field_info_str="""
            Field Name: username
            Field Type: VARCHAR(32)
            Is Primary Key: False
            Is Unique: False
            Is Nullable: True
            Examples: ['john.doe', 'jane.smith']
            """,
            supp_info="Field is used for user authentication"
        )
        
        column_response = llm.chat([ChatMessage(role="user", content=test_column_prompt)])
        logger.info(f"Risposta descrizione colonna: {column_response.message.content}")
        
        # Test prompt descrizione tabella
        logger.info("\nTest prompt descrizione tabella...")
        test_table_prompt = DEFAULT_TABLE_DESC_GEN_CHINESE_PROMPT.format(
            table_name="users",
            table_mschema="""
            Table: users
            Fields:
              - id_utente (INTEGER): Primary key
              - username (VARCHAR): User login name
              - email (VARCHAR): User email address
            """,
            sql="SELECT * FROM users LIMIT 5;",
            sql_res="""
            | id_utente | username | email |
            |-----------|----------|-------|
            | 1 | john.doe | john@example.com |
            | 2 | jane.smith | jane@example.com |
            """
        )
        
        table_response = llm.chat([ChatMessage(role="user", content=test_table_prompt)])
        logger.info(f"Risposta descrizione tabella: {table_response.message.content}")
        
        return True
        
    except Exception as e:
        logger.error(f"Errore durante il test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test Prompt Descrizioni ===")
    success = test_description_prompts()
    print("\n✓ Test completato" if success else "\n✗ Test fallito")