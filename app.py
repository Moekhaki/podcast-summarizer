import streamlit as st
from pathlib import Path
from typing import Tuple, List

from agents.transcriber import Transcriber
from agents.segmenter import Segmenter
from agents.content_analyzer import ContentAnalyzer
from agents.chatbot import ChatBot
from mcp_schema import MCPContext

def init_ui():
    st.set_page_config(page_title="🎧 Podcast Summarizer", layout="wide")
    st.title("Podcast Summarizer")
    st.write("Upload an audio file to transcribe, summarize, and extract key insights.")

def init_session_state():
    """Initialize session state variables"""
    if "mcp" not in st.session_state:
        st.session_state.mcp = MCPContext()
    if "audio_processed" not in st.session_state:
        st.session_state.audio_processed = False

def save_uploaded_file(uploaded_file) -> Path:
    audio_path = Path("sample_inputs") / uploaded_file.name
    audio_path.parent.mkdir(exist_ok=True)
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File uploaded: {uploaded_file.name}")
    return audio_path

def process_audio(audio_path: Path, skip_analysis: bool) -> Tuple[str, List[str], List[str], str]:
    """Process audio file and return results"""
    # Remove the MCP initialization here since it's already done in init_session_state()
    
    with st.spinner("Transcribing and generating embeddings..."):
        transcriber = Transcriber()
        results = transcriber.transcribe_and_embed(str(audio_path))
        transcript = results["transcript"]
        file_id = results["file_id"]
        st.session_state.mcp.add("transcriber", transcript)

    with st.spinner("Segmenting..."):
        segmenter = Segmenter(max_words=150)
        segments = segmenter.segment(transcript)
        st.session_state.mcp.add("segmenter", "\n\n".join(segments))

    analyses = []
    if not skip_analysis:
        with st.spinner("Analyzing content..."):
            analyzer = ContentAnalyzer()
            analyses = analyzer.analyze_all(segments)
            st.session_state.mcp.add("analyzer", "\n\n".join(analyses))

    return transcript, segments, analyses, file_id

def display_results(transcript: str, segments: List[str], analyses: List[str], skip_analysis: bool):
    st.subheader("Full Transcript")
    st.text_area("Transcript", transcript, height=200)

    if not skip_analysis:
        st.subheader("Segment Analyses")
        with st.expander("Segments:", expanded=False):
            for i, (segment, analysis) in enumerate(zip(segments, analyses)):
                with st.expander(f"Segment {i+1}"):
                    st.markdown(analysis)

def handle_chat(transcript: str, file_id: str):
    st.subheader("Ask the Podcast")

    # Initialize chatbot on first use after processing
    if "chatbot" not in st.session_state:
        chatbot = ChatBot()
        chatbot.add_context(transcript, file_id=file_id)
        st.session_state.chatbot = chatbot

    # Display chat form
    with st.form(key="chat_form", clear_on_submit=True):
        user_question = st.text_input("Ask a question based on this episode:", key="question_input")
        submit = st.form_submit_button("Ask")

        if submit and user_question:
            try:
                answer = st.session_state.chatbot.ask(user_question)
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                st.session_state.chat_history.append({"question": user_question, "answer": answer})
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

    display_chat_history()

def display_chat_history():
    if "chat_history" in st.session_state and st.session_state.chat_history:
        st.subheader("Previous Questions")
        for qa in reversed(st.session_state.chat_history):
            with st.expander(f"Q: {qa['question'][:60]}..."):
                st.markdown(f"**Question:** {qa['question']}")
                st.markdown(f"**Answer:** {qa['answer']}")

def display_context_log():
    with st.expander("MCP Context Log", expanded=False):
        if "mcp" in st.session_state:
            for msg in st.session_state.mcp.context:
                st.markdown(f"**{msg.role.upper()}**: {msg.content}")
        else:
            st.info("No MCP context available yet.")

def main():
    init_ui()

    # Initialize session state
    init_session_state()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload MP3 or WAV file", type=["mp3", "wav"])
    if uploaded_file:
        # Determine if a new file was uploaded (reset everything)
        file_changed = (
            "last_uploaded_file" not in st.session_state
            or st.session_state.last_uploaded_file != uploaded_file.name
        )

        if file_changed:
            # Reset session state for new file
            for key in [
                "transcript", "segments", "analyses",
                "chatbot", "chat_history", "mcp", 
                "audio_processed", "file_id"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.last_uploaded_file = uploaded_file.name
            # Reinitialize session state
            init_session_state()

        # Analysis preference
        analysis_preference = st.radio(
            "Would you like detailed content analysis?",
            options=["Yes", "No"],
            index=0,
            help="Choose 'No' for faster processing of longer files"
        )
        skip_analysis = analysis_preference == "No"

        # Processing button
        if st.button("Process Podcast") or st.session_state.get("audio_processed"):
            if not st.session_state.get("audio_processed"):
                audio_path = save_uploaded_file(uploaded_file)
                transcript, segments, analyses, file_id = process_audio(audio_path, skip_analysis)
                # Save all results to session state
                st.session_state.transcript = transcript
                st.session_state.segments = segments
                st.session_state.analyses = analyses
                st.session_state.file_id = file_id
                st.session_state.audio_processed = True
                # Optionally, also log to MCPContext (not shown here, add if needed)

            # Display all outputs
            display_results(
                st.session_state.transcript,
                st.session_state.segments,
                st.session_state.analyses,
                skip_analysis
            )
            handle_chat(
                st.session_state.transcript,
                st.session_state.file_id
            )
            display_context_log()

if __name__ == "__main__":
    main()
