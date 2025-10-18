try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3


import streamlit as st
from streamlit import spinner

from agent import (
    extract_video_id,
    get_transcript,
    translate_transcript,
    generate_notes,
    get_important_topics,
    create_chunks,
    create_vector_store,
    rag_answer
)

# Page configuration
st.set_page_config(
    page_title="YouTube AI Suite",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

USER_AVATAR = "👥"
BOT_AVATAR = "✨"
# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
        
    .stTextInput > div > div > input {
    color: #000000 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Title styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1e40af, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Card styling */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .result-card h3 {
        color: #1e40af;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(120deg, #10b981, #059669);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(16,185,129,0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        color=#000000;
    }
    
    /* Radio button styling */
    .stRadio > label {
        font-weight: 600;
        color: white;
        font-size: 1rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 1rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Success message styling */
    .element-container:has(.stSuccess) {
        margin-top: 1rem;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border-color: #e2e8f0;
    }
    
    /* Feature card */
    .feature-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
   
    st.markdown("##### Created with ❤️ by Lakhan")

    st.markdown("### 🎬 AI Video Suite")
    st.markdown("<hr style='margin: 1rem 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    
    st.markdown("##### Transform YouTube videos into:")
    st.markdown("• 📝 Structured notes")
    st.markdown("• 💬 Interactive chatbot")
    st.markdown("• 🎯 Key topic extraction")
    
    st.markdown("<hr style='margin: 1.5rem 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("### Input Configuration")

    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste the full YouTube video URL here"
    )
    
    language = st.text_input(
        "Video Language Code",
        placeholder="e.g., en, hi, es, fr",
        value="en",
        help="Enter the 2-letter language code"
    )

    st.markdown("### Select Task")
    task_option = st.radio(
        "Choose generation mode:",
        ["Chat with Video", "Notes For You"],
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.button("✨ Start Processing", type="primary")
    
    st.markdown("<hr style='margin: 1.5rem 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("##### 🔧 Version 1.0")
    st.markdown("##### Made with ❤️ using Streamlit")

# --- Main Page ---
st.markdown("<h1 class='main-title'>YouTube Content Synthesizer</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Harness AI to extract insights, generate notes, and chat with any YouTube video</p>", unsafe_allow_html=True)

# Welcome section
if not submit_button and "vector_store" not in st.session_state:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='feature-box'>
                <h3>📝 Smart Notes Generation</h3>
                <p>Automatically extract key topics and generate comprehensive notes from any YouTube video in seconds.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='feature-box'>
                <h3>🌐 Multi-Language Support</h3>
                <p>Process videos in any language with automatic translation to English for analysis.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='feature-box'>
                <h3>💬 Interactive Chat</h3>
                <p>Ask questions about the video content and get instant, context-aware answers powered by AI.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='feature-box'>
                <h3>⚡ Fast Processing</h3>
                <p>Advanced RAG technology ensures quick and accurate responses to your queries.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 Enter a YouTube URL in the sidebar and select your preferred task to get started!")

# --- Processing Flow ---
if submit_button:
    if youtube_url and language:
        video_id = extract_video_id(youtube_url)
        if video_id:
            # Create progress container
            progress_container = st.container()
            
            with progress_container:
                with st.spinner("🎥 Step 1/3 : Fetching transcript from YouTube..."):
                    full_transcript = get_transcript(video_id, language)

                    if language != "en":
                        with st.spinner("🌐 Step 1.5/3 : Translating transcript to English..."):
                            full_transcript = translate_transcript(full_transcript)
                            st.success("✅ Translation completed!")

            if task_option == "Notes For You":
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    with st.spinner("🎯 Step 2/3: Extracting important topics..."):
                        import_topics = get_important_topics(full_transcript)
                    
                    st.markdown("""
                        <div class='result-card'>
                            <h3>🎯 Important Topics</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(import_topics)

                with col2:
                    with st.spinner("📝 Generating comprehensive notes..."):
                        notes = generate_notes(full_transcript)
                    
                    st.markdown("""
                        <div class='result-card'>
                            <h3>📝 Your Notes</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(notes)

                st.success("✅ Summary and notes generated successfully!")

            if task_option == "Chat with Video":
                with st.spinner("🔧 Step 2/3: Preparing video for interactive chat..."):
                    chunks = create_chunks(full_transcript)
                    vectorstore = create_vector_store(chunks)
                    st.session_state.vector_store = vectorstore
                    st.session_state.messages = []
                
                st.success("✅ Video is ready for chat! Start asking questions below.")
        else:
            st.error("❌ Invalid YouTube URL. Please check and try again.")
    else:
        st.warning("⚠️ Please provide both YouTube URL and language code.")

# --- Chatbot Session ---
if task_option == "Chat with Video" and "vector_store" in st.session_state:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #1e40af; margin-bottom: 1.5rem;'>💬 Chat with Video</h2>", unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.get('messages', []):
        avatar = USER_AVATAR if message['role'] == 'user' else BOT_AVATAR
        with st.chat_message(message['role'], avatar=avatar):
            st.write(message['content'])

    # User input
    prompt = st.chat_input("Ask me anything about the video...")
    if prompt:
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message('user', avatar=USER_AVATAR):
            st.write(prompt)

        with st.chat_message('assistant', avatar=BOT_AVATAR):
            with st.spinner("🤔 Thinking..."):
                response = rag_answer(prompt, st.session_state.vector_store)
            st.write(response)
        st.session_state.messages.append({'role': 'assistant', 'content': response})
