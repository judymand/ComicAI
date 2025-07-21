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

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils import (
    validate_story_input, split_story_into_panels, 
    create_image_prompt, format_error_message
)


class TestUtils:
    """Test cases for utility functions."""
    
    def test_validate_story_input_valid(self):
        """Test valid story input validation."""
        story = "A cat discovers a magical garden and meets talking flowers."
        is_valid, error_msg = validate_story_input(story)
        assert is_valid is True
        assert error_msg == ""
    
    def test_validate_story_input_empty(self):
        """Test empty story input validation."""
        story = ""
        is_valid, error_msg = validate_story_input(story)
        assert is_valid is False
        assert "Please enter a story" in error_msg
    
    def test_validate_story_input_too_short(self):
        """Test story input that's too short."""
        story = "Hi"
        is_valid, error_msg = validate_story_input(story)
        assert is_valid is False
        assert "at least 10 characters" in error_msg
    
    def test_validate_story_input_too_long(self):
        """Test story input that's too long."""
        story = "A" * 1001
        is_valid, error_msg = validate_story_input(story)
        assert is_valid is False
        assert "under 1000 characters" in error_msg
    
    def test_split_story_into_panels(self):
        """Test story splitting into panels."""
        story = "This is a test story with multiple words to split into panels."
        panels = split_story_into_panels(story, num_panels=3)
        
        assert len(panels) == 3
        assert all(isinstance(panel, str) for panel in panels)
        assert all(len(panel) > 0 for panel in panels)
    
    def test_create_image_prompt(self):
        """Test image prompt creation."""
        panel_desc = "A cat in a garden"
        prompt = create_image_prompt(panel_desc, style="comic")
        
        assert "A cat in a garden" in prompt
        assert "comic book style" in prompt
        assert "vibrant colors" in prompt
    
    def test_create_image_prompt_different_style(self):
        """Test image prompt creation with different style."""
        panel_desc = "A cat in a garden"
        prompt = create_image_prompt(panel_desc, style="anime")
        
        assert "A cat in a garden" in prompt
        assert "anime style" in prompt
        assert "expressive characters" in prompt
    
    def test_format_error_message(self):
        """Test error message formatting."""
        # Test ConnectionError
        error = ConnectionError("Connection failed")
        message = format_error_message(error)
        assert "Unable to connect" in message
        
        # Test ValueError
        error = ValueError("Invalid input")
        message = format_error_message(error)
        assert "Invalid input provided" in message
        
        # Test unknown error
        error = RuntimeError("Unknown error")
        message = format_error_message(error)
        assert "unexpected error occurred" in message


if __name__ == "__main__":
    pytest.main([__file__]) 