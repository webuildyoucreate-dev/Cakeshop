import streamlit as st
import sqlite3
from cryptography.fernet import Fernet

from components.OrderForm import MakeOrderForm, ViewOrderForm
from components.Login import Login

try:
    with open("secret.key", "rb") as key_file:
        secret_key = key_file.read()
except Exception as e:
    st.error(f"Error loading encryption key: {e}")
    st.stop()

cipher_suite = Fernet(secret_key)
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

def logout():
    st.session_state.authenticated = False

def handle_screens():
    st.set_page_config(
        page_title="Desserts By Dana - Cake Order Form",
        layout="wide"
    )

    with st.sidebar:
        st.title(f"Logged in as: {st.session_state.username}")
        sc1,sc2 = st.columns(2)
        with sc1:
            st.button("Logout", on_click=logout)
        with sc2:
            if st.session_state.screen == "order_form":
                st.button("View Orders", on_click=lambda: st.session_state.update(screen="view_orders"))
            elif st.session_state.screen == "view_orders":
                st.button("Create Order", on_click=lambda: st.session_state.update(screen="order_form"))

    # Fetch roles for the logged in user
    cursor.execute("SELECT store, manager, admin FROM users WHERE username = ?", (st.session_state.username,))
    row = cursor.fetchone()
    user_store = ""
    user_manager = ""
    is_admin = False
    if row:
        user_store, user_manager, admin_flag = row
        is_admin = (admin_flag == 1 or st.session_state.username == "admin")

    if is_admin:
        st.warning("Admin and manager features are to the left in the sidebar.")
        is_admin_screen()
    elif user_manager:
        st.warning("Manager features are to the left in the sidebar.")
        is_manager_screen(user_manager)

    st.title("DESSERTS BY DANA")

    if st.session_state.screen == "order_form":
        MakeOrderForm(st.session_state.username)
    elif st.session_state.screen == "view_orders":
        ViewOrderForm()
    else:
        st.error("Unknown screen. Please select a valid option from the sidebar.")

def login_screen():
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if Login(username, password, cursor, cipher_suite):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        if "screen" not in st.session_state:
            st.session_state.screen = "order_form"
        handle_screens()

