import streamlit as st
from agents.transcriber import Transcriber
from agents.segmenter import Segmenter
from agents.content_analyzer import ContentAnalyzer
from agents.chatbot import ChatBot
from mcp_schema import MCPContext
import os

# UI Setup
st.set_page_config(page_title="🎧 Podcast Summarizer", layout="wide")
st.title("Podcast Summarizer")
st.write("Upload an audio file to transcribe, summarize, and extract key insights.")

# File uploader
uploaded_file = st.file_uploader("Upload MP3 or WAV file", type=["mp3", "wav"])

if uploaded_file:
    # Step 1: Process once and cache in session
    if "transcript" not in st.session_state:
        audio_path = f"sample_inputs/{uploaded_file.name}"
        os.makedirs("sample_inputs", exist_ok=True)
        with open(audio_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded: {uploaded_file.name}")

        # Create MCP context
        st.session_state.mcp = MCPContext(context=[])
        st.session_state.mcp.add("user", f"Summarize this podcast: {uploaded_file.name}")

        with st.spinner("Transcribing..."):
            transcriber = Transcriber()
            transcript = transcriber.transcribe(audio_path)
            st.session_state.transcript = transcript
            st.session_state.mcp.add("transcriber", transcript)

        with st.spinner("Segmenting..."):
            segmenter = Segmenter(max_words=150)
            segments = segmenter.segment(transcript)
            st.session_state.segments = segments
            st.session_state.mcp.add("segmenter", f"{len(segments)} segments created")

        with st.spinner("Analyzing content..."):
            analyzer = ContentAnalyzer()
            analyses = analyzer.analyze_all(segments)
            st.session_state.analyses = analyses
            st.session_state.mcp.add("analyzer", "\n".join(analyses))

    # Step 2: Use cached results
    transcript = st.session_state.transcript
    segments = st.session_state.segments
    analyses = st.session_state.analyses
    mcp = st.session_state.mcp

    # Step 3: Display Results
    st.subheader("Full Transcript")
    st.text_area("Transcript", transcript, height=200)

    st.subheader("Segment Analyses")
    for i, (segment, analysis) in enumerate(zip(segments, analyses)):
        with st.expander(f"Segment {i+1}"):
            st.markdown(analysis)

    # Step 4: Chatbot
    st.subheader("Ask the Podcast")
    
    # Initialize chatbot only once per session
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatBot()
        # Add context when initializing
        st.session_state.chatbot.add_context(transcript, analyses)

    user_question = st.text_input("Ask a question based on this episode:")

    if user_question:
        try:
            answer = st.session_state.chatbot.ask(user_question)
            mcp.add("chatbot", f"Q: {user_question}\nA: {answer}")
            st.markdown(f"**Answer:** {answer}")
        except Exception as e:
            st.error(f"Error getting response: {str(e)}")
            
    # Display chat history
    if "chatbot" in st.session_state:
        history = st.session_state.chatbot.get_history()
        if history:
            st.subheader("Previous Questions")
            for qa in history:
                with st.expander(f"Q: {qa['question'][:60]}..."):
                    st.markdown(f"**Question:** {qa['question']}")
                    st.markdown(f"**Answer:** {qa['answer']}")

    # Step 5: Context Log
    st.subheader("📜 MCP Context Log")
    for msg in mcp.context:
        st.markdown(f"**{msg.role.upper()}**: {msg.content}")
