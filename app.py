import streamlit as st
from agents.transcriber import Transcriber
from agents.segmenter import Segmenter
from agents.summarizer import Summarizer
from agents.explainer import Explainer
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

        with st.spinner("Summarizing..."):
            summarizer = Summarizer()
            summaries = summarizer.summarize_all(segments)
            st.session_state.summaries = summaries
            st.session_state.mcp.add("summarizer", "\n".join(summaries))

        with st.spinner("Explaining..."):
            explainer = Explainer()
            insights = explainer.explain_all(summaries)
            st.session_state.insights = insights
            st.session_state.mcp.add("explainer", "\n".join(insights))

    # Step 2: Use cached results
    transcript = st.session_state.transcript
    segments = st.session_state.segments
    summaries = st.session_state.summaries
    insights = st.session_state.insights
    mcp = st.session_state.mcp

    # Step 3: Display Results
    st.subheader("Full Transcript")
    st.text_area("Transcript", transcript, height=200)

    st.subheader("Summaries & Insights")
    for i, (seg, summary, insight) in enumerate(zip(segments, summaries, insights)):
        with st.expander(f"Segment {i+1}"):
            st.markdown(f"**📝 Summary:** {summary}")
            st.markdown(f"**💡 Insight:** {insight}")

    # Step 4: Chatbot
    st.subheader("Ask the Podcast")
    user_question = st.text_input("Ask a question based on this episode:")

    if user_question and summaries:
        from agents.chatbot import ChatBot
        chatbot = ChatBot()
        summary_context = "\n".join(summaries)
        answer = chatbot.ask(summary_context, user_question)
        mcp.add("chatbot", f"Q: {user_question}\nA: {answer}")
        st.markdown(f"**Answer:** {answer}")

    # Step 5: Context Log
    st.subheader("📜 MCP Context Log")
    for msg in mcp.context:
        st.markdown(f"**{msg.role.upper()}**: {msg.content}")
