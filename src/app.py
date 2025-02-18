import streamlit as st
from src.assistant import DeepSeekAssistant
from src.utils.db import init_db, save_conversation
from src.utils.exception import handle_error
from src.utils.helpers import load_config, get_conversation_id
import asyncio

def main():
    # Initialize application
    config = load_config()
    assistant = DeepSeekAssistant(config)
    asyncio.run(init_db())
    
    # Setup UI
    st.set_page_config(page_title="DeepSeek Chat", layout="wide")
    st.markdown(f'<style>{open("assets/styles.css").read()}</style>', unsafe_allow_html=True)
    
    # Session state initialization
    if 'current_conv' not in st.session_state:
        st.session_state.current_conv = get_conversation_id()
    
    # Sidebar for conversation management
    with st.sidebar:
        st.header("Conversations")
        if st.button("+ New Chat"):
            new_conv_id = get_conversation_id()
            st.session_state.current_conv = new_conv_id
            asyncio.run(save_conversation(new_conv_id))
        
        # Display conversation history
        conversations = asyncio.run(assistant.get_conversation_list())
        for conv in conversations:
            if st.button(f"Chat {conv['id']}"):
                st.session_state.current_conv = conv['id']
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"Chat {st.session_state.current_conv}")
        
        # Display messages
        messages = asyncio.run(assistant.get_messages(st.session_state.current_conv))
        for msg in messages:
            role_class = "user-message" if msg['role'] == 'user' else 'bot-message'
            st.markdown(f"<div class='message {role_class}'>{msg['content']}</div>", 
                       unsafe_allow_html=True)
        
        # Input area
        user_input = st.text_area("Your message:", key="input", 
                                height=100, placeholder="Type your message here...")
        
        # Action buttons
        if st.button("Send", key="send"):
            if user_input.strip():
                try:
                    asyncio.run(assistant.process_input(
                        st.session_state.current_conv,
                        user_input
                    ))
                    st.rerun()
                except Exception as e:
                    handle_error(e)
        
        if st.button("Clear", key="clear"):
            asyncio.run(assistant.clear_conversation(st.session_state.current_conv))
            st.rerun()
    
    with col2:
        st.header("Settings")
        # Model parameters
        new_temp = st.slider("Temperature", 0.0, 1.0, 
                            float(config['model']['temperature']), 0.1)
        if new_temp != config['model']['temperature']:
            assistant.update_parameters(temperature=new_temp)