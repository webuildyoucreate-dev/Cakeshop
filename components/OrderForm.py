import streamlit as st
import sqlite3
import json
import os
import random
from datetime import datetime

def MakeOrderForm(username="Guest"):

    if "order_type" not in st.session_state:
        st.session_state.order_type = None

    top_left, top_right = st.columns(2)

    with top_left:
        if st.button("Wedding order", use_container_width=True):
            st.session_state.order_type = "Wedding order"

    with top_right:
        if st.button("Non-wedding order", use_container_width=True):
            st.session_state.order_type = "Non-wedding order"

    if st.session_state.order_type:
        st.info(f"Current order type: {st.session_state.order_type}")

    is_wedding_order = st.session_state.order_type == "Wedding order"



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

        is_pickup_order = pickup_delivery == "Pick-up"

        if is_wedding_order:
            photographer = st.text_input("Photographer")
            wedding_colors = st.text_input("Wedding Colors")

    with right:
        st.markdown("## VENUE INFORMATION")

        if not is_pickup_order:
            venue_name = st.text_input("Venue Name")
            venue_address = st.text_input("Venue Address")
            venue_city = st.text_input("Venue City")
            venue_state = st.text_input("Venue State")
            venue_zip = st.text_input("Venue Zip")

            venue_contact = st.text_input("Contact Person's Name")
            venue_contact_phone = st.text_input("Contact Person's Phone")

        event_time = st.text_input("Event Time")

        if is_wedding_order:
            ceremony_time = st.text_input("Ceremony Time")
            florist = st.text_input("Florist")

        flowers_provided = st.radio(
            "Flowers Provided By Couple",
            ["Yes", "No"],
            horizontal=True
        )

    st.divider()

    # =====================================================
    # ITEMS (Cupcakes, Cakes, Tiered Cakes)
    # =====================================================

    st.markdown("## ITEMS")

    # Shared option lists
    FLAVORS = [
        "Almond","Amaretto","Apple Spice","Banana","Carrot","Chocolate",
        "Chocolate Banana","Chocolate Hazelnut","Chocolate Mint","Cookie Butter",
        "Cookies 'n Creme","Funfetti","Hazelnut","Key Lime","Lemon","Marble",
        "Mexican Chocolate","Orange Creamsicle","Pink Champagne","Pumpkin",
        "Raspberry","Red Velvet","Strawberry","Strawberry Banana","Sweet Potato",
        "Vanilla","Vanilla Chocolate Chip"
    ]

    FILLINGS = [
        "Italian Buttercream","Almond Cream","Banana Cream","Bavarian Cream w/Strawberries",
        "Cannoli Cream","Caramel","Caramelized Pineapple","Chambord Buttercream",
        "Chocolate Caramel Mousse","Chocolate Chambord Mousse","Chocolate Mousse",
        "Cookie Butter Mousse","Cream Cheese","Grand Marnier","Lemon Curd",
        "Lemon Curd with Blueberries","Mandarin Orange Segment","Mocha Mousse",
        "Nutella Mousse","Orange Marmalade","Peanut Butter Mousse","Pistachio Mousse",
        "Raspberry Preserves","Salted Chocolate Caramel Mousse","Strawberry Cream Cheese",
        "Strawberry Preserves","Tiramisu Mousse","White Chocolate Mousse"
    ]

    if "item_count" not in st.session_state:
        st.session_state.item_count = 1

    items_data = []

    for item in range(1, st.session_state.item_count + 1):
        st.markdown(f"### Item {item}")

        item_type = st.selectbox(
            "Item Type",
            ["Cake", "Cupcake", "Tiered Cake", "Other"],
            key=f"item_type_{item}"
        )

        if item_type == "Cupcake":
            row = st.columns(3)
            with row[0]:
                quantity = st.number_input("Quantity", min_value=1, step=1, key=f"cup_qty_{item}")
            with row[1]:
                flavor = st.selectbox("Flavor", FLAVORS, key=f"flavor_{item}")
            with row[2]:
                frosting = st.text_input("Frosting", key=f"frosting_{item}")

            design = st.text_area("Design Details", key=f"design_{item}", height=80)

            items_data.append({
                "item_number": item,
                "type": "Cupcake",
                "quantity": quantity,
                "flavor": flavor,
                "frosting": frosting,
                "design_details": design
            })

        elif item_type == "Other":
            row4 = st.columns(4)
            with row4[0]:
                type = st.text_input("Type of Item", key=f"other_type_{item}")
            with row4[1]:
                details = st.text_input("Item Details", key=f"other_details_{item}")
            with row4[2]:
                flavor = st.text_input("Flavor", key=f"other_flavor_{item}")
            with row4[3]:
                quantity = st.number_input("Quantity", min_value=1, step=1, key=f"other_qty_{item}")
            items_data.append({
                "item_number": item,
                "type": "Other",
                "other_type": type,
                "details": details,
                "flavor": flavor,
                "quantity": quantity
            })
            

        elif item_type == "Cake":
            row1 = st.columns(4)
            with row1[0]:
                size = st.text_input("Size", key=f"size_{item}")
            with row1[1]:
                shape = st.text_input("Shape", key=f"shape_{item}")
            with row1[2]:
                flavor = st.selectbox("Flavor", FLAVORS, key=f"flavor_{item}")
            with row1[3]:
                filling = st.selectbox("Filling", FILLINGS, key=f"filling_{item}")

            row2 = st.columns(3)
            with row2[0]:
                finish = st.selectbox("Finish", ["Buttercream", "Fondant"], key=f"finish_{item}")
            with row2[1]:
                base_color = st.text_input("Base Color", key=f"base_color_{item}")
            with row2[2]:
                accent_color = st.text_input("Accent Color", key=f"accent_color_{item}")

            design = st.text_area("Cake Design Details", key=f"design_{item}", height=100)
            uploaded_image = st.file_uploader("Upload Cake Image", key=f"image_{item}", type=['png', 'jpg', 'jpeg'])

            items_data.append({
                "item_number": item,
                "type": "Cake",
                "size": size,
                "shape": shape,
                "flavor": flavor,
                "filling": filling,
                "finish": finish,
                "base_color": base_color,
                "accent_color": accent_color,
                "design_details": design,
                "uploaded_image": uploaded_image
            })

        elif item_type == "Tiered Cake":
            tiers = st.number_input("Number of Tiers", min_value=2, max_value=10, value=2, step=1, key=f"tiers_{item}")

            tiers_info = []
            for t in range(1, tiers + 1):
                with st.expander(f"Tier {t}"):
                    tier_size = st.text_input("Tier Size (e.g. 6\" round)", key=f"tier_{item}_{t}_size")
                    tier_servings = st.number_input("Tier Servings", min_value=0, step=1, key=f"tier_{item}_{t}_servings")
                    tier_flavor = st.selectbox("Flavor", FLAVORS, key=f"tier_{item}_{t}_flavor")
                    tier_filling = st.selectbox("Filling", FILLINGS, key=f"tier_{item}_{t}_filling")
                    tier_finish = st.selectbox("Finish", ["Buttercream", "Fondant"], key=f"tier_{item}_{t}_finish")
                    tier_base_color = st.text_input("Base Color", key=f"tier_{item}_{t}_base_color")
                    tier_accent_color = st.text_input("Accent Color", key=f"tier_{item}_{t}_accent_color")
                    tier_image = st.file_uploader("Upload Tier Image", key=f"tier_{item}_{t}_image", type=['png', 'jpg', 'jpeg'])
                    
                    tiers_info.append({
                        "tier": t,
                        "size": tier_size,
                        "servings": tier_servings,
                        "flavor": tier_flavor,
                        "filling": tier_filling,
                        "finish": tier_finish,
                        "base_color": tier_base_color,
                        "accent_color": tier_accent_color,
                        "uploaded_image": tier_image
                    })

            design = st.text_area("Tiered Cake Design Details", key=f"design_{item}", height=140)

            items_data.append({
                "item_number": item,
                "type": "Tiered Cake",
                "tiers": tiers,
                "tiers_info": tiers_info,
                "design_details": design
            })

        st.markdown("---")

    # Buttons to add or remove an item from the items section
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("Add Item", key="add_item"):
            st.session_state.item_count += 1
            st.rerun()

    with col_remove:
        if st.button("Remove Item", key="remove_item"):
            if st.session_state.item_count > 1:
                st.session_state.item_count -= 1
            st.rerun()

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
    # CHECKLIST (form with conditional required fields)
    # =====================================================

    st.markdown("## Checklist")

    with st.form("checklist_form",border=False):
        needed_client = st.checkbox("Items Needed From Client")
        ordered_dbd = st.checkbox("Items To Be Ordered By Desserts By Dana")
        items_received = st.checkbox("Items Received (Date / Initials / Item)")
        equipment_returned = st.checkbox("Equipment Rental Returned To DBD")
        time_confirmed = st.checkbox("Time Confirmed")
        count_confirmed = st.checkbox("Count Confirmed")
        invoice = st.checkbox("Invoice")
        flower_reminder = st.checkbox("Flower/Topper/Stand Reminder")
        save_top_tier = st.checkbox("Save Top Tier")
        topper_venue = st.checkbox("Topper at Venue")

        submit = st.form_submit_button("Save Order")

        if submit:
            # Determine which checklist items are required
            required = ["time_confirmed", "count_confirmed"]
            if is_wedding_order:
                required += ["save_top_tier", "topper_venue"]

            field_map = {
                "time_confirmed": time_confirmed,
                "count_confirmed": count_confirmed,
                "save_top_tier": save_top_tier,
                "topper_venue": topper_venue,
            }

            missing = [name for name in required if not field_map.get(name)]
            if missing:
                labels = [name.replace("_", " ").title() for name in missing]
                st.error(f"Please complete required checklist items: {', '.join(labels)}")
            else:
                os.makedirs("images", exist_ok=True)
                
                def process_image(img_obj):
                    if img_obj is not None:
                        file_id = f"{random.randint(10000, 99999)}"
                        ext = os.path.splitext(img_obj.name)[1]
                        filename = f"{file_id}{ext}"
                        with open(os.path.join("images", filename), "wb") as f:
                            f.write(img_obj.getbuffer())
                        return filename
                    return None

                for i_data in items_data:
                    if i_data["type"] == "Cake":
                        img = i_data.pop("uploaded_image", None)
                        i_data["image_file"] = process_image(img)
                    elif i_data["type"] == "Tiered Cake":
                        for t_info in i_data.get("tiers_info", []):
                            img = t_info.pop("uploaded_image", None)
                            t_info["image_file"] = process_image(img)

                # Collect all order data into a dict
                order_data = {
                    "order_type": st.session_state.order_type,
                    "client": {
                        "name": client_name,
                        "phone": phone,
                        "email": email,
                    },
                    "event_details": {
                        "date": str(event_date),
                        "guest_count": guest_count,
                        "pickup_delivery": pickup_delivery,
                        "delivery_time": delivery_time if not is_pickup_order else "",
                        "photographer": photographer if is_wedding_order else "",
                        "wedding_colors": wedding_colors if is_wedding_order else "",
                        "event_time": event_time,
                        "ceremony_time": ceremony_time if is_wedding_order else "",
                        "florist": florist if is_wedding_order else "",
                        "flowers_provided": flowers_provided,
                    },
                    "venue": {
                        "name": venue_name if not is_pickup_order else "",
                        "address": venue_address if not is_pickup_order else "",
                        "city": venue_city if not is_pickup_order else "",
                        "state": venue_state if not is_pickup_order else "",
                        "zip": venue_zip if not is_pickup_order else "",
                        "contact_name": venue_contact if not is_pickup_order else "",
                        "contact_phone": venue_contact_phone if not is_pickup_order else "",
                    },
                    "items": items_data,
                    "overall_design_notes": design_details,
                    "pricing": {
                        "cake_price": cake_price,
                        "delivery_fee": delivery_fee,
                        "grand_total": grand_total,
                        "equipment_rental": equipment_rental,
                        "deposit_amount": deposit_amount,
                        "balance_due": balance_due,
                        "due_dates": due_dates,
                        "paid_in_full": paid_in_full,
                        "order_taken_by": order_taken_by,
                        "order_date": str(order_date),
                    },
                    "decor": {
                        "flowers_here": flowers_here,
                        "other_decor": other_decor,
                        "cake_stand": cake_stand,
                    },
                    "circle_location": circle_location,
                    "checklist": {
                        "needed_client": needed_client,
                        "ordered_dbd": ordered_dbd,
                        "items_received": items_received,
                        "equipment_returned": equipment_returned,
                        "time_confirmed": time_confirmed,
                        "count_confirmed": count_confirmed,
                        "invoice": invoice,
                        "flower_reminder": flower_reminder,
                        "save_top_tier": save_top_tier,
                        "topper_venue": topper_venue,
                    }
                }
                
                try:
                    conn = sqlite3.connect("app.db")
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO orders (author, `time created`, json) VALUES (?, ?, ?)",
                        (username, datetime.now().isoformat(), json.dumps(order_data))
                    )
                    conn.commit()
                    conn.close()
                    st.success("Order information saved.")
                except Exception as e:
                    st.error(f"Error saving order: {e}")

    st.divider()
    st.write(username)