def is_admin_screen():
    with st.sidebar:
        st.divider()
        st.write("Admin Panel")
        cursor.execute("SELECT username FROM users")
        admin_search_term = st.text_input("Search users:", placeholder="Type username...", key="admin_search")
        usernames = [row[0] for row in cursor.fetchall() if admin_search_term.lower() in row[0].lower()]
        with st.expander("Admin User View"):
            with st.container(height=300, border=False):
                for username in usernames:
                    with st.container(border=True):
                        c1,c2,c3= st.columns(3)
                        with c1:
                            st.write(username)
                        with c2:
                            with st.popover("Edit User", key = "edit_" + username):
                                st.write("Edit user details here")
                                cursor.execute("SELECT store, manager, admin FROM users WHERE username = ?", (username,))
                                account_details = cursor.fetchone()

                                if account_details[0] == "":
                                    st.checkbox("Store Employee Access(f)", value=False, key=username+"_Store_f")
                                    st.checkbox("Store Employee Access(m)", value=False, key=username+"_Store_m")
                                    st.checkbox("Store Employee Access(b)", value=False, key=username+"_Store_b")
                                else:
                                    if "f" in account_details[0]:
                                        st.checkbox("Store Employee Access(f)", value=True, key=username+"_Store_f")
                                    else:
                                        st.checkbox("Store Employee Access(f)", value=False, key=username+"_Store_f")
                                    if "m" in account_details[0]:
                                        st.checkbox("Store Employee Access(m)", value=True, key=username+"_Store_m")
                                    else:
                                        st.checkbox("Store Employee Access(m)", value=False, key=username+"_Store_m")
                                    if "b" in account_details[0]:
                                        st.checkbox("Store Employee Access(b)", value=True, key=username+"_Store_b")
                                    else:
                                        st.checkbox("Store Employee Access(b)", value=False, key=username+"_Store_b")

                                if account_details[1] == "":
                                    st.checkbox("Store Manager Access(f)", value=False, key=username+"_m_Store_f")
                                    st.checkbox("Store Manager Access(m)", value=False, key=username+"_m_Store_m")
                                    st.checkbox("Store Manager Access(b)", value=False, key=username+"_m_Store_b")
                                else:
                                    if "f" in account_details[1]:
                                        st.checkbox("Store Manager Access(f)", value=True, key=username+"_m_Store_f")
                                    else:
                                        st.checkbox("Store Manager Access(f)", value=False, key=username+"_m_Store_f")
                                    if "m" in account_details[1]:
                                        st.checkbox("Store Manager Access(m)", value=True, key=username+"_m_Store_m")
                                    else:
                                        st.checkbox("Store Manager Access(m)", value=False, key=username+"_m_Store_m")
                                    if "b" in account_details[1]:
                                        st.checkbox("Store Manager Access(b)", value=True, key=username+"_m_Store_b")
                                    else:
                                        st.checkbox("Store Manager Access(b)", value=False, key=username+"_m_Store_b")
                                
                                if account_details[2] == 0:
                                    st.checkbox("Admin", value=False, key=username+"_admin" )
                                elif account_details[2] == 1:
                                    st.checkbox("Admin", value=True, key=username+"_admin" )

                                if st.button("Change Password", key="change_pwd_" + username):
                                    pass

                                if st.button("Save Changes", key="save_" + username):
                                    new_store = ""
                                    new_manager = ""
                                    new_admin = 0

                                    if st.session_state[username+"_Store_f"]:
                                        new_store += "f"
                                    if st.session_state[username+"_Store_m"]:
                                        new_store += "m"
                                    if st.session_state[username+"_Store_b"]:
                                        new_store += "b"

                                    if st.session_state[username+"_m_Store_f"]:
                                        new_manager += "f"
                                    if st.session_state[username+"_m_Store_m"]:
                                        new_manager += "m"
                                    if st.session_state[username+"_m_Store_b"]:
                                        new_manager += "b"

                                    if st.session_state[username+"_admin"]:
                                        new_admin = 1

                                    try:
                                        cursor.execute(
                                            """UPDATE users SET store=?, manager=?, admin=? WHERE username=?""",
                                            (new_store, new_manager, new_admin, username)
                                        )
                                        conn.commit()
                                    except Exception as e:
                                        st.error(f"Error updating user: {e}")
                        with c3:
                            if st.button("Delete User", key="delete_" + username):
                                @st.dialog("Confirm Delete")
                                def confirm_delete():
                                    st.warning(f"Are you sure you want to delete user '{username}'? This action cannot be undone.")
                                    if st.button("Yes, Delete User"):
                                        if username != "admin":
                                            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                                            conn.commit()
                                confirm_delete()

        with st.popover("Add New User"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            if st.button("Create User"):
                hashed_password = cipher_suite.encrypt(new_password.encode('utf-8'))
                try:
                    cursor.execute(
                        "INSERT INTO users (username, pwd) VALUES (?, ?)", 
                        (new_username, hashed_password)
                    )
                    conn.commit()
                    st.success(f"Successfully added user '{new_username}' to the encrypted database!")
                except Exception as e:
                    st.error(f"Error adding user: {e}")
    is_manager_screen("fmb")

def is_manager_screen(manager_stores):
    with st.sidebar:
        st.divider()
        st.write("Manager Panel")
        
        # Fetch all users with their store assignments
        cursor.execute("SELECT username, store FROM users")
        rows = cursor.fetchall()
        
        # Normalize the manager's stores to a set of characters
        mgr_stores = set((manager_stores or "").lower())
        
        # Filter to only employees assigned to the manager's stores
        manager_employees = []
        for username, store in rows:
            emp_stores = set((store or "").lower())
            if mgr_stores & emp_stores:
                manager_employees.append((username, store))
        
        manager_search_term = st.text_input("Search employees:", placeholder="Type username...", key="manager_search")
        
        # Filter by search term
        filtered_employees = [
            (username, store)
            for username, store in manager_employees
            if manager_search_term.lower() in username.lower()
        ]
        
        with st.expander("Manager User View"):
            if not filtered_employees:
                st.write("No employees found.")
            for username, store in filtered_employees:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 2])
                    with c1:
                        st.write(username)
                    with c2:
                        store_display = ", ".join([char.upper() for char in store if char])
                        st.write(f"Stores: {store_display}")
                    with c3:
                        if st.button("View Orders", key=f"view_orders_{username}"):
                            st.session_state.screen = "view_orders"
                            st.session_state.view_orders_employee = username
                            st.rerun()

login_screen()
