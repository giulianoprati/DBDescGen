from openrouter_llm import OpenRouterLLM
from llama_index.core.llms import ChatMessage
import logging

def test_openrouter():
    """Test della connessione a OpenRouter con un prompt semplice."""
    
    # Configura logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Inizializza il client
        llm = OpenRouterLLM()
        
        # Crea un messaggio di test semplice
        messages = [
            ChatMessage(
                role="user",
                content="Rispondi con una sola parola: ciao"
            )
        ]
        
        print("\nInvio richiesta di test a OpenRouter...")
        response = llm.chat(messages)
        
        print(f"\nRisposta ricevuta: {response.message.content}")
        return True
        
    except Exception as e:
        print(f"\nErrore durante il test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Test OpenRouter ===")
    success = test_openrouter()
    print("\n✓ Test completato" if success else "\n✗ Test fallito")