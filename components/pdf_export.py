"""
pdf_export.py
Generates PDF bytes for Orders and Requisitions using ReportLab.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colour palette ─────────────────────────────────────────────────────────────
BRAND_PINK   = colors.HexColor("#E91E8C")
BRAND_DARK   = colors.HexColor("#1A1A2E")
LIGHT_GRAY   = colors.HexColor("#F5F5F5")
MID_GRAY     = colors.HexColor("#CCCCCC")
TEXT_DARK    = colors.HexColor("#333333")
WHITE        = colors.white


def _base_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        fontSize=22, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontSize=11, fontName="Helvetica",
        textColor=WHITE, alignment=TA_CENTER,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13, fontName="Helvetica-Bold",
        textColor=BRAND_PINK, spaceBefore=12, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="FieldLabel",
        fontSize=9, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#888888"), spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="FieldValue",
        fontSize=10, fontName="Helvetica",
        textColor=TEXT_DARK, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SmallNote",
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#888888"),
    ))
    styles.add(ParagraphStyle(
        name="CheckItem",
        fontSize=10, fontName="Helvetica",
        textColor=TEXT_DARK, spaceAfter=3, leftIndent=6,
    ))
    return styles


def _header_table(title: str, subtitle: str):
    """Returns a full-width header banner table."""
    data = [
        [Paragraph(title, _base_styles()["DocTitle"])],
        [Paragraph(subtitle, _base_styles()["DocSubtitle"])],
    ]
    tbl = Table(data, colWidths=[7.5 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [BRAND_DARK]),
    ]))
    return tbl


def _field(label: str, value, styles):
    """Returns [label paragraph, value paragraph]."""
    v = str(value) if value not in (None, "", 0, 0.0, False) else "—"
    return [
        Paragraph(label.upper(), styles["FieldLabel"]),
        Paragraph(v, styles["FieldValue"]),
    ]


def _two_col_fields(pairs, styles, col_widths=None):
    """Render pairs of (label, value) side-by-side in a table."""
    col_widths = col_widths or [3.75 * inch, 3.75 * inch]
    rows = []
    for i in range(0, len(pairs), 2):
        left_label, left_val = pairs[i]
        if i + 1 < len(pairs):
            right_label, right_val = pairs[i + 1]
        else:
            right_label, right_val = "", ""
        rows.append([
            Paragraph(left_label.upper(),  styles["FieldLabel"]),
            Paragraph(right_label.upper(), styles["FieldLabel"]),
        ])
        lv = str(left_val)  if left_val  not in (None, "", 0, 0.0, False) else "—"
        rv = str(right_val) if right_val not in (None, "", 0, 0.0, False) else "—"
        rows.append([
            Paragraph(lv, styles["FieldValue"]),
            Paragraph(rv, styles["FieldValue"]),
        ])

    if not rows:
        return []
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    return [tbl]


def _section(title: str, styles):
    return [
        Spacer(1, 6),
        Paragraph(title, styles["SectionHeader"]),
        HRFlowable(width="100%", thickness=1, color=MID_GRAY, spaceAfter=6),
    ]


def _checkbox(label: str, checked: bool, styles):
    mark = "☑" if checked else "☐"
    return Paragraph(f"{mark}  {label}", styles["CheckItem"])


# ══════════════════════════════════════════════════════════════════════════════
#  ORDER PDF
# ══════════════════════════════════════════════════════════════════════════════

def generate_order_pdf(order_data: dict, order_num: int, author: str, time_created: str) -> bytes:
    """Generate a PDF for a single order and return the raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.5 * inch,  bottomMargin=0.5 * inch,
    )
    styles = _base_styles()
    story = []

    order_type  = order_data.get("order_type", "Order")
    client      = order_data.get("client", {})
    client_name = client.get("name", "Unknown Client")
    events      = order_data.get("event_details", {})
    pricing     = order_data.get("pricing", {})
    venue       = order_data.get("venue", {})
    decor       = order_data.get("decor", {})
    checklist   = order_data.get("checklist", {})
    is_wedding  = order_type == "Wedding order"
    is_pickup   = events.get("pickup_delivery") == "Pick-up"

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(_header_table(
        "Ratzon Chen",
        f"Order #{order_num}  ·  {order_type}  ·  Created by {author}"
    ))
    story.append(Spacer(1, 10))

    # ── Client Information ─────────────────────────────────────────────────────
    story += _section("Client Information", styles)
    pairs = [
        ("Name",              client.get("name", "")),
        ("Phone",             client.get("phone", "")),
        ("Email",             client.get("email", "")),
        ("Event Date",        events.get("date", "")),
        ("Guest Count",       events.get("guest_count", "")),
        ("Delivery / Pick-up", events.get("pickup_delivery", "")),
        ("Delivery Time",     events.get("delivery_time", "")),
        ("Event Time",        events.get("event_time", "")),
    ]
    if is_wedding:
        pairs += [
            ("Photographer",    events.get("photographer", "")),
            ("Wedding Colors",  events.get("wedding_colors", "")),
            ("Ceremony Time",   events.get("ceremony_time", "")),
            ("Florist",         events.get("florist", "")),
        ]
    pairs.append(("Flowers Provided By Couple", events.get("flowers_provided", "")))
    story += _two_col_fields(pairs, styles)

    # ── Venue ──────────────────────────────────────────────────────────────────
    if not is_pickup:
        story += _section("Venue Information", styles)
        story += _two_col_fields([
            ("Venue Name",      venue.get("name", "")),
            ("Address",         venue.get("address", "")),
            ("City",            venue.get("city", "")),
            ("State",           venue.get("state", "")),
            ("Zip",             venue.get("zip", "")),
            ("Contact Name",    venue.get("contact_name", "")),
            ("Contact Phone",   venue.get("contact_phone", "")),
        ], styles)

    # ── Items ──────────────────────────────────────────────────────────────────
    story += _section("Items", styles)
    for i_data in order_data.get("items", []):
        itype    = i_data.get("type", "")
        item_num = i_data.get("item_number", "")
        story.append(Paragraph(f"Item {item_num}: {itype}", styles["SectionHeader"]))

        if itype == "Cupcake":
            story += _two_col_fields([
                ("Quantity", i_data.get("quantity", "")),
                ("Flavor",   i_data.get("flavor", "")),
                ("Frosting", i_data.get("frosting", "")),
            ], styles)
            story += _field("Design Details", i_data.get("design_details", ""), styles)

        elif itype == "Other":
            story += _two_col_fields([
                ("Type of Item", i_data.get("other_type", "")),
                ("Item Details", i_data.get("details", "")),
                ("Flavor",       i_data.get("flavor", "")),
                ("Quantity",     i_data.get("quantity", "")),
            ], styles)

        elif itype == "Cake":
            story += _two_col_fields([
                ("Size",         i_data.get("size", "")),
                ("Shape",        i_data.get("shape", "")),
                ("Flavor",       i_data.get("flavor", "")),
                ("Filling",      i_data.get("filling", "")),
                ("Finish",       i_data.get("finish", "")),
                ("Base Color",   i_data.get("base_color", "")),
                ("Accent Color", i_data.get("accent_color", "")),
            ], styles)
            story += _field("Design Details", i_data.get("design_details", ""), styles)

        elif itype == "Tiered Cake":
            story += _field("Number of Tiers", i_data.get("tiers", ""), styles)
            for tier in i_data.get("tiers_info", []):
                t_num = tier.get("tier", "")
                story.append(Paragraph(f"  Tier {t_num}", styles["FieldLabel"]))
                story += _two_col_fields([
                    ("Size",         tier.get("size", "")),
                    ("Servings",     tier.get("servings", "")),
                    ("Flavor",       tier.get("flavor", "")),
                    ("Filling",      tier.get("filling", "")),
                    ("Finish",       tier.get("finish", "")),
                    ("Base Color",   tier.get("base_color", "")),
                    ("Accent Color", tier.get("accent_color", "")),
                ], styles)
            story += _field("Design Details", i_data.get("design_details", ""), styles)

        story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=6))

    # ── Overall Design Notes ───────────────────────────────────────────────────
    story += _section("Overall Order Design Notes", styles)
    story += _field("", order_data.get("overall_design_notes", ""), styles)

    # ── Pricing ────────────────────────────────────────────────────────────────
    story += _section("Pricing", styles)
    story += _two_col_fields([
        ("Cake Price ($)",      pricing.get("cake_price", "")),
        ("Delivery ($)",        pricing.get("delivery_fee", "")),
        ("Grand Total ($)",     pricing.get("grand_total", "")),
        ("Equipment Rental",    pricing.get("equipment_rental", "")),
        ("Deposit Amount ($)",  pricing.get("deposit_amount", "")),
        ("Balance Due ($)",     pricing.get("balance_due", "")),
        ("Due Date(s)",         pricing.get("due_dates", "")),
        ("Paid in Full",        "Yes" if pricing.get("paid_in_full") else "No"),
        ("Order Taken By",      pricing.get("order_taken_by", "")),
        ("Order Date",          pricing.get("order_date", "")),
    ], styles)

    # ── Decor / Flowers ────────────────────────────────────────────────────────
    story += _section("Flowers / Décor / Stand", styles)
    story += _two_col_fields([
        ("Flowers Here",     decor.get("flowers_here", "")),
        ("Other Décor Here", decor.get("other_decor", "")),
    ], styles)
    story += _field("Cake Stand", decor.get("cake_stand", ""), styles)

    # ── Location ───────────────────────────────────────────────────────────────
    story += _section("Location", styles)
    story += _field("", order_data.get("circle_location", ""), styles)

    # ── Checklist ─────────────────────────────────────────────────────────────
    story += _section("Checklist", styles)
    checklist_items = [
        ("Items Needed From Client",              "needed_client"),
        ("Items To Be Ordered By Ratzon Chen",    "ordered_dbd"),
        ("Items Received (Date / Initials / Item)","items_received"),
        ("Equipment Rental Returned To DBD",      "equipment_returned"),
        ("Time Confirmed",                        "time_confirmed"),
        ("Count Confirmed",                       "count_confirmed"),
        ("Invoice",                               "invoice"),
        ("Flower/Topper/Stand Reminder",          "flower_reminder"),
        ("Save Top Tier",                         "save_top_tier"),
        ("Topper at Venue",                       "topper_venue"),
    ]
    for label, key in checklist_items:
        story.append(_checkbox(label, checklist.get(key, False), styles))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["SmallNote"]
    ))

    doc.build(story)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
