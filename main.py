import streamlit as st

st.set_page_config(
    page_title="Desserts By Dana - Cake Order Form",
    layout="wide"
)

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

st.title("DESSERTS BY DANA")



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
time_confirmed = st.checkbox("Time Confirmed")
count_confirmed = st.checkbox("Count Confirmed")
invoice = st.checkbox("Invoice")
flower_reminder = st.checkbox("Flower/Topper/Stand Reminder")
save_top_tier = st.checkbox("Save Top Tier")
topper_venue = st.checkbox("Topper at Venue")

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