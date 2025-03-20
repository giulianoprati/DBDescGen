from typing import Any, List, Mapping, Optional, Sequence, AsyncGenerator
import os
import json
import time
import random
import requests
import logging
import sys
from dotenv import load_dotenv
from llama_index.core.llms import (
    LLM,
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    LLMMetadata,
    CompletionResponseGen
)
from llama_index.core.base.response.schema import RESPONSE_TYPE

class OpenRouterError(Exception):
    """Errore personalizzato per OpenRouter."""
    pass

class OpenRouterLLM(LLM):
    """OpenRouter LLM implementation for XiYan-DBDescGen."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 5,
        initial_retry_delay: float = 1.0,
        max_retry_delay: float = 60.0,
        timeout: int = 30,
        requests_per_minute: int = 30
    ) -> None:
        """Initialize OpenRouter LLM."""
        super().__init__()
        load_dotenv()
        
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self._api_key:
            raise ValueError("OpenRouter API key not found. Set OPENROUTER_API_KEY in .env")
            
        self._model = model or os.getenv("OPENROUTER_MODEL", "mistral-7b-instruct")
        self._max_retries = int(os.getenv("OPENROUTER_MAX_RETRIES", max_retries))
        self._timeout = int(os.getenv("OPENROUTER_TIMEOUT", timeout))
        self._base_url = "https://openrouter.ai/api/v1"
        self._initial_retry_delay = initial_retry_delay
        self._max_retry_delay = max_retry_delay
        self._requests_per_minute = requests_per_minute
        self._last_request_time = 0
        
        # Configura logger
        self._logger = logging.getLogger("OpenRouterLLM")
        self._logger.setLevel(logging.DEBUG)
        
        if not self._logger.handlers:
            # Handler per il file con encoding UTF-8
            file_handler = logging.FileHandler('logs/openrouter.log', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)
            
            # Handler per la console con encoding UTF-8
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)

    def _wait_for_rate_limit(self):
        """Attende se necessario per rispettare il rate limit."""
        elapsed = time.time() - self._last_request_time
        min_interval = 60.0 / self._requests_per_minute
        
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            self._logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self._last_request_time = time.time()

    @property
    def _headers(self) -> dict:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://DBDescGen",
        }

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=4096,  # Può variare in base al modello
            num_output=1000,
            model_name=self._model
        )

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calcola il delay per il retry con exponential backoff."""
        delay = min(self._initial_retry_delay * (2 ** attempt), self._max_retry_delay)
        return delay + (0.1 * delay * (random.random() - 0.5))  # jitter ±5%

    def _make_request(
        self,
        messages: Sequence[ChatMessage],
        max_retries: Optional[int] = None,
        **kwargs: Any
    ) -> dict:
        """Make a request to OpenRouter API with improved retry logic."""
        max_retries = max_retries or self._max_retries
        formatted_messages = [
            {
                "role": msg.role,
                "content": msg.content if isinstance(msg.content, str) else str(msg.content)
            }
            for msg in messages
        ]
        
        payload = {
            "model": self._model,
            "messages": formatted_messages,
            "temperature": kwargs.get('temperature', 0.7),
            "max_tokens": kwargs.get('max_tokens', 1000)
        }
        
        self._logger.debug(f"Prepared request payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        last_error = None
        self._logger.info(f"Starting request to OpenRouter with {len(messages)} messages")
        
        for attempt in range(max_retries + 1):
            try:
                self._wait_for_rate_limit()
                
                if attempt > 0:
                    delay = self._calculate_retry_delay(attempt - 1)
                    self._logger.info(f"Retry attempt {attempt}/{max_retries}, waiting {delay:.2f}s")
                    time.sleep(delay)
                
                response = requests.post(
                    f"{self._base_url}/chat/completions",
                    headers=self._headers,
                    json=payload,
                    timeout=self._timeout
                )
                
                self._logger.debug(f"Response status: {response.status_code}")
                self._logger.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status_code == 429:  # Rate limit
                    retry_after = int(response.headers.get('Retry-After', 60))
                    self._logger.warning(f"Rate limited, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                try:
                    response_json = response.json()
                    self._logger.debug(f"Response body: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    self._logger.error(f"Invalid JSON response: {response.text}")
                    raise OpenRouterError("Invalid JSON response from API")
                
                response.raise_for_status()
                
                self._logger.info("Request successful")
                return response_json
                
            except requests.Timeout as e:
                last_error = f"Timeout error: {str(e)}"
                self._logger.warning(f"Request timeout on attempt {attempt + 1}/{max_retries}")
            
            except requests.RequestException as e:
                last_error = f"Request error: {str(e)}"
                self._logger.error(f"Request failed on attempt {attempt + 1}/{max_retries}: {str(e)}")
                
                if attempt == max_retries:
                    break
                    
                if response.status_code >= 500:
                    continue  # Retry server errors
                elif response.status_code == 401:
                    raise OpenRouterError("Invalid API key")
                elif response.status_code == 403:
                    raise OpenRouterError("API key lacks permission")
                elif response.status_code >= 400:
                    try:
                        error_json = response.json()
                        self._logger.error(f"API error response: {json.dumps(error_json, indent=2)}")
                    except:
                        self._logger.error(f"API error (raw): {response.text}")
                    raise OpenRouterError(f"API request failed: {str(e)}")
        
        raise OpenRouterError(f"Failed after {max_retries} retries. Last error: {last_error}")
                
    def complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponse:
        """Complete a prompt."""
        messages = [ChatMessage(role="user", content=prompt)]
        chat_response = self.chat(messages, **kwargs)
        return CompletionResponse(text=chat_response.message.content)

    def chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Chat with the LLM."""
        response_data = self._make_request(messages, **kwargs)
        
        if not response_data or "choices" not in response_data:
            raise OpenRouterError("Invalid response from OpenRouter API")
            
        message_content = response_data["choices"][0]["message"]["content"]
        role = response_data["choices"][0]["message"].get("role", "assistant")
        
        return ChatResponse(
            message=ChatMessage(role=role, content=message_content)
        )

    async def acomplete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponse:
        """Async complete not implemented."""
        raise NotImplementedError("Async methods not implemented")

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Async chat not implemented."""
        raise NotImplementedError("Async methods not implemented")

    def complete_batch(
        self, prompts: List[str], **kwargs: Any
    ) -> List[CompletionResponse]:
        """Batch completion not implemented."""
        raise NotImplementedError("Batch methods not implemented")

    async def acomplete_batch(
        self, prompts: List[str], **kwargs: Any
    ) -> List[CompletionResponse]:
        """Async batch completion not implemented."""
        raise NotImplementedError("Async methods not implemented")

    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream completion not implemented."""
        raise NotImplementedError("Streaming not implemented")

    async def astream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        """Async stream completion not implemented."""
        raise NotImplementedError("Streaming not implemented")
        
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream chat implementation."""
        raise NotImplementedError("Stream chat not implemented")

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> AsyncGenerator[ChatResponse, None]:
        """Async stream chat implementation."""
        raise NotImplementedError("Async stream chat not implemented")