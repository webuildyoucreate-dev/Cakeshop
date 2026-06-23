import streamlit as st
import sqlite3
import json
from datetime import datetime

CATEGORIES = {
    "Fillings": [
        "Pastry cream",
        "Lemon curd",
        "Cannoli cream"
    ],
    "Miscellaneous": [
        "Glaze",
        "Glitter",
        "Cocoa powder",
        "Mini cannoli shells",
        "Mini cupcake wrappers",
        "Cupcake wrappers",
        "1/2 sheet parchment paper",
        "Large piping bags",
        "Large star tips for Piping"
    ],
    "Toppings": [
        "Reese’s",
        "Snickers",
        "Crushed Oreos",
        "Strawberry crunch",
        "Heath bar",
        "Kit Kat",
        "Biscoff Cookie Butter",
        "Peanut Butter",
        "Cotton candy",
        "Mini marshmallows",
        "Marshmallows",
        "Coconut",
        "Whole Oreos",
        "Lemon sandwich cookies"
    ],
    "Cupcakes": [
        "Vanilla",
        "Chocolate",
        "Red velvet",
        "Strawberry",
        "Funfetti",
        "Cookies and cream",
        "Lemon",
        "Orange",
        "Pumpkin",
        "Apple",
        "Sweet potato",
        "Mint chocolate chip"
    ],
    "Cake towers": [
        "Death By Chocolate",
        "Chocolate Chocolate",
        "Red velvet",
        "Carrot",
        "Cookies and cream",
        "Pineapple coconut",
        "Banana split",
        "Funfetti",
        "Chocolate Peanut Butter",
        "Caramel"
    ],
    "Bundts": [
        "Pineapple upside down",
        "Strawberry",
        "Chocolate Flan",
        "Jewish apple",
        "Lemon Berry"
    ],
    "Other": [
        "Napoleon",
        "Tiramisu",
        "Creme Brulee",
        "Flan",
        "Coconut macaroons",
        "Apple purse"
    ],
    "Tarts": [
        "Key lime",
        "Chocolate caramel",
        "Smores",
        "Pecan",
        "Chocolate pecan",
        "Raspberry elder flower",
        "Apple crumb",
        "Strawberry rhubarb",
        "Sweet potato pie"
    ],
    "Case cakes (6 in)": [
        "Death by Chocolate",
        "Strawberry Crunch",
        "Strawberry Shortcake",
        "Cookies and Cream",
        "Funfetti",
        "Carrot",
        "Vanilla",
        "Coconut pineapple"
    ],
    "Pies": [
        "Apple",
        "Caramel apple",
        "Sweet Potato",
        "Pumpkin",
        "Bourbon Pecan",
        "Chocolate Pecan",
        "Cherry",
        "Peach",
        "Sweet Potato Pecan"
    ],
    "Brownies and bars": [
        "Brownie",
        "Walnut brownie",
        "Cookies and cream brownie",
        "Cookie butter brownie",
        "Lemon bar",
        "Millionaire bar",
        "Peach and blueberry bar"
    ],
    "Parfaits": [
        "Banana puddings",
        "Strawberry shortcake",
        "Tres leches",
        "Pina colada",
        "Lemon Blueberry",
        "Black Forest",
        "Apple cheesecake"
    ]
}

def RequisitionForm(username=None):
    if username is None:
        username = st.session_state.get("username", "Guest")

    st.header("Requisition Form")

    # Initialize Requisitions table
    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                "time created" TEXT DEFAULT CURRENT_TIMESTAMP,
                json TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database error initializing requisitions table: {e}")

    # Success alert across reruns
    if st.session_state.get("requisition_saved"):
        st.success("Requisition saved to database successfully!")
        del st.session_state["requisition_saved"]

    # Form versioning to reset inputs without modifying st.session_state key after instantiation
    if "req_form_id" not in st.session_state:
        st.session_state.req_form_id = 0

    tab_new, tab_past = st.tabs(["New Requisition", "Past Requisitions"])

    with tab_new:
        st.markdown("### Create New Requisition")
        st.write("Enter the quantity needed for each item below, then click **Save Requisition** at the bottom.")

        # Requisition Categories distribution in 3 columns
        col1_categories = ["Fillings", "Miscellaneous", "Toppings"]
        col2_categories = ["Cupcakes", "Cake towers", "Bundts", "Other"]
        col3_categories = ["Tarts", "Case cakes (6 in)", "Pies", "Brownies and bars", "Parfaits"]

        c1, c2, c3 = st.columns(3)

        form_id = st.session_state.req_form_id

        def render_categories(categories, column):
            with column:
                for category in categories:
                    with st.container(border=True):
                        st.markdown(f"#### {category}")
                        for item in CATEGORIES[category]:
                            cols_item = st.columns([3, 1.5])
                            with cols_item[0]:
                                # Clean vertical layout alignment
                                st.markdown(f"<div style='padding-top: 6px;'>{item}</div>", unsafe_allow_html=True)
                            with cols_item[1]:
                                st.number_input(
                                    label=item,
                                    min_value=0,
                                    step=1,
                                    value=0,
                                    key=f"req_{category}_{item}_{form_id}",
                                    label_visibility="collapsed"
                                )

        render_categories(col1_categories, c1)
        render_categories(col2_categories, c2)
        render_categories(col3_categories, c3)

        st.divider()

        if st.button("Save Requisition", type="primary", use_container_width=True):
            # Gather non-zero requisition items
            requisition_data = {}
            for category, items in CATEGORIES.items():
                category_data = {}
                for item in items:
                    qty = st.session_state.get(f"req_{category}_{item}_{form_id}", 0)
                    if qty > 0:
                        category_data[item] = qty
                if category_data:
                    requisition_data[category] = category_data

            if not requisition_data:
                st.warning("Please specify a quantity greater than 0 for at least one item before saving.")
            else:
                try:
                    conn = sqlite3.connect("app.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO requisitions (author, `time created`, json) VALUES (?, ?, ?)",
                        (username, datetime.now().isoformat(), json.dumps(requisition_data))
                    )
                    conn.commit()
                    conn.close()

                    # Increment form version to reset inputs on rerun
                    st.session_state.req_form_id += 1
                    st.session_state.requisition_saved = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving requisition to database: {e}")

    with tab_past:
        st.markdown("### Past Requisitions")
        try:
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, author, `time created`, json FROM requisitions ORDER BY id DESC")
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            st.error(f"Error fetching requisitions: {e}")
            rows = []

        if not rows:
            st.info("No past requisitions found.")
        else:
            for req_id, author, time_created, json_str in rows:
                try:
                    data = json.loads(json_str)
                except Exception as e:
                    data = {"error": f"Invalid JSON: {e}"}

                try:
                    # Clean time display
                    dt = datetime.fromisoformat(time_created)
                    formatted_time = dt.strftime("%b %d, %Y %I:%M %p")
                except:
                    formatted_time = time_created

                with st.expander(f"Requisition #{req_id} | Saved by {author} | {formatted_time}"):
                    for category, items in data.items():
                        if isinstance(items, dict):
                            st.markdown(f"**{category}**")
                            for item, qty in items.items():
                                st.write(f"- {item}: **{qty}**")
                        else:
                            st.write(items)
