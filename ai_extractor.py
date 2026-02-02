import os
import json
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv

load_dotenv()

class AIExtractor:
    """
    Unified interface for AI-powered data extraction.
    Supports local Ollama and various cloud LLM providers.
    """
    
    def __init__(self, provider: str = "ollama", model: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model or self._get_default_model()

    def _get_default_model(self) -> str:
        defaults = {
            "ollama": "llama3",
            "groq": "llama3-8b-8192",
            "anthropic": "claude-3-haiku-20240307",
            "google": "gemini-1.5-flash",
            "openrouter": "openai/gpt-3.5-turbo"
        }
        return defaults.get(self.provider, "llama3")

    def extract(self, html_content: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from HTML based on a provided JSON schema."""
        prompt = f"""
        Extract data from the following HTML content according to this JSON schema:
        Schema: {json.dumps(schema)}
        
        HTML Content:
        {html_content[:5000]}  # Truncate for token limits
        
        Return ONLY valid JSON.
        """
        
        if self.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.provider in ["groq", "anthropic", "google", "openrouter", "together"]:
            return self._call_cloud_api(prompt)
        else:
            raise ValueError(f"Provider {self.provider} not supported")

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Calls local Ollama instance."""
        try:
            resp = httpx.post("http://localhost:11434/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=30.0)
            return json.loads(resp.json()['response'])
        except Exception as e:
            return {"error": str(e)}

    def _call_cloud_api(self, prompt: str) -> Dict[str, Any]:
        """Generic cloud API caller (simplified handling for demo)."""
        api_keys = {
            "groq": os.getenv("GROQ_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_API_KEY"),
            "openrouter": os.getenv("OPENROUTER_API_KEY"),
            "together": os.getenv("TOGETHER_API_KEY")
        }
        
        api_key = api_keys.get(self.provider)
        if not api_key:
            return {"error": f"API key for {self.provider} missing"}

        # Placeholder for provider-specific API logic
        # For brevity, only implementing Groq here as an example
        if self.provider == "groq":
            resp = httpx.post("https://api.groq.com/openai/v1/chat/completions", 
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }, timeout=30.0)
            return json.loads(resp.json()['choices'][0]['message']['content'])
        
        return {"error": f"Cloud provider {self.provider} logic not fully implemented yet"}

if __name__ == "__main__":
    extractor = AIExtractor(provider="ollama")
    schema = {"title": "string", "price": "number"}
    # result = extractor.extract("<html><body><h1>iPhone 15</h1><span>$999</span></body></html>", schema)
    # print(result)
