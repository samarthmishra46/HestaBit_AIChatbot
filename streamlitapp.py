import streamlit as st
import requests
import uuid
import time
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
import os
import io
from openai import OpenAI
from datetime import datetime

# Initialize OpenAI client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set the backend FastAPI URL
API_URL = "http://127.0.0.1:8003/chat"

# Create audio directory if it doesn't exist
if not os.path.exists("audio_files"):
    os.makedirs("audio_files")

# Session state for session_id and message history
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you today?"}]

st.title("🧠 Memory-Aware Chatbot")
st.write("This chatbot uses Redis (short-term) and FAISS (long-term) memory to enhance responses.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Audio recorder
audio_bytes = audio_recorder("Click to record", pause_threshold=2.0, key="recorder")

# Process audio if recorded
if audio_bytes:
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"audio_files/audio_{st.session_state.session_id}_{timestamp}.mp3"
    
    try:
        # Convert bytes to AudioSegment and save as MP3
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
        audio.export(audio_filename, format="mp3")
        
        # Transcribe audio using OpenAI
        with st.spinner("Transcribing your audio..."):
            with open(audio_filename, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",  # Using Whisper as GPT-4o-transcribe isn't available yet
                    file=audio_file
                )
            transcribed_text = transcription.text
            
        # Add transcribed message to chat history
        st.session_state.messages.append({"role": "user", "content": transcribed_text})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(transcribed_text)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Send to backend
            try:
                res = requests.post(API_URL, json={
                    "prompt": transcribed_text,
                    "session_id": st.session_state.session_id
                })
                res.raise_for_status()
                data = res.json()
                bot_reply = data["response"]
                
                # Simulate stream of response
                for chunk in bot_reply.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                full_response = "Sorry, I encountered an error processing your request."
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        st.error(f"Error processing audio: {e}")
    finally:
        # Delete the audio file after processing
        if os.path.exists(audio_filename):
            os.remove(audio_filename)

# Text input at the bottom
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Send to backend
        try:
            res = requests.post(API_URL, json={
                "prompt": prompt,
                "session_id": st.session_state.session_id
            })
            res.raise_for_status()
            data = res.json()
            bot_reply = data["response"]
            
            # Simulate stream of response
            for chunk in bot_reply.split():
                full_response += chunk + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.05)
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            full_response = "Sorry, I encountered an error processing your request."
            message_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.markdown("---")
st.markdown(f"**Session ID**: `{st.session_state.session_id}`")