#  REQUISITION PDF
# ══════════════════════════════════════════════════════════════════════════════

def generate_requisition_pdf(req_data: dict, req_id: int, author: str, time_created: str) -> bytes:
    """Generate a PDF for a single requisition and return the raw bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
        topMargin=0.5 * inch,  bottomMargin=0.5 * inch,
    )
    styles = _base_styles()
    story = []

    meta     = req_data.get("_meta", {})
    from_loc = meta.get("from_location", "")
    to_loc   = meta.get("to_location", "")

    try:
        dt = datetime.fromisoformat(time_created)
        formatted_time = dt.strftime("%B %d, %Y  %I:%M %p")
    except Exception:
        formatted_time = time_created

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(_header_table(
        "Ratzon Chen",
        f"Requisition #{req_id}  ·  Saved by {author}  ·  {formatted_time}"
    ))
    story.append(Spacer(1, 10))

    # ── Locations ──────────────────────────────────────────────────────────────
    if from_loc or to_loc:
        story += _section("Locations", styles)
        story += _two_col_fields([
            ("From Location", from_loc),
            ("To Location",   to_loc),
        ], styles)

    # ── Items by Category ──────────────────────────────────────────────────────
    story += _section("Requisition Items", styles)

    category_rows = []
    for category, items in req_data.items():
        if category == "_meta":
            continue
        if not isinstance(items, dict):
            continue
        for item_name, qty in items.items():
            category_rows.append((category, item_name, qty))

    if not category_rows:
        story.append(Paragraph("No items requested.", styles["FieldValue"]))
    else:
        # Group by category for a clean table
        current_category = None
        table_rows = [
            [
                Paragraph("CATEGORY", styles["FieldLabel"]),
                Paragraph("ITEM", styles["FieldLabel"]),
                Paragraph("QTY", styles["FieldLabel"]),
            ]
        ]
        for cat, item, qty in category_rows:
            cat_display = cat if cat != current_category else ""
            if cat != current_category:
                current_category = cat
            table_rows.append([
                Paragraph(cat_display, styles["FieldValue"]),
                Paragraph(item, styles["FieldValue"]),
                Paragraph(str(qty), styles["FieldValue"]),
            ])

        tbl = Table(
            table_rows,
            colWidths=[2.2 * inch, 4.3 * inch, 1.0 * inch],
            repeatRows=1,
        )
        tbl.setStyle(TableStyle([
            # Header row
            ("BACKGROUND",   (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0), 9),
            # Alternating rows
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            # Grid
            ("GRID",         (0, 0), (-1, -1), 0.5, MID_GRAY),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        styles["SmallNote"]
    ))

    doc.build(story)
    return buf.getvalue()
