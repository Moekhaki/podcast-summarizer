import streamlit as st
from pathlib import Path
from typing import Tuple, List

from agents.transcriber import Transcriber
from agents.segmenter import Segmenter
from agents.content_analyzer import ContentAnalyzer
from agents.chatbot import ChatBot
from mcp_schema import MCPContext

def init_ui() -> None:
    """Initialize Streamlit UI components"""
    st.set_page_config(page_title="🎧 Podcast Summarizer", layout="wide")
    st.title("Podcast Summarizer")
    st.write("Upload an audio file to transcribe, summarize, and extract key insights.")

def save_uploaded_file(uploaded_file) -> Path:
    """Save uploaded file and return its path"""
    audio_path = Path("sample_inputs") / uploaded_file.name
    audio_path.parent.mkdir(exist_ok=True)
    
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File uploaded: {uploaded_file.name}")
    return audio_path

def process_audio(audio_path: Path, skip_analysis: bool) -> Tuple[str, List[str], List[str]]:
    """Process audio file and return transcript, segments, and analyses"""
    # Transcribe
    with st.spinner("Transcribing..."):
        transcriber = Transcriber()
        transcript = transcriber.transcribe(str(audio_path))
        st.session_state.mcp.add("transcriber", transcript)

    # Segment
    with st.spinner("Segmenting..."):
        segmenter = Segmenter(max_words=150)
        segments = segmenter.segment(transcript)
        st.session_state.mcp.add("segmenter", f"{len(segments)} segments created")

    # Analyze if requested
    analyses = []
    if not skip_analysis:
        with st.spinner("Analyzing content..."):
            analyzer = ContentAnalyzer()
            analyses = analyzer.analyze_all(segments)
            st.session_state.mcp.add("analyzer", "\n".join(analyses))
    else:
        st.session_state.mcp.add("analyzer", "Analysis skipped")

    return transcript, segments, analyses

def display_results(transcript: str, segments: List[str], analyses: List[str], skip_analysis: bool) -> None:
    """Display processing results"""
    # Show transcript
    st.subheader("Full Transcript")
    st.text_area("Transcript", transcript, height=200)

    # Show analyses if available
    if not skip_analysis:
        st.subheader("Segment Analyses")
        with st.expander("Segments:", expanded=False):
            for i, (segment, analysis) in enumerate(zip(segments, analyses)):
                with st.expander(f"Segment {i+1}"):
                    st.markdown(analysis)

def handle_chat(transcript: str, analyses: List[str]) -> None:
    """Handle chat interface and interactions"""
    st.subheader("Ask the Podcast")
    
    # Initialize chatbot
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot()
        st.session_state.chatbot.add_context(transcript, analyses)

    # Handle user input
    user_question = st.text_input("Ask a question based on this episode:")
    if user_question:
        try:
            answer = st.session_state.chatbot.ask(user_question)
            st.session_state.mcp.add("chatbot", f"Q: {user_question}\nA: {answer}")
            st.markdown(f"**Answer:** {answer}")
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")

    # Show chat history
    display_chat_history()

def display_chat_history() -> None:
    """Display chat history if available"""
    if "chatbot" in st.session_state:
        history = st.session_state.chatbot.get_history()
        if history:
            st.subheader("Previous Questions")
            for qa in history:
                with st.expander(f"Q: {qa['question'][:60]}..."):
                    st.markdown(f"**Question:** {qa['question']}")
                    st.markdown(f"**Answer:** {qa['answer']}")

def display_context_log() -> None:
    """Display MCP context log"""
    st.subheader("MCP Context Log")
    for msg in st.session_state.mcp.context:
        st.markdown(f"**{msg.role.upper()}**: {msg.content}")

def main() -> None:
    """Main application flow"""
    init_ui()
    
    # File upload
    uploaded_file = st.file_uploader("Upload MP3 or WAV file", type=["mp3", "wav"])
    if not uploaded_file:
        return

    # Analysis preference
    analysis_preference = st.radio(
        "Would you like detailed content analysis?",
        options=["Yes", "No"],
        index=0,
        help="Choose 'No' for faster processing of longer files"
    )
    skip_analysis = analysis_preference == "No"

    # Process button
    if not st.button("Process Podcast"):
        return

    # Initialize fresh session
    st.session_state.mcp = MCPContext(context=[])
    if "chatbot" in st.session_state:
        del st.session_state.chatbot

    # Process audio
    audio_path = save_uploaded_file(uploaded_file)
    transcript, segments, analyses = process_audio(audio_path, skip_analysis)

    # Display results
    display_results(transcript, segments, analyses, skip_analysis)
    handle_chat(transcript, analyses)
    display_context_log()

if __name__ == "__main__":
    main()
