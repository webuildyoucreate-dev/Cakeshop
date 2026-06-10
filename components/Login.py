import streamlit as st
import sqlite3
from cryptography.fernet import Fernet

try:
    with open("secret.key", "rb") as key_file:
        secret_key = key_file.read()
except Exception as e:
    st.error(f"Error loading encryption key: {e}")
    st.stop()

cipher_suite = Fernet(secret_key)

def login(user, pwd):
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        # Get the encrypted password from database
        cursor.execute("SELECT pwd FROM users WHERE username = ?", (user,))
        row = cursor.fetchone()
        conn.close()
        
        if row is not None:
            encrypted_pwd = row[0]
            # Decrypt and compare
            decrypted_pwd = cipher_suite.decrypt(encrypted_pwd).decode('utf-8')
            if decrypted_pwd == pwd:
                return True
        return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def login_screen():
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.title(f"Welcome, {st.session_state.username}! 🍰")
        st.write("You are logged in.")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

login_screen()