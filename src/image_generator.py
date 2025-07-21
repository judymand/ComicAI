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
import base64
import io
from typing import List, Optional, Dict, Tuple
import requests
import time

from PIL import Image, ImageDraw, ImageFont
from loguru import logger


class ImageGenerator:
    """
    Handler for image generation using Stable Diffusion via Hugging Face Spaces.
    """
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        Initialize the image generator.
        
        Args:
            api_url: URL for the Stable Diffusion API
            api_key: API key for authentication (if required)
        """
        self.api_url = api_url or os.getenv("STABLE_DIFFUSION_API_URL")
        self.api_key = api_key or os.getenv("HUGGING_FACE_API_KEY")
        self.default_headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            self.default_headers["Authorization"] = f"Bearer {self.api_key}"
    
    def generate_image(self, prompt: str, style: str = "comic", 
                      width: int = 512, height: int = 512) -> Optional[Image.Image]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description for the image
            style: Art style to apply
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            PIL Image object, or None if generation failed
        """
        try:
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Generate image using API
            image_data = self._call_image_api(enhanced_prompt, width, height)
            
            if image_data:
                # Convert to PIL Image
                image = Image.open(io.BytesIO(image_data))
                return self._post_process_image(image, style)
            else:
                logger.error("Failed to generate image")
                return self._create_placeholder_image(prompt, width, height)
                
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._create_placeholder_image(prompt, width, height)
    
    def generate_comic_panels(self, panel_descriptions: List[str], 
                            style: str = "comic") -> List[Image.Image]:
        """
        Generate images for multiple comic panels.
        
        Args:
            panel_descriptions: List of panel descriptions
            style: Art style to apply
            
        Returns:
            List of PIL Image objects
        """
        images = []
        
        for i, description in enumerate(panel_descriptions):
            logger.info(f"Generating image for panel {i+1}/{len(panel_descriptions)}")
            
            # Add panel context to description
            panel_prompt = f"Comic panel {i+1}: {description}"
            
            image = self.generate_image(panel_prompt, style)
            if image:
                images.append(image)
            else:
                # Create placeholder if generation failed
                placeholder = self._create_placeholder_image(description)
                images.append(placeholder)
            
            # Add delay between requests to avoid rate limiting
            if i < len(panel_descriptions) - 1:
                time.sleep(1)
        
        return images
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """
        Enhance the prompt with style-specific details.
        
        Args:
            prompt: Original prompt
            style: Art style to apply
            
        Returns:
            Enhanced prompt
        """
        style_enhancements = {
            "comic": "comic book style, vibrant colors, bold outlines, clear composition",
            "realistic": "photorealistic, detailed, natural lighting, high quality",
            "cartoon": "cartoon style, simple shapes, bright colors, clean lines",
            "anime": "anime style, expressive characters, detailed backgrounds, manga influence",
            "watercolor": "watercolor painting style, soft colors, artistic",
            "sketch": "pencil sketch style, black and white, artistic"
        }
        
        enhancement = style_enhancements.get(style, style_enhancements["comic"])
        
        # Add negative prompts to avoid common issues
        negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy"
        
        enhanced_prompt = f"{prompt}, {enhancement}"
        return enhanced_prompt, negative_prompt
    
    def _call_image_api(self, prompt: str, width: int, height: int) -> Optional[bytes]:
        """
        Call the image generation API.
        
        Args:
            prompt: Enhanced prompt
            width: Image width
            height: Image height
            
        Returns:
            Image data as bytes, or None if failed
        """
        if not self.api_url:
            logger.error("No API URL configured for image generation")
            return None
        
        enhanced_prompt, negative_prompt = self._enhance_prompt(prompt, "comic")
        
        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "num_images_per_prompt": 1
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.default_headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different API response formats
                if "images" in result:
                    # Hugging Face Spaces format
                    image_data = base64.b64decode(result["images"][0])
                    return image_data
                elif "data" in result:
                    # Alternative format
                    image_data = base64.b64decode(result["data"][0])
                    return image_data
                else:
                    logger.error(f"Unexpected API response format: {result}")
                    return None
            else:
                logger.error(f"Image API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Image generation request timed out")
            return None
        except Exception as e:
            logger.error(f"Error calling image API: {e}")
            return None
    
    def _post_process_image(self, image: Image.Image, style: str) -> Image.Image:
        """
        Apply post-processing to the generated image.
        
        Args:
            image: Original image
            style: Art style applied
            
        Returns:
            Processed image
        """
        # Resize to standard comic panel size if needed
        target_size = (512, 512)
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Apply style-specific enhancements
        if style == "comic":
            # Enhance contrast for comic style
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
        
        return image
    
    def _create_placeholder_image(self, prompt: str, width: int = 512, 
                                height: int = 512) -> Image.Image:
        """
        Create a placeholder image when generation fails.
        
        Args:
            prompt: The prompt that failed
            width: Image width
            height: Image height
            
        Returns:
            Placeholder image
        """
        # Create a simple placeholder
        image = Image.new('RGB', (width, height), color='#f0f0f0')
        draw = ImageDraw.Draw(image)
        
        # Add text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw placeholder text
        text = f"Image generation failed\nPrompt: {prompt[:50]}..."
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='#666666', font=font)
        
        # Draw border
        draw.rectangle([0, 0, width-1, height-1], outline='#cccccc', width=2)
        
        return image
    
    def combine_panels_into_comic(self, images: List[Image.Image], 
                                layout: str = "horizontal") -> Image.Image:
        """
        Combine multiple panel images into a single comic strip.
        
        Args:
            images: List of panel images
            layout: Layout style ("horizontal", "vertical", "grid")
            
        Returns:
            Combined comic image
        """
        if not images:
            return self._create_placeholder_image("No panels to combine")
        
        panel_width, panel_height = images[0].size
        spacing = 10  # Space between panels
        
        if layout == "horizontal":
            # Arrange panels horizontally
            total_width = len(images) * panel_width + (len(images) - 1) * spacing
            total_height = panel_height
            
            combined_image = Image.new('RGB', (total_width, total_height), 'white')
            
            for i, image in enumerate(images):
                x = i * (panel_width + spacing)
                combined_image.paste(image, (x, 0))
        
        elif layout == "vertical":
            # Arrange panels vertically
            total_width = panel_width
            total_height = len(images) * panel_height + (len(images) - 1) * spacing
            
            combined_image = Image.new('RGB', (total_width, total_height), 'white')
            
            for i, image in enumerate(images):
                y = i * (panel_height + spacing)
                combined_image.paste(image, (0, y))
        
        else:  # grid layout
            # Arrange in a grid (2 columns)
            cols = 2
            rows = (len(images) + 1) // 2
            
            total_width = cols * panel_width + (cols - 1) * spacing
            total_height = rows * panel_height + (rows - 1) * spacing
            
            combined_image = Image.new('RGB', (total_width, total_height), 'white')
            
            for i, image in enumerate(images):
                row = i // cols
                col = i % cols
                x = col * (panel_width + spacing)
                y = row * (panel_height + spacing)
                combined_image.paste(image, (x, y))
        
        return combined_image
    
    def add_text_to_image(self, image: Image.Image, text: str, 
                         position: str = "bottom") -> Image.Image:
        """
        Add text overlay to an image.
        
        Args:
            image: Original image
            text: Text to add
            position: Text position ("top", "bottom", "center")
            
        Returns:
            Image with text overlay
        """
        # Create a copy to avoid modifying original
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        img_width, img_height = image.size
        
        if position == "top":
            x = (img_width - text_width) // 2
            y = 10
        elif position == "bottom":
            x = (img_width - text_width) // 2
            y = img_height - text_height - 10
        else:  # center
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
        
        # Draw text with outline for better visibility
        outline_color = 'black'
        text_color = 'white'
        
        # Draw outline
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)
        
        return result 