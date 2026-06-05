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

def logout():
    st.session_state.authenticated = False
    #st.rerun()

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
        logged_in_screen()
        

def logged_in_screen():

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
            st.button("View Orders")
        st.divider()

    if st.session_state.username == "admin":
        st.warning("Admin and manager features are to the left in the sidebar.")
        is_admin_screen()

    st.title("DESSERTS BY DANA")

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
    is_manager_screen()

def is_manager_screen():
    with st.sidebar:
        st.write("Manager Panel")
login_screen()
