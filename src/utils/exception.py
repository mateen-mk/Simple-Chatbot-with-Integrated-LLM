import streamlit as st
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)

def handle_error(e):
    logging.error(f"Error: {str(e)}", exc_info=True)
    st.error(f"An error occurred: {str(e)}")
    st.rerun()