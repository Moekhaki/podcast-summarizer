# 🎧 Podcast Summarizer with Chatbot

A powerful podcast analysis tool that transcribes audio, segments it, summarizes each part, extracts insights, and enables interactive Q&A through a chatbot interface. Built with Streamlit and powered by advanced AI models.

## Features

- **Audio Transcription**: Converts MP3/WAV files to text using Whisper
- **Segmentation**: Breaks down long transcripts into digestible chunks
- **Content Analysis**: Extracts key insights and summaries
- **Interactive Chat**: Ask questions about the podcast content
- **MCP Integration**: Tracks all model interactions for transparency
- **Caching System**: Optimizes performance with cached results

## Getting Started

### Prerequisites

- Python 3.10+
- Google API Key (for Gemini)

### Option 1: To run the app locally

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

4. Running the App

```bash
streamlit run app.py
```

### Option 2: To run the app in a Docker container 🐳

1. Build the Docker image:
```bash
docker build -t podcast-summarizer .
```

2. Run the container:
```bash
docker run -p 8501:8501 \
  --env-file .env \
  podcast-summarizer
```

3. Access the application at `http://localhost:8501`

The Docker container includes:
- Python 3.10 slim base image
- FFmpeg for audio processing
- All required Python dependencies
- Exposed port 8501 for Streamlit

Note: Make sure to create the `.env` file with your API keys before building the container.

## Usage

1. Open the app in your browser (typically http://localhost:8501)
2. Upload an MP3 or WAV file
3. Choose whether you want detailed content analysis
4. Click "Process Podcast" to start the analysis
5. View the results:
   - Full transcript
   - Segmented analysis with key insights
   - Ask questions through the chatbot interface
   - Review the MCP context log

## Project Structure

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

## Caching

The application implements caching for:
- Transcriptions
- Content analysis
- Embeddings

This helps improve performance and reduce API costs for repeated operations.

## Model Context Protocol (MCP)

The MCP system tracks all AI model interactions, including:
- Transcription results
- Segmentation operations
- Content analysis
- Chat interactions

This provides transparency and reproducibility of results.

## Development

To contribute:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
