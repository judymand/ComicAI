"""
MIT License

Copyright (c) 2024 ComicAI Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import json
from typing import List, Dict, Optional, Tuple
import requests
import time

from loguru import logger


class LLMHandler:
    """
    Handler for local LLM interactions using Ollama or similar services.
    """
    
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        """
        Initialize the LLM handler.
        
        Args:
            model_name: Name of the LLM model to use
            base_url: Base URL for the Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
    def is_service_available(self) -> bool:
        """
        Check if the LLM service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"LLM service not available: {e}")
            return False
    
    def generate_panel_descriptions(self, story: str, num_panels: int = 4) -> List[str]:
        """
        Generate panel descriptions from a story using the local LLM.
        
        Args:
            story: The complete story text
            num_panels: Number of panels to generate
            
        Returns:
            List of panel descriptions
        """
        if not self.is_service_available():
            logger.warning("LLM service not available, using fallback method")
            return self._fallback_panel_generation(story, num_panels)
        
        prompt = self._create_panel_prompt(story, num_panels)
        
        try:
            response = self._call_llm_api(prompt)
            if response:
                return self._parse_panel_response(response, num_panels)
            else:
                return self._fallback_panel_generation(story, num_panels)
        except Exception as e:
            logger.error(f"Error generating panels with LLM: {e}")
            return self._fallback_panel_generation(story, num_panels)
    
    def _create_panel_prompt(self, story: str, num_panels: int) -> str:
        """
        Create a prompt for panel generation.
        
        Args:
            story: The story text
            num_panels: Number of panels to generate
            
        Returns:
            Formatted prompt for the LLM
        """
        prompt = f"""
        You are a comic book artist. Break down the following story into {num_panels} comic panels.
        Each panel should be a clear, visual scene that can be illustrated.
        
        Story: {story}
        
        Please provide {num_panels} panel descriptions, each on a new line starting with "Panel X:".
        Make each description visual and specific enough for an artist to draw.
        Keep each description under 50 words.
        
        Format your response as:
        Panel 1: [description]
        Panel 2: [description]
        ...
        Panel {num_panels}: [description]
        """
        return prompt.strip()
    
    def _call_llm_api(self, prompt: str) -> Optional[str]:
        """
        Call the local LLM API.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM response text, or None if failed
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 500
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("LLM API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            return None
    
    def _parse_panel_response(self, response: str, num_panels: int) -> List[str]:
        """
        Parse the LLM response into panel descriptions.
        
        Args:
            response: The LLM response text
            num_panels: Expected number of panels
            
        Returns:
            List of panel descriptions
        """
        lines = response.strip().split('\n')
        panels = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Panel') and ':' in line:
                # Extract description after the colon
                description = line.split(':', 1)[1].strip()
                if description:
                    panels.append(description)
        
        # If we didn't get enough panels, pad with fallback
        if len(panels) < num_panels:
            logger.warning(f"Only got {len(panels)} panels from LLM, using fallback for missing ones")
            while len(panels) < num_panels:
                panels.append(f"Scene {len(panels) + 1}")
        
        return panels[:num_panels]
    
    def _fallback_panel_generation(self, story: str, num_panels: int) -> List[str]:
        """
        Fallback method for panel generation when LLM is not available.
        
        Args:
            story: The story text
            num_panels: Number of panels to generate
            
        Returns:
            List of panel descriptions
        """
        # Simple word-based splitting as fallback
        words = story.split()
        words_per_panel = len(words) // num_panels
        
        panels = []
        for i in range(num_panels):
            start_idx = i * words_per_panel
            end_idx = start_idx + words_per_panel if i < num_panels - 1 else len(words)
            panel_words = words[start_idx:end_idx]
            panel_text = " ".join(panel_words)
            
            # Create a more descriptive panel name
            panel_desc = f"Scene {i+1}: {panel_text[:30]}{'...' if len(panel_text) > 30 else ''}"
            panels.append(panel_desc)
        
        return panels
    
    def enhance_panel_description(self, panel_desc: str, style: str = "comic") -> str:
        """
        Enhance a panel description with style-specific details.
        
        Args:
            panel_desc: Basic panel description
            style: Art style to apply
            
        Returns:
            Enhanced panel description
        """
        style_enhancements = {
            "comic": "comic book style, bold colors, clear outlines",
            "realistic": "photorealistic, detailed, natural lighting",
            "cartoon": "cartoon style, simple shapes, bright colors",
            "anime": "anime style, expressive characters, detailed backgrounds"
        }
        
        enhancement = style_enhancements.get(style, style_enhancements["comic"])
        return f"{panel_desc}, {enhancement}"
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models from the LLM service.
        
        Returns:
            List of available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            else:
                return []
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return [] 