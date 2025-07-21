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
import sys
from pathlib import Path
from typing import List, Optional

import streamlit as st
from PIL import Image
import io

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from utils import (
    setup_logging, validate_story_input, get_session_state, 
    clear_session_state, format_error_message, create_download_link
)
from llm_handler import LLMHandler
from image_generator import ImageGenerator
from local_image_generator import LocalImageGenerator


def main():
    """
    Main Streamlit application for ComicAI.
    """
    # Configure page
    st.set_page_config(
        page_title="ComicAI - AI-Powered Comic Creator",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Setup logging
    setup_logging()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .comic-panel {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🎨 ComicAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your ideas into unique comic strips!</p>', 
                unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Art style selection
        art_style = st.selectbox(
            "Art Style",
            ["comic", "cartoon", "anime", "realistic", "watercolor", "sketch"],
            help="Choose the visual style for your comic"
        )
        
        # Number of panels
        num_panels = st.slider(
            "Number of Panels",
            min_value=2,
            max_value=6,
            value=4,
            help="How many panels should your comic have?"
        )
        
        # Layout style
        layout_style = st.selectbox(
            "Layout Style",
            ["horizontal", "vertical", "grid"],
            help="How should the panels be arranged?"
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            # LLM model selection
            llm_model = st.text_input(
                "LLM Model",
                value="llama2",
                help="Name of the local LLM model to use"
            )
            
            # API URL for image generation
            api_url = st.text_input(
                "Image API URL",
                value=os.getenv("STABLE_DIFFUSION_API_URL", ""),
                help="URL for Stable Diffusion API"
            )
            
            # API key
            api_key = st.text_input(
                "API Key",
                value=os.getenv("HUGGING_FACE_API_KEY", ""),
                type="password",
                help="API key for image generation (if required)"
            )
        
        # Clear session button
        if st.button("🗑️ Clear Session"):
            clear_session_state()
            st.success("Session cleared!")
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Your Story")
        
        # Story input
        story_text = st.text_area(
            "Enter your story or idea here:",
            height=200,
            placeholder="Once upon a time, a brave cat discovered a magical garden...",
            help="Describe your story in detail. The AI will break it down into comic panels."
        )
        
        # Generate button
        if st.button("🚀 Generate Comic", type="primary", use_container_width=True):
            if story_text.strip():
                generate_comic(story_text, art_style, num_panels, layout_style, 
                             llm_model, api_url, api_key)
            else:
                st.error("Please enter a story first!")
    
    with col2:
        st.header("📊 Status")
        
        # Display current status
        session_data = get_session_state()
        
        if session_data["generated"]:
            st.success("✅ Comic generated successfully!")
            
            # Display panel count
            st.metric("Panels Created", len(session_data["panels"]))
            st.metric("Images Generated", len(session_data["images"]))
            
            # Show generation time if available
            if "generation_time" in session_data:
                st.metric("Generation Time", f"{session_data['generation_time']:.1f}s")
        else:
            st.info("💡 Enter your story and click 'Generate Comic' to get started!")
    
    # Display generated comic
    if session_data["generated"] and session_data["images"]:
        st.header("🎨 Your Comic")
        
        # Display individual panels
        st.subheader("Individual Panels")
        cols = st.columns(min(len(session_data["images"]), 4))
        
        for i, (image, panel_text) in enumerate(zip(session_data["images"], session_data["panels"])):
            col_idx = i % len(cols)
            with cols[col_idx]:
                st.image(image, caption=f"Panel {i+1}: {panel_text[:50]}...", use_column_width=True)
        
        # Display combined comic
        st.subheader("Combined Comic Strip")
        
        # Create combined image
        local_generator = LocalImageGenerator()
        if local_generator.is_available():
            combined_image = local_generator.combine_panels_into_comic(
                session_data["images"], layout_style
            )
        else:
            image_generator = ImageGenerator(api_url, api_key)
            combined_image = image_generator.combine_panels_into_comic(
                session_data["images"], layout_style
            )
        
        st.image(combined_image, caption="Your complete comic strip!", use_column_width=True)
        
        # Download options
        st.subheader("💾 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download combined comic
            img_buffer = io.BytesIO()
            combined_image.save(img_buffer, format="PNG")
            img_data = img_buffer.getvalue()
            
            st.download_button(
                label="📥 Download Combined Comic",
                data=img_data,
                file_name="comic_strip.png",
                mime="image/png",
                use_container_width=True
            )
        
        with col2:
            # Download individual panels
            if st.button("📥 Download All Panels", use_container_width=True):
                # Create zip file with all panels
                import zipfile
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for i, (image, panel_text) in enumerate(zip(session_data["images"], session_data["panels"])):
                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format="PNG")
                        zip_file.writestr(f"panel_{i+1}.png", img_buffer.getvalue())
                
                st.download_button(
                    label="📦 Download ZIP",
                    data=zip_buffer.getvalue(),
                    file_name="comic_panels.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        
        with col3:
            # Share options
            if st.button("📤 Share Comic", use_container_width=True):
                st.info("Sharing feature coming soon! For now, you can download and share manually.")


def generate_comic(story_text: str, art_style: str, num_panels: int, 
                  layout_style: str, llm_model: str, api_url: str, api_key: str):
    """
    Generate a comic from the given story text.
    
    Args:
        story_text: The story to convert into a comic
        art_style: Visual style for the comic
        num_panels: Number of panels to generate
        layout_style: Layout arrangement for panels
        llm_model: LLM model to use
        api_url: Image generation API URL
        api_key: API key for image generation
    """
    import time
    
    # Get session state
    session_data = get_session_state()
    
    # Validate input
    is_valid, error_msg = validate_story_input(story_text)
    if not is_valid:
        st.error(error_msg)
        return
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        start_time = time.time()
        
        # Step 1: Generate panel descriptions
        status_text.text("🤖 Generating panel descriptions...")
        progress_bar.progress(20)
        
        llm_handler = LLMHandler(model_name=llm_model)
        panel_descriptions = llm_handler.generate_panel_descriptions(story_text, num_panels)
        
        # Step 2: Generate images for each panel
        status_text.text("🎨 Generating images...")
        progress_bar.progress(40)
        
        # Try local generation first, fallback to API if available
        local_generator = LocalImageGenerator()
        if local_generator.is_available():
            st.info("🎨 Using local Stable Diffusion for image generation (no API needed!)")
            images = local_generator.generate_comic_panels(panel_descriptions, art_style)
        elif api_url:
            st.info("🌐 Using API for image generation")
            image_generator = ImageGenerator(api_url, api_key)
            images = image_generator.generate_comic_panels(panel_descriptions, art_style)
        else:
            st.warning("⚠️ No image generation available. Using placeholders.")
            # Create placeholder images
            from PIL import Image, ImageDraw, ImageFont
            images = []
            for i, description in enumerate(panel_descriptions):
                img = Image.new('RGB', (512, 512), color='#f0f0f0')
                draw = ImageDraw.Draw(img)
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
                text = f"Panel {i+1}: {description[:30]}..."
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (512 - text_width) // 2
                y = (512 - text_height) // 2
                draw.text((x, y), text, fill='#666666', font=font)
                draw.rectangle([0, 0, 511, 511], outline='#cccccc', width=2)
                images.append(img)
        
        # Step 3: Update session state
        status_text.text("💾 Saving results...")
        progress_bar.progress(80)
        
        session_data["story"] = story_text
        session_data["panels"] = panel_descriptions
        session_data["images"] = images
        session_data["generated"] = True
        session_data["generation_time"] = time.time() - start_time
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Comic generated successfully!")
        
        # Show success message
        st.success("🎉 Your comic has been generated! Scroll down to see the results.")
        
    except Exception as e:
        # Handle errors gracefully
        error_msg = format_error_message(e)
        st.error(f"❌ Error generating comic: {error_msg}")
        progress_bar.progress(0)
        status_text.text("❌ Generation failed")


if __name__ == "__main__":
    main() 