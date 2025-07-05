# 🎧 Podcast Summarizer with Chatbot

This project is a podcast analysis tool built using the Model Context Protocol (MCP). It transcribes audio, segments it, summarizes each part, extracts insights, and allows you to ask questions via an interactive chatbot.

---

## Features

-  Transcribe MP3/WAV podcast episodes using Whisper
-  Segment the transcript into manageable chunks
-  Summarize each segment using a Hugging Face summarization model
-  Extract key insights
-  Ask questions via a chatbot (powered by Mistral 7B Instruct)
-  All interactions tracked using MCP

---

## Run with Docker

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/podcast-summarizer-mcp.git
cd podcast-summarizer-mcp
```

### 2. Set your Hugging Face API Token

Create a `.env` file or set an environment variable:

```bash
export HUGGINGFACE_API_TOKEN=your_token_here
```

> You can get a token from: https://huggingface.co/settings/tokens

### 3. Build the Docker image

```bash
docker build -t podcast-summarizer .
```

### 4. Run the container

```bash
docker run -it --rm -p 8501:8501 \
  -v $(pwd)/sample_inputs:/app/sample_inputs \
  -e HUGGINGFACE_API_TOKEN=$HUGGINGFACE_API_TOKEN \
  podcast-summarizer
```

---

## Usage Instructions

1. Start the Docker container (as above)
2. Open your browser and go to: `http://localhost:8501`
3. Upload an `.mp3` or `.wav` file (under `sample_inputs`)
4. The app will:
   - Transcribe it
   - Segment and summarize it
   - Extract insights
   - Allow you to ask follow-up questions

---

## 📁 File Structure

```
.
├── app.py                     # Streamlit UI
├── agents/
│   ├── transcriber.py
│   ├── segmenter.py
│   ├── summarizer.py
│   ├── explainer.py
│   └── chatbot.py
├── mcp_schema.py              # Model Context Protocol (MCP)
├── sample_inputs/             # Drop audio files here
├── requirements.txt
└── Dockerfile
```

---

## MCP

The Model Context Protocol tracks all interactions:
- Who did what (`transcriber`, `summarizer`, `chatbot`, etc.)
- What content was processed
- Everything is stored in a single context list for reproducibility

---

## TODO

- Add downloadable report
- Support multi-turn chatbot sessions
- Save MCP context to disk

---

## License

MIT License

