# 🎨 ComicAI

> **Transform your ideas into unique comic strips!** ComicAI lets you enter a short story or idea, splits it into comic panels using a local AI model, and generates original images for each panel, presenting everything in a beautiful comic strip layout.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red.svg)](https://streamlit.io)
[![AI](https://img.shields.io/badge/AI-Powered-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Local LLM setup (Ollama recommended)
- Stable Diffusion API access (Hugging Face Spaces)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/comicai.git
   cd comicai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   # Create .env file
   echo "STABLE_DIFFUSION_API_URL=your_api_url_here" > .env
   echo "HUGGING_FACE_API_KEY=your_api_key_here" >> .env
   ```

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

---

## 🎯 How It Works

### Core Flow

1. **📝 Story Input** - Enter your creative idea in the text box
2. **🤖 Panel Breakdown** - Local LLM splits your story into 3-5 comic panels
3. **🎨 Image Generation** - Stable Diffusion creates unique illustrations for each panel
4. **📱 Comic Presentation** - View your comic strip in a beautiful web interface
5. **💾 Download/Share** - Save your creation in multiple formats

### AI Pipeline

```
User Story/Idea 
    ↓
[Local LLM: Split story into panels]
    ↓
Scene Descriptions
    ↓
[Stable Diffusion API: Generate images]
    ↓
Comic Panels
    ↓
[Streamlit: Display comic strip]
```

---

## 🛠️ Features

### ✨ Core Features
- **Simple Story Input** - Just type your idea and let AI do the rest
- **AI-Powered Panel Generation** - Automatic story breakdown into comic panels
- **Original Image Creation** - Unique illustrations for each panel
- **Beautiful Web Interface** - Clean, intuitive Streamlit app
- **Download & Share** - Export your comics in multiple formats
- **Completely Free** - No paid services required

### 🎨 Art Styles
- **Comic Book** - Bold colors, clear outlines
- **Cartoon** - Simple shapes, bright colors
- **Anime** - Expressive characters, detailed backgrounds
- **Realistic** - Photorealistic, detailed
- **Watercolor** - Soft colors, artistic
- **Sketch** - Pencil style, black and white

### 📐 Layout Options
- **Horizontal** - Traditional comic strip layout
- **Vertical** - Stacked panels
- **Grid** - 2-column arrangement

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Image Generation API
STABLE_DIFFUSION_API_URL=https://your-api-endpoint.com
HUGGING_FACE_API_KEY=your_api_key_here

# Local LLM (optional)
OLLAMA_BASE_URL=http://localhost:11434
```

### Local LLM Setup

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Windows
   # Download from https://ollama.ai/download
   ```

2. **Pull a model**
   ```bash
   ollama pull llama2
   # or
   ollama pull qwen
   ```

3. **Start Ollama service**
   ```bash
   ollama serve
   ```

---

## 📖 Usage

### Basic Usage

1. **Start the app**
   ```bash
   streamlit run src/app.py
   ```

2. **Enter your story**
   - Type or paste your creative idea
   - Minimum 10 characters, maximum 1000 characters

3. **Configure settings**
   - Choose art style (comic, cartoon, anime, etc.)
   - Select number of panels (2-6)
   - Pick layout style (horizontal, vertical, grid)

4. **Generate your comic**
   - Click "Generate Comic" button
   - Watch the progress as AI creates your panels

5. **Download results**
   - Download individual panels
   - Get the combined comic strip
   - Export as ZIP file

### Advanced Usage

#### Custom LLM Models
```python
from src.llm_handler import LLMHandler

# Use a different model
llm = LLMHandler(model_name="qwen")
panels = llm.generate_panel_descriptions("Your story here", num_panels=4)
```

#### Custom Image Generation
```python
from src.image_generator import ImageGenerator

# Generate single image
generator = ImageGenerator(api_url="your_api_url")
image = generator.generate_image("A cat in a garden", style="comic")
```

---

## 🏗️ Project Structure

```
ComicAI/
├── .cursor/
│   └── rules                 # Development rules
├── src/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Main Streamlit application
│   ├── utils.py             # Utility functions
│   ├── llm_handler.py       # Local LLM integration
│   └── image_generator.py   # Image generation logic
├── assets/                  # Static assets
├── tests/                   # Test files
├── data/                    # Data storage
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── product_definition.md   # Product documentation
```

---

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/comicai.git
cd comicai

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run code formatting
black src/
flake8 src/
mypy src/
```

---

## 🐛 Troubleshooting

### Common Issues

**LLM Service Not Available**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

**Image Generation Fails**
- Verify your API URL is correct
- Check your API key is valid
- Ensure you have sufficient API credits

**Streamlit App Won't Start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- 📖 **Documentation**: Check the [product_definition.md](product_definition.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/comicai/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/comicai/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hugging Face** - For providing free AI model APIs
- **Streamlit** - For the amazing web app framework
- **Stable Diffusion** - For image generation capabilities
- **Ollama** - For local LLM support
- **Open Source Community** - For inspiration and support

---

## 📞 Contact

- **Project Link**: [https://github.com/yourusername/comicai](https://github.com/yourusername/comicai)
- **Issues**: [GitHub Issues](https://github.com/yourusername/comicai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/comicai/discussions)

---

<div align="center">

**Made with ❤️ by the ComicAI Team**

[![Star](https://img.shields.io/github/stars/yourusername/comicai?style=social)](https://github.com/yourusername/comicai)
[![Fork](https://img.shields.io/github/forks/yourusername/comicai?style=social)](https://github.com/yourusername/comicai)

</div>
