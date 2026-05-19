import streamlit as st
import pandas as pd
import sqlite3
import json
import os

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# --- Database Helpers ---
def update_quote(quote_id, name, email, phone, date, cart_json):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE quotes 
        SET name = ?, email = ?, phone = ?, date = ?, cart = ?
        WHERE id = ?
    """, (name, email, phone, date, cart_json, quote_id))
    conn.commit()
    conn.close()
    load_data.clear()

def delete_quote(quote_id):
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    conn.close()
    load_data.clear()

# --- CSV Data Loaders ---
@st.cache_data(ttl=60)
def get_fillings():
    try:
        df = pd.read_csv("csv-folder/fillings.csv")
        return df['Name'].dropna().tolist()
    except Exception:
        return []

@st.cache_data(ttl=60)
def get_flavors():
    try:
        df = pd.read_csv("csv-folder/menu-items.csv")
        return df.iloc[:, 0].dropna().tolist()
    except Exception:
        return []

@st.dialog("Edit Order Details", width="large")
def edit_dialog(quote_row):
    quote_id = quote_row['id']
    state_key = f"edit_cart_{quote_id}"
    
    # Initialize session state for this specific quote if it doesn't exist
    if state_key not in st.session_state:
        try:
            st.session_state[state_key] = json.loads(quote_row['cart'])
        except json.JSONDecodeError:
            st.session_state[state_key] = []
            
    st.subheader("Customer Details")
    new_name = st.text_input("Name", value=quote_row['name'])
    new_email = st.text_input("Email", value=quote_row['email'])
    new_phone = st.text_input("Phone", value=quote_row['phone'])
    new_date = st.text_input("Event Date", value=quote_row['date'])
    
    st.subheader("Cart Items")
    fillings_list = get_fillings()
    finish_options = ["Buttercream", "Fondant", "Naked", "Semi-Naked", "Other"]
    
    cart_items = st.session_state[state_key]
    
    for i, item in enumerate(cart_items):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**Item {i+1}**")
        with col2:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state[state_key].pop(i)
                st.rerun()
                
        # We need to update the item dictionary directly when inputs change
        item['name'] = st.text_input(f"Flavor / Product Name (Item {i+1})", value=item.get('name', ''), key=f"name_{i}")
        item['note'] = st.text_area(f"Note (Item {i+1})", value=item.get('note', ''), key=f"note_{i}")
        
        opts = item.get('options', {})
        st.markdown("**Options:**")
        
        # Finish
        current_finish = opts.get("Finish", "Buttercream")
        if current_finish not in finish_options:
            finish_options.append(current_finish)
        new_finish = st.selectbox(f"Finish (Item {i+1})", options=finish_options, index=finish_options.index(current_finish), key=f"finish_{i}")
        opts["Finish"] = new_finish
        
        # Fillings
        current_fillings_str = opts.get("Fillings", "")
        current_fillings = [f.strip() for f in current_fillings_str.split(",")] if current_fillings_str else []
        # Ensure current fillings are in the list
        for f in current_fillings:
            if f and f not in fillings_list:
                fillings_list.append(f)
        new_fillings = st.multiselect(f"Fillings (Item {i+1})", options=fillings_list, default=[f for f in current_fillings if f], key=f"fillings_{i}")
        if new_fillings:
            opts["Fillings"] = ", ".join(new_fillings)
        else:
            opts.pop("Fillings", None)
            
        # Colors
        new_base = st.text_input(f"Base Color (Item {i+1})", value=opts.get("Base Color", ""), key=f"base_color_{i}")
        if new_base:
            opts["Base Color"] = new_base
        else:
            opts.pop("Base Color", None)
            
        new_accent = st.text_input(f"Accent Color (Item {i+1})", value=opts.get("Accent Color", ""), key=f"accent_color_{i}")
        if new_accent:
            opts["Accent Color"] = new_accent
        else:
            opts.pop("Accent Color", None)
            
        # Inspiration ID
        if "Inspiration ID" in opts:
            st.caption(f"Inspiration ID attached: {opts['Inspiration ID']}")
            
        item['options'] = opts
        st.divider()

    # Add item button
    if st.button("➕ Add Cart Item"):
        st.session_state[state_key].append({
            "name": "New Item (Size)",
            "note": "",
            "options": {"Finish": "Buttercream"}
        })
        st.rerun()

    st.write("")
    if st.button("Save Changes", type="primary"):
        update_quote(quote_id, new_name, new_email, new_phone, new_date, json.dumps(st.session_state[state_key]))
        if state_key in st.session_state:
            del st.session_state[state_key]
        st.success("Order updated!")
        st.rerun()

@st.dialog("Delete Order")
def delete_dialog(quote_id, name):
    st.warning(f"Are you sure you want to delete the order for {name}? This cannot be undone.")
    if st.button("Yes, Delete"):
        delete_quote(quote_id)
        st.success("Order deleted!")
        st.rerun()

# --- Fetch Data ---
@st.cache_data(ttl=5) # Cache for 5 seconds to prevent constant DB reads on interaction, but refresh quickly
def load_data():
    conn = sqlite3.connect("quotes.db")
    df = pd.read_sql_query("SELECT * FROM quotes ORDER BY submitted_at DESC", conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load database: {e}")
    st.stop()

if df.empty:
    st.info("No quote requests have been submitted yet.")
    st.stop()

# --- Filters & Search ---
with st.expander("Filters & Search", expanded=False):
    with st.form("search_form", border=False):
        search_query = st.text_input("Search (Name, Email, Phone)")
        
        col1, col2 = st.columns(2)
        
        # Date Submitted filter
        min_submit = pd.to_datetime(df['submitted_at']).min().date()
        max_submit = pd.to_datetime(df['submitted_at']).max().date()
        with col1:
            submit_date_range = st.date_input(
                "Date Submitted",
                value=(min_submit, max_submit),
                min_value=min_submit,
                max_value=max_submit
            )

        # Event Date filter
        df['event_date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
        valid_dates = df['event_date_parsed'].dropna()
        with col2:
            if not valid_dates.empty:
                min_event = valid_dates.min().date()
                max_event = valid_dates.max().date()
                event_date_range = st.date_input(
                    "Event Date",
                    value=(min_event, max_event),
                    min_value=min_event,
                    max_value=max_event
                )
            else:
                event_date_range = None
                
        submitted = st.form_submit_button("Search")

# Apply filters
filtered_df = df.copy()

if search_query:
    query = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['name'].str.lower().str.contains(query, na=False) |
        filtered_df['email'].str.lower().str.contains(query, na=False) |
        filtered_df['phone'].astype(str).str.contains(query, na=False)
    ]

if len(submit_date_range) == 2:
    start_date, end_date = submit_date_range
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df['submitted_at']).dt.date >= start_date) & 
        (pd.to_datetime(filtered_df['submitted_at']).dt.date <= end_date)
    ]

if event_date_range and len(event_date_range) == 2:
    start_event, end_event = event_date_range
    filtered_df = filtered_df[
        (filtered_df['event_date_parsed'].dt.date >= start_event) & 
        (filtered_df['event_date_parsed'].dt.date <= end_event)
    ]

# --- Scrollable Detailed View ---
st.header("Orders List")
st.write(f"Showing {len(filtered_df)} orders based on filters")

# Container for orders (border removed as requested)
with st.container():
    if filtered_df.empty:
        st.info("No orders match the selected filters.")
    else:
        for _, quote_row in filtered_df.iterrows():
            date_str = pd.to_datetime(quote_row['submitted_at']).strftime('%b %d, %Y %H:%M')
            
            # Extract cake flavors
            cake_flavors = "No Items"
            try:
                cart_items = json.loads(quote_row['cart'])
                if cart_items:
                    cake_flavors = ", ".join([item.get('name', 'Unknown Item') for item in cart_items])
            except json.JSONDecodeError:
                cake_flavors = "Invalid Cart Data"
                cart_items = []
                
            # Create the card layout
            with st.container(border=True):
                # Layout the main card information
                col1, col2, col3 = st.columns([1, 1, 3])
                
                # Try to get first item's images
                prod_img = "images/vanilla_bean_cake.png"
                insp_img = None
                
                if cart_items:
                    first_item = cart_items[0]
                    # Product image
                    image_src = first_item.get("imageSrc", "")
                    if image_src and os.path.exists(image_src):
                        prod_img = image_src
                        
                    # Insp image
                    opts = first_item.get('options', {})
                    insp_id = opts.get("Inspiration ID")
                    if insp_id:
                        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                            pot_path = os.path.join("images", f"insp_{insp_id}{ext}")
                            if os.path.exists(pot_path):
                                insp_img = pot_path
                                break
                
                with col1:
                    st.image(prod_img, use_container_width=True)
                    
                with col2:
                    if insp_img:
                        st.image(insp_img, use_container_width=True)
                    else:
                        st.caption("No inspiration picture provided.")
                        
                with col3:
                    st.subheader(quote_row['name'])
                    st.markdown(f"**Email:** {quote_row['email']} &nbsp;|&nbsp; **Phone:** {quote_row['phone']}")
                    st.markdown(f"**Submitted:** {date_str} &nbsp;|&nbsp; **Event Date:** {quote_row['date']}")
                    st.markdown(f"**Flavors:** {cake_flavors}")
                    
                    st.write("")
                    btn_c1, btn_c2, _ = st.columns([1, 1, 3])
                    if btn_c1.button("Edit Order", key=f"edit_{quote_row['id']}"):
                        edit_dialog(quote_row)
                    if btn_c2.button("Delete", key=f"del_{quote_row['id']}"):
                        delete_dialog(quote_row['id'], quote_row['name'])
                
                # Expandable details
                with st.expander("View Specific Details", expanded=False):
                    st.write("### Cart Items")
                    
                    if not cart_items:
                        st.info("Cart was empty or invalid.")
                    else:
                        for i, item in enumerate(cart_items):
                            st.markdown(f"**{i+1}. {item.get('name', 'Unknown Item')}**")
                            
                            # Display product image
                            image_src = item.get("imageSrc", "")
                            fallback = "images/vanilla_bean_cake.png"
                            if image_src and os.path.exists(image_src):
                                st.image(image_src, width=200)
                            elif os.path.exists(fallback):
                                st.image(fallback, width=200)
                            
                            # Check for note
                            if item.get('note'):
                                st.markdown(f"**Note:** {item['note']}")
                            
                            # Check for options
                            options = item.get('options', {})
                            if options:
                                for k, v in options.items():
                                    st.markdown(f"- **{k}:** {v}")
                                
                                # Display Image if Inspiration ID is present
                                insp_id = options.get("Inspiration ID")
                                if insp_id:
                                    st.write("**Inspiration Image:**")
                                    found = False
                                    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                                        potential_path = os.path.join("images", f"insp_{insp_id}{ext}")
                                        if os.path.exists(potential_path):
                                            st.image(potential_path, width=400)
                                            found = True
                                            break
                                    if not found:
                                        st.warning(f"Image for Inspiration ID {insp_id} not found on disk.")
                            st.divider()
