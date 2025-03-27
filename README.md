# NetSourceAI 🤖🌐

A simple intelligent conversational assistant that combines the power of open-source AI models with real-time web access. Inspired by Perplexity AI, but running entirely locally for enhanced privacy and control.

### ✨ At a Glance
- 🔒 100% local and private
- 🌐 Real-time web searches
- 🎯 Accurate responses through web context
- 🚀 2-minute setup

## Quick Start

```bash
# With LM Studio (Recommended)
# 1. Install LM Studio from https://lmstudio.ai/
# 2. Install and run a model
pip install lms
lms get google_gemma-3-4b-it
lms load google_gemma-3-4b-it
lms server start
git clone https://github.com/marlonmo-dev/NetSourceAI.git && cd NetSourceAI
pip install -r requirements.txt
streamlit run app.py
```

Visit http://localhost:8501 to start chatting!

## Setup Options

### Prerequisites
- Python 3.8+
- Internet connection
- One AI backend: Ollama, LMStudio, or OpenAI API

### Alternative Backends

**Ollama**:
- Install from official [website](https://ollama.com/)
- Start your model (server on `localhost:11434`)

**OpenAI**:
- Add to `.env`: `OPENAI_API_KEY=your_key`

## Configuration

Customize via `config.yaml`:
- Model selection
- Generation parameters
- Web sources
- Interface settings

