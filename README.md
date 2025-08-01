# 🎧 Podcast Summarizer with Chatbot

A powerful podcast analysis tool that transcribes audio, segments it, summarizes each part, extracts insights, and enables interactive Q&A through a chatbot interface. Built with Streamlit and powered by advanced AI models.

## 🌟 Features

- **Audio Transcription**: Converts MP3/WAV files to text using Whisper
- **Smart Segmentation**: Breaks down long transcripts into digestible chunks
- **Content Analysis**: Extracts key insights and summaries using Gemini
- **Interactive Chat**: Ask questions about the podcast content
- **MCP Integration**: Tracks all model interactions for transparency
- **Caching System**: Optimizes performance with cached results

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Google API Key (for Gemini)

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd podcast-summarizer
```

2. Create a `.env` file with your API keys:
```bash
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash  # Optional, this is the default
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

## 📖 Usage

1. Open the app in your browser (typically http://localhost:8501)
2. Upload an MP3 or WAV file
3. Choose whether you want detailed content analysis
4. Click "Process Podcast" to start the analysis
5. View the results:
   - Full transcript
   - Segmented analysis with key insights
   - Ask questions through the chatbot interface
   - Review the MCP context log

## 🏗️ Project Structure

```
.
├── agents/
│   ├── chatbot.py           # Q&A functionality
│   ├── content_analyzer.py   # Content analysis using Gemini
│   ├── segmenter.py         # Text segmentation
│   └── transcriber.py       # Audio transcription
├── utils/
│   └── caching.py           # Caching utilities
├── app.py                   # Main Streamlit application
├── mcp_schema.py           # Model Context Protocol implementation
└── requirements.txt        # Project dependencies
```

## 💾 Caching

The application implements caching for:
- Transcriptions
- Content analysis
- Embeddings

This helps improve performance and reduce API costs for repeated operations.

## 📋 Model Context Protocol (MCP)

The MCP system tracks all AI model interactions, including:
- Transcription results
- Segmentation operations
- Content analysis
- Chat interactions

This provides transparency and reproducibility of results.

## 🔨 Development

To contribute:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License

