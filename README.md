# Linky - AI-Powered LinkedIn Content Generator

![Linky Logo](https://img.shields.io/badge/Linky-AI%20Content%20Engine-0077B5?style=for-the-badge)

## Overview

Linky is an intelligent LinkedIn content generation engine that produces viral, engaging, and unique posts based on user input and real-time data. Built with LangGraph orchestration and powered by advanced LLMs via OpenRouter.

## Brand Identity

- **Name**: Linky
- **Essence**: Intelligent Connection, Effortless Influence, Narrative Impact, Data-Driven Storytelling
- **Color Palette**:
  - Primary Blue: `#0077B5` (Main branding, CTAs)
  - Accent Teal: `#00B5AD` (Secondary accents, interactive elements)
  - Neutral Gray: `#4A4A4A` (Text, backgrounds)
  - Light Gray: `#F0F2F5` (Backgrounds, dividers)

## Features

- **Intelligent Content Generation**: AI-powered posts tailored to your topic and preferences
- **Real-Time Data Integration**: Fetches latest news and statistics relevant to your topic
- **Multiple Tones & Styles**: Choose from various professional personas
- **Anti-Slop Principles**: Ensures high-quality, human-like content
- **Uniqueness Guarantee**: Dynamic perspective shifting and contextual data integration
- **Live Preview**: See your content as you configure it

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd linky_app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.template` to `.env`
   - Add your OpenRouter API key
   - (Optional) Add News API keys for enhanced data retrieval

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Project Structure

```
linky_app/
├── app.py                  # Streamlit UI
├── linky_agents.py         # LangGraph state, nodes, and workflow definition
├── llm_utils.py            # OpenRouter API integration and LLM calls
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
└── README.md               # Project documentation
```

## Usage

1. **Enter Your Topic**: Describe what you want to post about
2. **Add Custom Content** (Optional): Include your own insights, research, or quotes
3. **Configure Settings**:
   - Select your desired tone (Visionary, Educator, Provocateur, etc.)
   - Choose content types (News Breakdown, Case Study, Personal Story, etc.)
   - Adjust length, engagement level, and narrative patterns
4. **Generate**: Click "Generate LinkedIn Post"
5. **Review & Edit**: Preview your post, make edits if needed
6. **Copy & Share**: Copy to clipboard and post to LinkedIn

## Technology Stack

- **Frontend**: Streamlit
- **Orchestration**: LangGraph
- **LLM Provider**: OpenRouter (Groq/Llama models)
- **Language**: Python 3.8+

## Anti-Slop Principles

Linky adheres to strict quality standards:
- No em-dashes
- Varied sentence structure
- Cohesive and self-explanatory content
- Factual precision & validation
- Human-like nuance
- Output-ready content

## Uniqueness Principles

- Dynamic perspective shifting
- Contextual data integration
- Algorithmic variation
- User-provided content as unique seed

## API Requirements

- **OpenRouter API Key** (Required): Get yours at [OpenRouter](https://openrouter.ai/)
- **News API Key** (Optional): For enhanced news retrieval at [NewsAPI](https://newsapi.org/)

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on the project repository.

---

Built with ❤️ using Antigravity