def ViewOrderForm():
    st.title("Desserts By Dana - Order Viewer")

    def load_orders():
        try:
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT author, `time created`, json FROM orders ORDER BY `time created` DESC")
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            st.error(f"Error loading from database: {e}")
            return []

    orders = load_orders()

    if not orders:
        st.info("No orders found in the database.")
    else:
        for idx, (author, time_created, order_json_str) in enumerate(orders):
            try:
                order_data = json.loads(order_json_str)
            except Exception as e:
                order_data = {"error": f"Invalid JSON: {e}", "raw": order_json_str}
                
            order_type = order_data.get('order_type', 'Unknown Type')
            client_name = order_data.get('client', {}).get('name', 'Unknown Client')
            event_date = order_data.get('event_details', {}).get('date', 'Unknown Date')
            
            with st.expander(f"Order #{len(orders)-idx} | {client_name} | {order_type} | {event_date}"):
                st.markdown(f"**Author:** {author} | **Created At:** {time_created}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader("Client Information")
                    client = order_data.get('client', {})
                    st.write(f"**Name:** {client.get('name', '')}")
                    st.write(f"**Phone:** {client.get('phone', '')}")
                    st.write(f"**Email:** {client.get('email', '')}")
                    
                with col2:
                    st.subheader("Event Details")
                    events = order_data.get('event_details', {})
                    st.write(f"**Date:** {events.get('date', '')}")
                    st.write(f"**Guest Count:** {events.get('guest_count', 0)}")
                    st.write(f"**Delivery/Pickup:** {events.get('pickup_delivery', '')}")
                    
                with col3:
                    st.subheader("Pricing")
                    pricing = order_data.get('pricing', {})
                    st.write(f"**Grand Total:** ${pricing.get('grand_total', 0)}")
                    st.write(f"**Balance Due:** ${pricing.get('balance_due', 0)}")
                
                st.divider()
                st.subheader("Raw Order Data")
                st.json(order_data)

if __name__ == "__main__":
    MakeOrderForm()


