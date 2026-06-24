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

    st.markdown("### Create New Requisition")
    st.write("Enter the quantity needed for each item below, then click **Save Requisition** at the bottom.")

    # From / To location
    loc_col1, loc_col2 = st.columns(2)
    with loc_col1:
        from_location = st.text_input("From Location", placeholder="e.g. Main Kitchen", key=f"req_from_loc_{st.session_state.req_form_id}")
    with loc_col2:
        to_location = st.text_input("To Location", placeholder="e.g. Store F", key=f"req_to_loc_{st.session_state.req_form_id}")

    st.divider()

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
        requisition_data = {
            "_meta": {
                "from_location": from_location,
                "to_location": to_location,
            }
        }
        for category, items in CATEGORIES.items():
            category_data = {}
            for item in items:
                qty = st.session_state.get(f"req_{category}_{item}_{form_id}", 0)
                if qty > 0:
                    category_data[item] = qty
            if category_data:
                requisition_data[category] = category_data

        has_items = any(k != "_meta" for k in requisition_data)
        if not has_items:
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


def ViewRequisitionForm():
    """Renders the past requisitions list with search, filter, and sort. Can be standalone or embedded in a tab."""
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
        return

    # ── Search bar ──────────────────────────────────────────────────────────
    st.subheader("🔍 Search and Filter Requisitions")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "Search",
            placeholder="Search by author, category, or item name...",
            label_visibility="collapsed",
            key="req_viewer_search_input"
        )
    with col2:
        st.markdown(
            f"<div style='text-align: right; color: gray; padding-top: 5px; font-weight: bold;'>"
            f"Total: {len(rows)} requisitions</div>",
            unsafe_allow_html=True
        )

    # ── Filter & Sort expander ───────────────────────────────────────────────
    with st.expander("Filter & Sort Options", expanded=False):
        f_col1, f_col2 = st.columns(2)

        with f_col1:
            unique_authors = sorted(list(set(author for _, author, _, _ in rows if author)))
            author_options = ["All"] + unique_authors
            selected_author = st.selectbox(
                "Created By (Author)",
                author_options,
                key="req_viewer_author_select"
            )

        with f_col2:
            sort_option = st.selectbox(
                "Sort By",
                [
                    "Date Created (Newest First)",
                    "Date Created (Oldest First)",
                ],
                key="req_viewer_sort_select"
            )

        date_col1, date_col2 = st.columns([1, 2])
        with date_col1:
            use_date_filter = st.selectbox(
                "Date Filter",
                ["No Date Filter", "Filter by Date Created"],
                key="req_viewer_date_filter_type"
            )
        with date_col2:
            if use_date_filter != "No Date Filter":
                date_range = st.date_input(
                    "Select Date Range (Start & End)",
                    value=[],
                    key="req_viewer_date_range"
                )
            else:
                date_range = []

        if st.button("Reset Filters", use_container_width=True, key="req_viewer_reset_btn"):
            st.rerun()

    # ── Apply search / filters / sort ────────────────────────────────────────
    def matches_search(author, data, query):
        if not query:
            return True
        query = query.lower()
        if query in (author or "").lower():
            return True
        for category, items in data.items():
            if query in category.lower():
                return True
            if isinstance(items, dict):
                for item_name in items:
                    if query in item_name.lower():
                        return True
        return False

    filtered = []
    for req_id, author, time_created, json_str in rows:
        try:
            data = json.loads(json_str)
        except Exception:
            data = {}

        # Text search
        if search_query and not matches_search(author, data, search_query):
            continue

        # Author filter
        if selected_author != "All" and author != selected_author:
            continue

        # Date filter
        if use_date_filter != "No Date Filter" and date_range:
            if isinstance(date_range, (list, tuple)) and len(date_range) > 0:
                start_date = date_range[0]
                end_date = date_range[1] if len(date_range) == 2 else date_range[0]
                date_to_compare = None
                try:
                    date_str = time_created.split("T")[0]
                    date_to_compare = datetime.strptime(date_str, "%Y-%m-%d").date()
                except Exception:
                    pass
                if date_to_compare is None or not (start_date <= date_to_compare <= end_date):
                    continue

        filtered.append((req_id, author, time_created, data))

    # Sort
    if sort_option == "Date Created (Newest First)":
        filtered.sort(key=lambda x: x[2] or "", reverse=True)
    else:
        filtered.sort(key=lambda x: x[2] or "", reverse=False)

    # ── Results ──────────────────────────────────────────────────────────────
    if not filtered:
        st.info("No requisitions found matching your search and filter criteria.")
        return

    st.success(f"Showing {len(filtered)} of {len(rows)} requisitions")

    for req_id, author, time_created, data in filtered:
        try:
            dt = datetime.fromisoformat(time_created)
            formatted_time = dt.strftime("%b %d, %Y %I:%M %p")
        except Exception:
            formatted_time = time_created

        with st.expander(f"Requisition #{req_id} | Saved by {author} | {formatted_time}"):
            meta = data.get("_meta", {})
            from_loc = meta.get("from_location", "")
            to_loc = meta.get("to_location", "")
            if from_loc or to_loc:
                loc_c1, loc_c2 = st.columns(2)
                with loc_c1:
                    st.text_input("From Location", value=from_loc, disabled=True, key=f"view_from_{req_id}")
                with loc_c2:
                    st.text_input("To Location", value=to_loc, disabled=True, key=f"view_to_{req_id}")
                st.divider()
            for category, items in data.items():
                if category == "_meta":
                    continue
                if isinstance(items, dict):
                    st.markdown(f"**{category}**")
                    for item, qty in items.items():
                        st.write(f"- {item}: **{qty}**")
                else:
                    st.write(items)
