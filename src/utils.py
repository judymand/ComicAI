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
import base64
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

import streamlit as st
from PIL import Image
import requests
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR)
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        "logs/comicai.log",
        rotation="10 MB",
        retention="7 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    # Add console output
    logger.add(
        lambda msg: print(msg, end=""),
        level=log_level,
        format="{time:HH:mm:ss} | {level} | {message}"
    )


def validate_story_input(story_text: str) -> Tuple[bool, str]:
    """
    Validate the user's story input.
    
    Args:
        story_text: The story text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not story_text or not story_text.strip():
        return False, "Please enter a story or idea."
    
    if len(story_text.strip()) < 10:
        return False, "Story must be at least 10 characters long."
    
    if len(story_text) > 1000:
        return False, "Story is too long. Please keep it under 1000 characters."
    
    return True, ""


def split_story_into_panels(story_text: str, num_panels: int = 4) -> List[str]:
    """
    Split a story into panel descriptions.
    
    Args:
        story_text: The complete story text
        num_panels: Number of panels to create (default: 4)
        
    Returns:
        List of panel descriptions
    """
    # Simple splitting logic - can be enhanced with AI
    words = story_text.split()
    words_per_panel = len(words) // num_panels
    
    panels = []
    for i in range(num_panels):
        start_idx = i * words_per_panel
        end_idx = start_idx + words_per_panel if i < num_panels - 1 else len(words)
        panel_words = words[start_idx:end_idx]
        panels.append(" ".join(panel_words))
    
    return panels


def create_image_prompt(panel_description: str, style: str = "comic") -> str:
    """
    Create an image generation prompt from panel description.
    
    Args:
        panel_description: Description of the panel
        style: Art style for the image (comic, realistic, cartoon, etc.)
        
    Returns:
        Formatted prompt for image generation
    """
    style_prompts = {
        "comic": "comic book style, vibrant colors, clear lines",
        "realistic": "photorealistic, detailed, natural lighting",
        "cartoon": "cartoon style, simple shapes, bright colors",
        "anime": "anime style, expressive characters, detailed backgrounds"
    }
    
    style_desc = style_prompts.get(style, style_prompts["comic"])
    
    prompt = f"{panel_description}, {style_desc}, high quality, clear composition"
    return prompt


def save_comic_to_file(images: List[Image.Image], panel_texts: List[str], 
                      output_path: str) -> bool:
    """
    Save the generated comic to a file.
    
    Args:
        images: List of PIL Image objects
        panel_texts: List of panel descriptions
        output_path: Path to save the comic
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save as individual images
        for i, (image, text) in enumerate(zip(images, panel_texts)):
            image_path = f"{output_path}_panel_{i+1}.png"
            image.save(image_path, "PNG")
            logger.info(f"Saved panel {i+1} to {image_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving comic: {e}")
        return False


def encode_image_to_base64(image: Image.Image) -> str:
    """
    Encode a PIL Image to base64 string for web display.
    
    Args:
        image: PIL Image object
        
    Returns:
        Base64 encoded string
    """
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


def get_session_state() -> Dict:
    """
    Get or initialize Streamlit session state.
    
    Returns:
        Dictionary containing session state
    """
    if "comic_data" not in st.session_state:
        st.session_state.comic_data = {
            "story": "",
            "panels": [],
            "images": [],
            "generated": False
        }
    
    return st.session_state.comic_data


def clear_session_state() -> None:
    """Clear the current session state."""
    if "comic_data" in st.session_state:
        del st.session_state.comic_data


def format_error_message(error: Exception) -> str:
    """
    Format error messages for user-friendly display.
    
    Args:
        error: The exception that occurred
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        "ConnectionError": "Unable to connect to AI service. Please check your internet connection.",
        "TimeoutError": "Request timed out. Please try again.",
        "ValueError": "Invalid input provided. Please check your story text.",
        "RuntimeError": "An error occurred while processing your request. Please try again."
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, f"An unexpected error occurred: {str(error)}")


def validate_api_response(response: requests.Response) -> bool:
    """
    Validate API response and handle common errors.
    
    Args:
        response: Requests response object
        
    Returns:
        True if response is valid, False otherwise
    """
    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        logger.error("API authentication failed")
        return False
    elif response.status_code == 429:
        logger.error("API rate limit exceeded")
        return False
    elif response.status_code >= 500:
        logger.error(f"Server error: {response.status_code}")
        return False
    else:
        logger.error(f"API error: {response.status_code} - {response.text}")
        return False


def create_download_link(data: bytes, filename: str, text: str) -> str:
    """
    Create a download link for Streamlit.
    
    Args:
        data: File data as bytes
        filename: Name of the file to download
        text: Display text for the link
        
    Returns:
        HTML download link
    """
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download="{filename}">{text}</a>'
    return href 