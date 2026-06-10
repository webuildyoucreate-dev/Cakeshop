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
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

def login(user, pwd):
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

def logout():
    st.session_state.authenticated = False
    #st.rerun()

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
        order_form_screen()
    else:
        st.error("Unknown screen. Please select a valid option from the sidebar.")

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
        if "screen" not in st.session_state:
            st.session_state.screen = "order_form"
        handle_screens()
        
def order_form_screen():

    

    # =====================================================
    # TOP CHECKBOXES
    # =====================================================

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        time_confirmed = st.checkbox("Time Confirmed")

    with c2:
        count_confirmed = st.checkbox("Count Confirmed")

    with c3:
        invoice = st.checkbox("Invoice")

    with c4:
        flower_reminder = st.checkbox("Flower/Topper/Stand Reminder")

    with c5:
        save_top_tier = st.checkbox("Save Top Tier")

    with c6:
        topper_venue = st.checkbox("Topper at Venue")

    st.divider()

    # =====================================================
    # CLIENT + VENUE INFORMATION
    # =====================================================

    left, right = st.columns(2)

    with left:
        st.markdown("## CLIENT INFORMATION")

        client_name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")

        c1, c2 = st.columns(2)

        with c1:
            event_date = st.date_input("Event Date")

        with c2:
            guest_count = st.number_input(
                "Amt of ppl",
                min_value=0,
                step=1
            )

        c1, c2 = st.columns(2)

        with c1:
            pickup_delivery = st.selectbox(
                "Delivery or Pick-up",
                ["Delivery", "Pick-up"]
            )

        with c2:
            delivery_time = st.text_input("Delivery Time")

        photographer = st.text_input("Photographer")
        wedding_colors = st.text_input("Wedding Colors")

    with right:
        st.markdown("## VENUE INFORMATION")

        venue_name = st.text_input("Venue / Contact")
        venue_address = st.text_input("Address")
        city_state_zip = st.text_input("City / State / Zip")

        venue_contact = st.text_input("Contact Person / Phone")

        c1, c2 = st.columns(2)

        with c1:
            ceremony_time = st.text_input("Ceremony Time")

        with c2:
            event_time = st.text_input("Event Time")

        florist = st.text_input("Florist")

        flowers_provided = st.radio(
            "Flowers Provided By Couple",
            ["Yes", "No"],
            horizontal=True
        )

    st.divider()

    # =====================================================
    # CAKES
    # =====================================================

    st.markdown("## CAKES")

    cake_count = st.number_input(
        "Number of Cakes",
        min_value=1,
        max_value=100,
        value=1,
        step=1
    )

    cake_data = []

    for cake in range(1, cake_count + 1):

        st.markdown(f"### Cake {cake}")

        # -------------------------------------------------
        # Cake Information
        # -------------------------------------------------

        row1 = st.columns(4)

        with row1[0]:
            size = st.selectbox(
                "Size",
                [ "6 inch", "9 inch"],
                key=f"size_{cake}"
            )

        with row1[1]:
            shape = st.text_input(
                "Shape",
                key=f"shape_{cake}"
            )

        with row1[2]:
            flavor = st.selectbox(
                "Flavor",
                [
                    "Almond",
                    "Amaretto",
                    "Apple Spice",
                    "Banana",
                    "Carrot",
                    "Chocolate",
                    "Chocolate Banana",
                    "Chocolate Hazelnut",
                    "Chocolate Mint",
                    "Cookie Butter",
                    "Cookies 'n Creme",
                    "Funfetti",
                    "Hazelnut",
                    "Key Lime",
                    "Lemon",
                    "Marble",
                    "Mexican Chocolate",
                    "Orange Creamsicle",
                    "Pink Champagne",
                    "Pumpkin",
                    "Raspberry",
                    "Red Velvet",
                    "Strawberry",
                    "Strawberry Banana",
                    "Sweet Potato",
                    "Vanilla",
                    "Vanilla Chocolate Chip"
                ],
                key=f"flavor_{cake}"
        )

        with row1[3]:
            filling = st.selectbox(
                "Filling",
                [
                    "Italian Buttercream",
                    "Almond Cream",
                    "Banana Cream",
                    "Bavarian Cream w/Strawberries",
                    "Cannoli Cream",
                    "Caramel",
                    "Caramelized Pineapple",
                    "Chambord Buttercream",
                    "Chocolate Caramel Mousse",
                    "Chocolate Chambord Mousse",
                    "Chocolate Mousse",
                    "Cookie Butter Mousse",
                    "Cream Cheese",
                    "Grand Marnier",
                    "Lemon Curd",
                    "Lemon Curd with Blueberries",
                    "Mandarin Orange Segment",
                    "Mocha Mousse",
                    "Nutella Mousse"
                    "Orange Marmalade",
                    "Peanut Butter Mousse",
                    "Pistachio Mousse",
                    "Raspberry Preserves",
                    "Salted Chocolate Caramel Mousse",
                    "Strawberry Cream Cheese",
                    "Strawberry Preserves",
                    "Tiramisu Mousse",
                    "White Chocolate Mousse",

                ],
                key=f"filling_{cake}"
            )

        # -------------------------------------------------
        # Appearance
        # -------------------------------------------------

        row2 = st.columns(3)

        with row2[0]:
            finish = st.selectbox(
                "Finish",
                [
                    "Buttercream",
                    "Fondant",
                ],
                key=f"finish_{cake}"
            )

        with row2[1]:
            base_color = st.text_input(
                "Base Color",
                key=f"base_color_{cake}"
            )

        with row2[2]:
            accent_color = st.text_input(
                "Accent Color",
                key=f"accent_color_{cake}"
            )

        # -------------------------------------------------
        # Cake Design Details
        # -------------------------------------------------

        cake_design = st.text_area(
            "Cake Design Details",
            key=f"design_{cake}",
            height=100
        )

        # -------------------------------------------------
        # Store Cake Data
        # -------------------------------------------------

        cake_data.append({
            "cake_number": cake,
            "size": size,
            "shape": shape,
            "flavor": flavor,
            "filling": filling,
            "finish": finish,
            "base_color": base_color,
            "accent_color": accent_color,
            "design_details": cake_design
        })

        st.markdown("---")

    # =====================================================
    # OVERALL ORDER NOTES
    # =====================================================

    st.markdown("### Overall Order Design Notes")

    design_details = st.text_area(
        "",
        height=200,
        key="overall_design_details",
        label_visibility="collapsed"
    )
    # =====================================================
    # PRICING
    # =====================================================

    st.markdown("## PRICING")

    left, right = st.columns(2)

    with left:
        cake_price = st.number_input(
            "Cake Price ($)",
            min_value=0.0,
            step=1.0
        )

        delivery_fee = st.number_input(
            "Delivery ($)",
            min_value=0.0,
            step=1.0
        )

        grand_total = st.number_input(
            "Grand Total ($)",
            min_value=0.0,
            step=1.0
        )

    with right:
        equipment_rental = st.text_input("Equipment Rental")

        deposit_amount = st.number_input(
            "Deposit Amount ($)",
            min_value=0.0,
            step=1.0
        )

        balance_due = st.number_input(
            "Balance Due ($)",
            min_value=0.0,
            step=1.0
        )

        due_dates = st.text_input("Due Date(s)")
        paid_in_full = st.checkbox("Paid in Full")

    c1, c2 = st.columns(2)

    with c1:
        order_taken_by = st.text_input("Order Taken By")

    with c2:
        order_date = st.date_input("Date")

    st.divider()



    # =====================================================
    # FLOWERS / DECOR / STAND
    # =====================================================

    left, right = st.columns(2)

    with left:
        flowers_here = st.text_area(
            "Flowers Here",
            height=120
        )

        other_decor = st.text_area(
            "Other Décor Here",
            height=120
        )

    with right:
        cake_stand = st.text_area(
            "Cake Stand",
            height=260
        )

    st.divider()

    # =====================================================
    # CHECKLIST
    # =====================================================

    st.markdown("## Checklist")

    needed_client = st.checkbox("Items Needed From Client")
    ordered_dbd = st.checkbox("Items To Be Ordered By Desserts By Dana")
    items_received = st.checkbox("Items Received (Date / Initials / Item)")
    equipment_returned = st.checkbox("Equipment Rental Returned To DBD")

    st.divider()

    # =====================================================
    # CIRCLE LOCATION
    # =====================================================

    st.markdown("## Circle Location")

    circle_location = st.radio(
        "",
        ["F", "M", "B"],
        horizontal=True
    )

    st.divider()

    # =====================================================
    # SAVE BUTTON
    # =====================================================

    if st.button("Save Order"):
        st.success("Order information saved.")

def is_admin_screen():
    with st.sidebar:
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
