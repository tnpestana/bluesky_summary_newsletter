"""
AI summarization service supporting multiple providers.
"""

import logging
import requests
import subprocess
import time
import atexit
import os
from typing import Dict, List, Any
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self, provider: str, models: list, base_url: str = None):
        self.provider = provider
        self.models = models if isinstance(models, list) else [models]
        self.base_url = base_url
        self.ollama_process = None
        
        if provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")
        elif provider == "groq":
            # Groq uses OpenAI-compatible API
            openai.api_key = os.getenv("GROQ_API_KEY")
            # Ensure proper URL formatting for Groq
            if base_url and not base_url.endswith('/'):
                base_url = base_url + '/'
            openai.base_url = base_url
        elif provider == "anthropic":
            self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        elif provider == "ollama":
            self.setup_ollama()
        
        atexit.register(self.cleanup)

    def setup_ollama(self):
        """Start Ollama server and ensure model is available."""
        logger.info("Setting up Ollama...")
        
        # Check if Ollama is already running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama is already running")
                self.ensure_model_available()
                return
        except requests.exceptions.RequestException:
            pass
        
        # Start Ollama server
        logger.info("Starting Ollama server...")
        try:
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            for _ in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{self.base_url}/api/tags", timeout=2)
                    if response.status_code == 200:
                        logger.info("Ollama server started successfully")
                        break
                except requests.exceptions.RequestException:
                    time.sleep(1)
            else:
                raise Exception("Ollama server failed to start within 30 seconds")
            
            self.ensure_model_available()
            
        except Exception as e:
            logger.error(f"Failed to start Ollama: {str(e)}")
            raise

    def ensure_model_available(self):
        """Ensure the specified model is pulled and available."""
        logger.info(f"Checking if model '{self.model}' is available...")
        
        try:
            # Check if model is already available
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            
            for model in models:
                if model["name"].startswith(self.model):
                    logger.info(f"Model '{self.model}' is available")
                    return
            
            # Pull the model if not available
            logger.info(f"Pulling model '{self.model}'. This may take a while...")
            pull_process = subprocess.run(
                ["ollama", "pull", self.model],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for model pull
            )
            
            if pull_process.returncode == 0:
                logger.info(f"Model '{self.model}' pulled successfully")
            else:
                raise Exception(f"Failed to pull model: {pull_process.stderr}")
                
        except Exception as e:
            logger.error(f"Error ensuring model availability: {str(e)}")
            raise

    def cleanup(self):
        """Clean up Ollama process on exit."""
        if self.ollama_process and self.ollama_process.poll() is None:
            logger.info("Stopping Ollama server...")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()

    def generate_summary(self, posts_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate AI summary of all posts."""
        if not any(posts_data.values()):
            return "No posts found in the specified time period."
        
        # Prepare post text for AI
        post_text = ""
        for handle, posts in posts_data.items():
            if posts:
                post_text += f"\n--- Posts from {handle} ---\n"
                for post in posts:
                    post_text += f"• {post['text']}\n"
        
        # Load prompt template from file
        try:
            with open("prompt_template.txt", "r", encoding="utf-8") as f:
                prompt_template = f.read()
        except FileNotFoundError:
            logger.warning("prompt_template.txt not found, using default prompt")
            prompt_template = """You are a professional sports newsletter writer. Create a comprehensive summary of these Bluesky posts.
            
            POSTS TO SUMMARIZE:
            {post_text}
            
            Create a polished newsletter summary."""
        
        prompt = prompt_template.format(post_text=post_text)

        try:
            if self.provider in ["openai", "groq"]:
                # Try models in order until one succeeds
                last_error = None
                for i, model_to_try in enumerate(self.models):
                    try:
                        logger.info(f"Trying model {i+1}/{len(self.models)}: {model_to_try}")
                        response = openai.chat.completions.create(
                            model=model_to_try,
                            messages=[
                                {"role": "system", "content": "You are a professional sports newsletter writer specializing in structured content creation."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=2000  # Increased for longer structured content
                        )
                        logger.info(f"Successfully used model: {model_to_try}")
                        return response.choices[0].message.content
                    except Exception as e:
                        last_error = e
                        logger.warning(f"Model {model_to_try} failed: {str(e)}")
                        if i == len(self.models) - 1:  # Last model in list
                            logger.error("All models failed, re-raising last error")
                            raise last_error
                        continue  # Try next model
            
            elif self.provider == "anthropic":
                # For Anthropic, use the first model in the list
                model_to_use = self.models[0] if self.models else "claude-3-sonnet-20240229"
                response = self.anthropic_client.messages.create(
                    model=model_to_use,
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
            
            elif self.provider == "ollama":
                # For Ollama, use the first model in the list
                model_to_use = self.models[0] if self.models else "llama3"
                payload = {
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return f"Error generating summary: {str(e)}"