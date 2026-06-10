import sqlite3
from cryptography.fernet import Fernet
import streamlit as st



def Login(user, pwd, cursor, cipher_suite):
    try:
        # Get the encrypted password from database
        cursor.execute("SELECT pwd FROM users WHERE username = ?", (user,))
        row = cursor.fetchone()
        
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