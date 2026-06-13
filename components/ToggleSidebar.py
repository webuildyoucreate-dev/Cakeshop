import streamlit as st

def ToggleSidebar():
    if st.session_state.sidebar_state == "collapsed":
        st.session_state.sidebar_state = "expanded"
    else:
        st.session_state.sidebar_state = "collapsed"