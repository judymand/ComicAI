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
import time
from typing import List, Optional
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from loguru import logger

try:
    from diffusers import StableDiffusionPipeline
    import torch
    LOCAL_DIFFUSION_AVAILABLE = True
except ImportError:
    LOCAL_DIFFUSION_AVAILABLE = False
    logger.warning("Local Stable Diffusion not available. Install with: pip install diffusers transformers torch")


class LocalImageGenerator:
    """
    Local image generator using Stable Diffusion.
    Works completely offline without any API keys.
    """
    
    def __init__(self, model_name: str = "runwayml/stable-diffusion-v1-5"):
        """
        Initialize the local image generator.
        
        Args:
            model_name: Name of the Stable Diffusion model to use
        """
        self.model_name = model_name
        self.pipeline = None
        self.device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Using device: {self.device}")
        
        if not LOCAL_DIFFUSION_AVAILABLE:
            logger.error("Local Stable Diffusion not available")
            return
        
        self._load_model()
    
    def _load_model(self):
        """Load the Stable Diffusion model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            logger.info("This may take a few minutes on first run...")
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            if self.device != "cpu":
                self.pipeline = self.pipeline.to(self.device)
            
            logger.info("✅ Model loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.pipeline = None
    
    def is_available(self) -> bool:
        """
        Check if local image generation is available.
        
        Returns:
            True if available, False otherwise
        """
        return LOCAL_DIFFUSION_AVAILABLE and self.pipeline is not None
    
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
        if not self.is_available():
            logger.warning("Local image generation not available, using placeholder")
            return self._create_placeholder_image(prompt, width, height)
        
        try:
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            logger.info(f"Generating image: {enhanced_prompt[:50]}...")
            
            # Generate image
            result = self.pipeline(
                prompt=enhanced_prompt,
                width=width,
                height=height,
                num_inference_steps=20,
                guidance_scale=7.5,
                num_images_per_prompt=1
            )
            
            if result.images and len(result.images) > 0:
                image = result.images[0]
                return self._post_process_image(image, style)
            else:
                logger.error("No images generated")
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
            
            # Small delay between generations
            if i < len(panel_descriptions) - 1:
                time.sleep(0.5)
        
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
            "comic": "comic book style, vibrant colors, bold outlines, clear composition, high quality",
            "realistic": "photorealistic, detailed, natural lighting, high quality, sharp focus",
            "cartoon": "cartoon style, simple shapes, bright colors, clean lines, cute",
            "anime": "anime style, expressive characters, detailed backgrounds, manga influence, high quality",
            "watercolor": "watercolor painting style, soft colors, artistic, beautiful",
            "sketch": "pencil sketch style, black and white, artistic, detailed"
        }
        
        enhancement = style_enhancements.get(style, style_enhancements["comic"])
        
        # Add negative prompts to avoid common issues
        negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, watermark, signature"
        
        enhanced_prompt = f"{prompt}, {enhancement}"
        return enhanced_prompt
    
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
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw placeholder text
        text = f"Local generation failed\nPrompt: {prompt[:40]}..."
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