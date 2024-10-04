import streamlit as st

def initialize_session():
    if 'page' not in st.session_state:
        st.session_state.page = "welcome"
    if 'unique_code' not in st.session_state:
        st.session_state.unique_code = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'vs_data' not in st.session_state:
        st.session_state.vs_data = None

def collect_session_data():
    return {
        'unique_code': st.session_state.get('unique_code'),
        'user_name': st.session_state.get('user_name'),
        'vs_data': st.session_state.get('vs_data'),
        'page': st.session_state.get('page'),
    }



