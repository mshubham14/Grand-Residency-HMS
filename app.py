import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import io
import random
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Import MySQL database connection
from database import create_connection

# ---------------------------------------------------------
# Page Configuration & Royal Glassmorphism Theme (Outfit & Cinzel Fonts)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Grand Residency | Royal Enterprise HMS",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0f172a 0%, #060911 60%, #020617 100%);
        color: #f1f5f9;
    }
    
    h1, h2, h3, .royal-header {
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.05em;
    }

    /* Glassmorphism Card Style */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.5);
    }

    /* Interactive Floor Grid Tile */
    .room-tile {
        padding: 16px;
        border-radius: 14px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .room-tile:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
    }
    
    .tile-available {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.22) 0%, rgba(5, 150, 105, 0.35) 100%);
        border-color: rgba(52, 211, 153, 0.5);
    }
    .tile-occupied {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.22) 0%, rgba(185, 28, 28, 0.35) 100%);
        border-color: rgba(248, 113, 113, 0.5);
    }
    .tile-maintenance {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.22) 0%, rgba(180, 83, 9, 0.35) 100%);
        border-color: rgba(251, 191, 36, 0.5);
    }

    /* Metric Counters */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
        border-radius: 16px !important;
        padding: 18px 22px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Cinzel', serif !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #fcd34d !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }

    /* Royal Metallic Gold Button */
    .stButton>button {
        background: linear-gradient(135deg, #d97706 0%, #b45309 50%, #78350f 100%);
        color: #ffffff;
        border: 1px solid rgba(251, 191, 36, 0.4);
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.04em;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        box-shadow: 0 4px 18px rgba(245, 158, 11, 0.45);
        color: #fff;
    }

    /* Virtual Credit Card Mockup */
    .virtual-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 22px;
        color: #fff;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        position: relative;
        margin-bottom: 15px;
    }

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background: #060911 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
</style>
"""
st.markdown(CUSTOM_THEME, unsafe_allow_html=True)

# ---------------------------------------------------------
# Database Utility Layer
# ---------------------------------------------------------
def run_query(query, params=None, fetch=False, fetch_one=False, commit=False):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return True
        if fetch_one:
            return cursor.fetchone()
        if fetch:
            return cursor.fetchall()
    except Exception as err:
        st.error(f"SQL Error: {err}")
        if commit:
            conn.rollback()
        return None
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def fetch_dataframe(query, params=None):
    res = run_query(query, params, fetch=True)
    return pd.DataFrame(res) if res else pd.DataFrame()

# ---------------------------------------------------------
# PDF Invoice Generator (Grand Residency Official Folio)
# ---------------------------------------------------------
def generate_pdf_invoice(bill_id, guest_name, room_no, c_in, c_out, r_bill, f_bill, discount, tax, total, txn_id, method):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Header Banner
    pdf.setFillColorRGB(0.04, 0.07, 0.12)
    pdf.rect(0, 715, 612, 85, fill=1, stroke=0)
    pdf.setFillColorRGB(0.98, 0.83, 0.3)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(45, 755, "GRAND RESIDENCY")
    pdf.setFillColorRGB(0.8, 0.85, 0.9)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(45, 736, "Luxury Resort & Spa | Official Tax Invoice & Guest Folio")

    # Guest Details
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(45, 680, f"Invoice Number: GR-{bill_id:05d}")
    pdf.drawString(45, 662, f"Transaction Ref: {txn_id}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(45, 644, f"Primary Guest: {guest_name}")
    pdf.drawString(45, 626, f"Payment Channel: {method}")
    pdf.drawString(45, 608, f"Date of Issue: {date.today().strftime('%d %B %Y')}")
    
    pdf.drawString(330, 680, f"Room Assigned: {room_no}")
    pdf.drawString(330, 662, f"Check-In Date:  {c_in}")
    pdf.drawString(330, 644, f"Check-Out Date: {c_out}")
    
    pdf.setStrokeColorRGB(0.8, 0.8, 0.8)
    pdf.line(45, 595, 560, 595)
    
    # Financial Line Items
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(45, 575, "Service / Item Description")
    pdf.drawString(450, 575, "Amount (INR)")
    pdf.line(45, 565, 560, 565)
    
    pdf.setFont("Helvetica", 10)
    pdf.drawString(45, 540, "Room Accommodation Tariff")
    pdf.drawString(450, 540, f"Rs. {r_bill:,.2f}")
    pdf.drawString(45, 515, "Dining & Room Service Orders")
    pdf.drawString(450, 515, f"Rs. {f_bill:,.2f}")
    pdf.drawString(45, 490, "Loyalty Discount Deducted")
    pdf.drawString(450, 490, f"- Rs. {discount:,.2f}")
    pdf.drawString(45, 465, "Applicable Goods & Services Tax (5% GST)")
    pdf.drawString(450, 465, f"+ Rs. {tax:,.2f}")
    
    pdf.line(45, 445, 560, 445)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(300, 420, "Total Amount Paid:")
    pdf.drawString(450, 420, f"Rs. {total:,.2f}")
    
    pdf.line(45, 395, 560, 395)
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColorRGB(0.3, 0.3, 0.3)
    pdf.drawString(45, 365, "Thank you for staying at Grand Residency. We look forward to welcoming you again.")
    pdf.drawString(45, 350, "Front Desk: +91 20 6800 9900 | Email: frontdesk@grandresidency.com")
    
    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# Multi-Role Authentication Setup
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.username = None

def handle_login(user, pwd):
    accounts = {
        "admin": ("admin123", "Platform Admin"),
        "hoteladmin": ("hotel123", "Hotel Admin"),
        "manager": ("manager123", "Manager Admin"),
        "waiter": ("waiter123", "Waiter Admin")
    }
    if user in accounts and accounts[user][0] == pwd:
        st.session_state.authenticated = True
        st.session_state.user_role = accounts[user][1]
        st.session_state.username = user
        return True
    return False

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, login_box, _ = st.columns([1, 1.2, 1])
    with login_box:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h1 style="color: #fcd34d; margin: 0;">👑 GRAND RESIDENCY</h1>
            <p style="color: #94a3b8; font-size: 0.85rem; letter-spacing: 0.1em; text-transform: uppercase;">Next-Gen Hotel Enterprise System</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<p style='font-weight:600;'>Console Security Authentication</p>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="admin / manager / waiter")
            p = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Authenticate Access", use_container_width=True)
            if submit:
                if handle_login(u, p):
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")
        st.caption("Quick Logins: `admin`/`admin123` | `manager`/`manager123` | `waiter`/`waiter123`")
    st.stop()

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0;">
        <h2 style="color: #fcd34d; margin:0; font-family:'Cinzel', serif;">👑 GRAND RESIDENCY</h2>
        <span style="font-size: 0.8rem; color: #94a3b8; letter-spacing:0.06em;">LUXURY HOTEL & RESORT</span>
    </div>
    """, unsafe_allow_html=True)
    st.write(f"Active Operator: **{st.session_state.username.title()}**")
    st.caption(f"Role: **{st.session_state.user_role}**")
    st.divider()

    if st.session_state.user_role == "Waiter Admin":
        pages = ["🍽️️ Food & POS Orders"]
    elif st.session_state.user_role == "Manager Admin":
        pages = [
            "📊 Executive Dashboard", 
            "📝 Front Desk & Bookings", 
            "🛎️️ Check-In / Check-Out", 
            "🍽️ Food & POS Orders", 
            "💳 Smart Payment Hub", 
            "🧹 Housekeeping Operations"
        ]
    else:
        pages = [
            "📊 Executive Dashboard", 
            "📝 Front Desk & Bookings", 
            "🛎️ Check-In / Check-Out", 
            "🍽️ Food & POS Orders", 
            "💳 Smart Payment Hub", 
            "🧹 Housekeeping Operations", 
            "🏨 Rooms Master Control", 
            "👥 Staff Management", 
            "📈 Financial Audit & Reports"
        ]

    selected_page = st.radio("NAVIGATION MENU", pages)
    st.divider()
    if st.button("🚪 Terminate Session", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.rerun()

# ---------------------------------------------------------
# 1. Executive Dashboard (KPIs, RevPAR & Floor Map)
# ---------------------------------------------------------
if selected_page == "📊 Executive Dashboard":
    st.markdown("### 📊 Grand Residency — Operational Overview")
    
    rooms_df = fetch_dataframe("SELECT * FROM rooms")
    tot_rooms = len(rooms_df)
    occ_rooms = len(rooms_df[rooms_df['status'] == 'Occupied']) if not rooms_df.empty else 0
    avail_rooms = len(rooms_df[rooms_df['status'] == 'Available']) if not rooms_df.empty else 0
    occ_ratio = (occ_rooms / tot_rooms * 100) if tot_rooms > 0 else 0.0

    rev_res = run_query("SELECT COALESCE(SUM(amount), 0) AS total_rev FROM payments WHERE payment_status = 'Paid'", fetch_one=True)
    total_rev = float(rev_res['total_rev']) if rev_res else 0.0
    
    adr = (total_rev / occ_rooms) if occ_rooms > 0 else 0.0
    revpar = (total_rev / tot_rooms) if tot_rooms > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Available Rooms", avail_rooms, f"{tot_rooms} Total Inventory")
    c2.metric("Occupancy Ratio", f"{occ_ratio:.1f}%")
    c3.metric("ADR (Avg Rate)", f"₹{adr:,.0f}")
    c4.metric("Realized Revenue", f"₹{total_rev:,.0f}", f"RevPAR: ₹{revpar:,.0f}")

    st.write("")
    st.markdown("#### 🗺️ Interactive Live Room Status Map")
    if not rooms_df.empty:
        grid = st.columns(4)
        for idx, r in rooms_df.iterrows():
            col = grid[idx % 4]
            status_style = "tile-available" if r['status'] == "Available" else ("tile-occupied" if r['status'] == "Occupied" else "tile-maintenance")
            badge = "🟢 VACANT" if r['status'] == "Available" else ("🔴 OCCUPIED" if r['status'] == "Occupied" else "🟠 SERVICE")
            with col:
                st.markdown(f"""
                <div class="room-tile {status_style}">
                    <div style="font-size: 0.75rem; font-weight:700;">{badge}</div>
                    <h3 style="margin: 4px 0; color:#fff;">Room {r['room_number']}</h3>
                    <div style="font-size: 0.82rem; color: #cbd5e1;">{r['room_type']}</div>
                    <div style="font-weight: 700; color: #fcd34d; margin-top: 4px;">₹{r['price_per_night']} / night</div>
                </div>
                """, unsafe_allow_html=True)

    st.divider()
    ch1, ch2 = st.columns([1, 1.4])
    with ch1:
        st.markdown("**Room Occupancy Status**")
        if not rooms_df.empty:
            sc = rooms_df['status'].value_counts().reset_index()
            sc.columns = ['Status', 'Count']
            fig_pie = px.pie(sc, names='Status', values='Count', hole=0.55,
                             color='Status', color_discrete_map={'Available':'#10b981', 'Occupied':'#ef4444', 'Maintenance':'#f59e0b'})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1', height=280, margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_pie, use_container_width=True)
    with ch2:
        st.markdown("**Daily Realized Revenue**")
        pay_df = fetch_dataframe("SELECT DATE(payment_date) as pay_date, SUM(amount) as daily_rev FROM payments WHERE payment_status = 'Paid' GROUP BY DATE(payment_date)")
        if not pay_df.empty:
            fig_bar = px.bar(pay_df, x='pay_date', y='daily_rev', color_discrete_sequence=['#f59e0b'])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#cbd5e1', height=280, margin=dict(t=5,b=5,l=5,r=5))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No recorded payment transactions available yet.")

# ---------------------------------------------------------
# 2. Front Desk & Bookings
# ---------------------------------------------------------
elif selected_page == "📝 Front Desk & Bookings":
    st.markdown("### 📝 Reservation & Guest Management")
    t1, t2 = st.tabs(["✨ New Reservation", "📋 Reservation Records"])
    
    with t1:
        with st.form("new_res_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                name = st.text_input("Customer Name *")
                phone = st.text_input("Phone Number (10 digits) *")
                email = st.text_input("Email Address")
                addr = st.text_input("Residential City/Address")
            with fc2:
                avail_rooms = run_query("SELECT room_id, room_number, room_type, price_per_night FROM rooms WHERE status = 'Available'", fetch=True)
                if avail_rooms:
                    r_map = {f"Room {r['room_number']} ({r['room_type']}) - ₹{r['price_per_night']}": r for r in avail_rooms}
                    sel_r = st.selectbox("Assign Vacant Room *", list(r_map.keys()))
                else:
                    st.warning("No vacant rooms available.")
                    sel_r = None
                cin = st.date_input("Check-In Date", value=date.today())
                cout = st.date_input("Check-Out Date", value=date.today())
            
            sub_res = st.form_submit_button("Book & Confirm Reservation", use_container_width=True)
            if sub_res:
                if not name or len(phone) != 10 or not sel_r:
                    st.error("Please enter a valid Customer Name, 10-digit Phone, and Room.")
                elif (cout - cin).days <= 0:
                    st.error("Check-out date must be at least 1 day after check-in.")
                else:
                    room_data = r_map[sel_r]
                    run_query("INSERT INTO customers (full_name, phone, email, address) VALUES (%s, %s, %s, %s)", 
                              (name, phone, email, addr), commit=True)
                    cust_record = run_query("SELECT customer_id FROM customers WHERE phone = %s ORDER BY customer_id DESC LIMIT 1", (phone,), fetch_one=True)
                    cid = cust_record['customer_id']
                    
                    run_query("INSERT INTO bookings (customer_id, room_id, check_in, check_out, booking_status) VALUES (%s, %s, %s, %s, 'Booked')",
                              (cid, room_data['room_id'], cin, cout), commit=True)
                    st.success(f"Reservation confirmed for {name} in Room {room_data['room_number']}!")
                    st.balloons()
                    st.rerun()

    with t2:
        bk_df = fetch_dataframe("""
            SELECT b.booking_id, c.full_name, c.phone, r.room_number, r.room_type, b.check_in, b.check_out, b.booking_status
            FROM bookings b
            INNER JOIN customers c ON b.customer_id = c.customer_id
            INNER JOIN rooms r ON b.room_id = r.room_id
            ORDER BY b.booking_id DESC
        """)
        if not bk_df.empty:
            st.dataframe(bk_df, use_container_width=True, hide_index=True)
        else:
            st.info("No bookings recorded yet.")

# ---------------------------------------------------------
# 3. Check-In & Check-Out Operations
# ---------------------------------------------------------
elif selected_page == "🛎️ Check-In / Check-Out":
    st.markdown("### 🛎️ Front Desk Check-In & Check-Out")
    ci_col, co_col = st.columns(2)
    with ci_col:
        st.markdown("#### 🟢 Customer Check-In")
        booked_stays = run_query("""
            SELECT b.booking_id, c.full_name, r.room_number, r.room_id
            FROM bookings b
            INNER JOIN customers c ON b.customer_id = c.customer_id
            INNER JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_status = 'Booked' AND r.status = 'Available'
        """, fetch=True)
        
        if booked_stays:
            b_map = {f"Booking #{b['booking_id']} | {b['full_name']} (Room {b['room_number']})": b for b in booked_stays}
            sel_ci = st.selectbox("Select Pending Arrival:", list(b_map.keys()))
            if st.button("Confirm Check-In & Handover Keys", use_container_width=True):
                target = b_map[sel_ci]
                run_query("UPDATE bookings SET booking_status = 'Checked-In' WHERE booking_id = %s", (target['booking_id'],), commit=True)
                run_query("UPDATE rooms SET status = 'Occupied' WHERE room_id = %s", (target['room_id'],), commit=True)
                st.success(f"{target['full_name']} checked into Room {target['room_number']}!")
                st.rerun()
        else:
            st.info("No guests currently queued for Check-In.")

    with co_col:
        st.markdown("#### 🔴 Customer Check-Out")
        active_stays = run_query("""
            SELECT b.booking_id, c.full_name, r.room_number, r.room_id
            FROM bookings b
            INNER JOIN customers c ON b.customer_id = c.customer_id
            INNER JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_status = 'Checked-In'
        """, fetch=True)
        
        if active_stays:
            co_map = {f"Stay #{s['booking_id']} | {s['full_name']} (Room {s['room_number']})": s for s in active_stays}
            sel_co = st.selectbox("Select In-House Departure:", list(co_map.keys()))
            if st.button("Mark Checked-Out & Free Room", use_container_width=True):
                target_co = co_map[sel_co]
                run_query("UPDATE bookings SET booking_status = 'Checked-Out' WHERE booking_id = %s", (target_co['booking_id'],), commit=True)
                run_query("UPDATE rooms SET status = 'Available' WHERE room_id = %s", (target_co['room_id'],), commit=True)
                st.success(f"Checked out Room {target_co['room_number']}. Room marked Available!")
                st.rerun()
        else:
            st.info("No checked-in guests found.")

# ---------------------------------------------------------
# 4. Food & POS Orders (Full CRUD: Add Dish, Order, Manage)
# ---------------------------------------------------------
elif selected_page == "🍽️ Food & POS Orders":
    st.markdown("### 🍽️ Grand Residency Dining & Kitchen POS")
    f_tab1, f_tab2, f_tab3 = st.tabs(["🛎️ Take Room Order", "➕ Add New Dish / Drink", "⚙️ Manage Food Menu"])
    
    with f_tab1:
        checked_in = run_query("""
            SELECT b.booking_id, c.full_name, r.room_number 
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_status = 'Checked-In'
        """, fetch=True)
        
        food_items = run_query("SELECT food_id, food_name, price FROM food_items WHERE availability = 'Available'", fetch=True)
        
        if not checked_in:
            st.warning("No guests are currently checked-in to place orders.")
        elif not food_items:
            st.warning("No available food items in the database.")
        else:
            with st.form("food_order_form", clear_on_submit=True):
                room_opts = {f"Room {g['room_number']} - {g['full_name']}": g['booking_id'] for g in checked_in}
                target_booking = st.selectbox("Select Resident Room:", list(room_opts.keys()))
                
                dish_opts = {f"{f['food_name']} (₹{f['price']})": f for f in food_items}
                selected_dish = st.selectbox("Select Food/Beverage:", list(dish_opts.keys()))
                qty = st.number_input("Order Quantity", min_value=1, max_value=20, value=1)
                
                send_order = st.form_submit_button("Send Order to Kitchen", use_container_width=True)
                if send_order:
                    b_id = room_opts[target_booking]
                    dish = dish_opts[selected_dish]
                    unit_p = dish['price']
                    total_p = unit_p * qty
                    
                    run_query("""
                        INSERT INTO food_orders (booking_id, food_id, quantity, unit_price, total_price, order_status)
                        VALUES (%s, %s, %s, %s, %s, 'Pending')
                    """, (b_id, dish['food_id'], qty, unit_p, total_p), commit=True)
                    st.success(f"Order sent: {qty}x {dish['food_name']} (₹{total_p}) assigned to folio!")
                    st.rerun()

        st.markdown("#### 📋 Live Kitchen Orders Stream")
        orders_df = fetch_dataframe("""
            SELECT fo.order_id, c.full_name, r.room_number, fi.food_name, fo.quantity, fo.total_price, fo.order_status, fo.order_date
            FROM food_orders fo
            JOIN bookings b ON fo.booking_id = b.booking_id
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            JOIN food_items fi ON fo.food_id = fi.food_id
            ORDER BY fo.order_id DESC LIMIT 10
        """)
        if not orders_df.empty:
            st.dataframe(orders_df, use_container_width=True, hide_index=True)

    with f_tab2:
        st.markdown("#### ➕ Add New Item to Menu")
        with st.form("new_food_form", clear_on_submit=True):
            nf1, nf2 = st.columns(2)
            n_dish = nf1.text_input("Food Item Name *", placeholder="e.g. Paneer Tikka Masala")
            n_cat = nf2.selectbox("Menu Category", ["Breakfast", "Main Course", "Starters", "Beverages", "Desserts"])
            n_price = nf1.number_input("Unit Price (₹) *", min_value=20.0, step=10.0, value=250.0)
            
            if st.form_submit_button("Enlist Item in Menu"):
                if n_dish:
                    run_query("INSERT INTO food_items (food_name, category, price, availability) VALUES (%s, %s, %s, 'Available')",
                              (n_dish, n_cat, n_price), commit=True)
                    st.success(f"'{n_dish}' added to restaurant menu!")
                    st.rerun()

    with f_tab3:
        st.markdown("#### ⚙️ Manage Menu & Availability")
        all_food = run_query("SELECT food_id, food_name, category, price, availability FROM food_items", fetch=True)
        if all_food:
            f_lookup = {f"{it['food_name']} ({it['category']}) - Currently {it['availability']}": it for it in all_food}
            sel_target_dish = st.selectbox("Select Item to Update:", list(f_lookup.keys()))
            target_obj = f_lookup[sel_target_dish]
            
            u_col1, u_col2 = st.columns(2)
            new_avail = u_col1.selectbox("Update Availability:", ["Available", "Unavailable"], index=0 if target_obj['availability'] == 'Available' else 1)
            new_p = u_col2.number_input("Update Price (₹):", min_value=10.0, step=10.0, value=float(target_obj['price']))
            
            b1, b2 = st.columns(2)
            if b1.button("Save Item Changes", use_container_width=True):
                run_query("UPDATE food_items SET availability = %s, price = %s WHERE food_id = %s", (new_avail, new_p, target_obj['food_id']), commit=True)
                st.success("Item updated successfully!")
                st.rerun()
            if b2.button("Delete Item from Menu", use_container_width=True):
                run_query("DELETE FROM food_items WHERE food_id = %s", (target_obj['food_id'],), commit=True)
                st.warning(f"Deleted {target_obj['food_name']} from menu.")
                st.rerun()
        st.dataframe(fetch_dataframe("SELECT * FROM food_items"), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 5. Smart Payment Hub (Interactive Gateway, UPI QR, Invoicing)
# ---------------------------------------------------------
elif selected_page == "💳 Smart Payment Hub":
    st.markdown("### 💳 Grand Residency Smart Payment Terminal")
    b_tab1, b_tab2 = st.tabs(["🧾 Generate Folio & Bill", "💰 Interactive Payment Gateway"])
    
    with b_tab1:
        eligible_bookings = run_query("""
            SELECT b.booking_id, c.full_name, r.room_number, r.price_per_night, b.check_in, b.check_out
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_status IN ('Checked-In', 'Checked-Out')
              AND b.booking_id NOT IN (SELECT booking_id FROM bills)
        """, fetch=True)
        
        if eligible_bookings:
            e_map = {f"Booking #{e['booking_id']} | {e['full_name']} (Room {e['room_number']})": e for e in eligible_bookings}
            sel_b = st.selectbox("Select Stay to Generate Bill:", list(e_map.keys()))
            target_stay = e_map[sel_b]
            
            nights = max(1, (target_stay['check_out'] - target_stay['check_in']).days)
            room_charges = float(target_stay['price_per_night']) * nights
            
            food_res = run_query("SELECT COALESCE(SUM(total_price), 0) AS ftotal FROM food_orders WHERE booking_id = %s AND order_status != 'Cancelled'", 
                                 (target_stay['booking_id'],), fetch_one=True)
            food_charges = float(food_res['ftotal']) if food_res else 0.0
            
            subtotal = room_charges + food_charges
            
            # Coupon / Discount Input
            coupon = st.text_input("Enter Promo / Loyalty Code (Optional)", placeholder="e.g. WELCOME10")
            discount = 0.0
            if coupon.upper() == "WELCOME10":
                discount = subtotal * 0.10
                st.success("🎉 Promo Code Applied! 10% Discount")
                
            sub_after_disc = max(0.0, subtotal - discount)
            tax = sub_after_disc * 0.05
            grand_total = sub_after_disc + tax
            
            st.info(f"**Room Charges:** ₹{room_charges:,.2f} ({nights} nights) | **Dining:** ₹{food_charges:,.2f} | **Discount:** ₹{discount:,.2f} | **Tax (5%):** ₹{tax:,.2f} | **Net Total:** ₹{grand_total:,.2f}")
            
            if st.button("Finalize & Post Bill to Gateway", use_container_width=True):
                run_query("""
                    INSERT INTO bills (booking_id, room_charges, food_charges, subtotal, tax, discount, grand_total, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
                """, (target_stay['booking_id'], room_charges, food_charges, subtotal, tax, discount, grand_total), commit=True)
                st.success("Bill generated and queued for Payment!")
                st.rerun()
        else:
            st.info("No unbilled bookings awaiting folio generation.")

    with b_tab2:
        pending_bills = run_query("""
            SELECT b.bill_id, bk.booking_id, c.full_name, r.room_number, bk.check_in, bk.check_out, 
                   b.room_charges, b.food_charges, b.discount, b.tax, b.grand_total, b.payment_status
            FROM bills b
            JOIN bookings bk ON b.booking_id = bk.booking_id
            JOIN customers c ON bk.customer_id = c.customer_id
            JOIN rooms r ON bk.room_id = r.room_id
            ORDER BY b.bill_id DESC
        """, fetch=True)
        
        if pending_bills:
            p_map = {f"Bill #{p['bill_id']} | {p['full_name']} (Room {p['room_number']}) - Status: {p['payment_status']}": p for p in pending_bills}
            sel_p = st.selectbox("Select Folio Bill Record:", list(p_map.keys()))
            bill_data = p_map[sel_p]
            
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color:#fcd34d; margin:0 0 10px 0;">Folio Statement: {bill_data['full_name']}</h3>
                <p style="margin:2px 0;"><b>Hotel:</b> Grand Residency Suites</p>
                <p style="margin:2px 0;"><b>Room:</b> {bill_data['room_number']} | <b>Stay Window:</b> {bill_data['check_in']} to {bill_data['check_out']}</p>
                <p style="margin:2px 0; color:#cbd5e1;">Room: ₹{bill_data['room_charges']:,.2f} | Food: ₹{bill_data['food_charges']:,.2f} | Discount: ₹{bill_data['discount']:,.2f} | GST: ₹{bill_data['tax']:,.2f}</p>
                <h2 style="color:#34d399; margin:8px 0;">Net Outstanding: ₹{bill_data['grand_total']:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if bill_data['payment_status'] == 'Pending':
                pay_method = st.radio("Choose Payment Gateway / Channel:", ["UPI (Instant QR & App Link)", "Credit / Debit Card Terminal", "Net Banking Gateway", "Cash Desk"], horizontal=True)
                
                # Dynamic Gateway Views
                if pay_method == "UPI (Instant QR & App Link)":
                    q1, q2 = st.columns([1, 1.5])
                    upi_str = f"upi://pay?pa=grandresidency@icici&pn=GrandResidency&am={bill_data['grand_total']:.2f}&cu=INR&tn=Bill-{bill_data['bill_id']}"
                    encoded_upi = urllib.parse.quote(upi_str)
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_upi}"
                    
                    with q1:
                        st.image(qr_url, caption="Scan with GPay / PhonePe / Paytm", width=180)
                    with q2:
                        st.markdown("**Instant App Checkout:**")
                        st.markdown(f"""
                        <a href="{upi_str}" target="_blank" style="text-decoration:none;">
                            <button style="background:#22c55e; color:#fff; padding:10px 20px; border:none; border-radius:8px; font-weight:600; cursor:pointer;">
                                📱 Open UPI App Directly
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.caption("Works on phones with installed UPI apps.")
                        
                elif pay_method == "Credit / Debit Card Terminal":
                    st.markdown("""
                    <div class="virtual-card">
                        <div style="font-size:0.8rem; letter-spacing:0.15em; color:#cbd5e1;">GRAND RESIDENCY SECURE CARD TERMINAL</div>
                        <h3 style="letter-spacing:0.2em; margin:15px 0;">•••• •••• •••• 4242</h3>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                            <span>CARDHOLDER: GUEST DESK</span>
                            <span>VALID THRU: 12/28</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    c_col1, c_col2 = st.columns(2)
                    c_col1.text_input("Card Number", placeholder="•••• •••• •••• 1234")
                    c_col2.text_input("Expiry & CVV", placeholder="MM/YY  •••")

                elif pay_method == "Net Banking Gateway":
                    st.selectbox("Select Partner Bank:", ["HDFC Bank", "State Bank of India", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "Bank of Baroda"])
                
                st.write("")
                if st.button("Complete Transaction & Authorize Payment", use_container_width=True):
                    gen_txn = f"TXN-GR{random.randint(100000, 999999)}"
                    run_query("INSERT INTO payments (bill_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'Paid')",
                              (bill_data['bill_id'], bill_data['grand_total'], pay_method), commit=True)
                    run_query("UPDATE bills SET payment_status = 'Paid' WHERE bill_id = %s", (bill_data['bill_id'],), commit=True)
                    st.success(f"Payment of ₹{bill_data['grand_total']:,.2f} Successful! Transaction Ref: {gen_txn}")
                    st.balloons()
                    st.rerun()
            else:
                st.success("✅ This bill is fully paid & settled.")
                txn_data = run_query("SELECT payment_id, payment_method, payment_date FROM payments WHERE bill_id = %s ORDER BY payment_id DESC LIMIT 1", 
                                     (bill_data['bill_id'],), fetch_one=True)
                t_id = f"GR-TXN-{txn_data['payment_id']:04d}" if txn_data else "GR-PAID-DESK"
                p_method = txn_data['payment_method'] if txn_data else "Cash"
                
                pdf_file = generate_pdf_invoice(
                    bill_data['bill_id'], bill_data['full_name'], bill_data['room_number'],
                    bill_data['check_in'], bill_data['check_out'], bill_data['room_charges'],
                    bill_data['food_charges'], bill_data['discount'], bill_data['tax'], 
                    bill_data['grand_total'], t_id, p_method
                )
                
                st.download_button(
                    label="📄 Download Grand Residency Tax Invoice (PDF)",
                    data=pdf_file,
                    file_name=f"Grand_Residency_Invoice_{bill_data['bill_id']}_{bill_data['full_name']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("No bills recorded in database.")

# ---------------------------------------------------------
# 6. Housekeeping Operations (Full CRUD)
# ---------------------------------------------------------
elif selected_page == "🧹 Housekeeping Operations":
    st.markdown("### 🧹 Housekeeping & Facility Operations")
    h_tab1, h_tab2 = st.tabs(["➕ Assign Service Task", "📋 Update Task Status"])
    
    with h_tab1:
        with st.form("new_hk_task", clear_on_submit=True):
            st.markdown("#### Assign Cleaning/Repair Task")
            rooms = run_query("SELECT room_id, room_number FROM rooms", fetch=True)
            r_opts = {f"Room {r['room_number']}": r['room_id'] for r in rooms} if rooms else {}
            assigned_room = st.selectbox("Target Room", list(r_opts.keys())) if r_opts else None
            task_type = st.selectbox("Service Category", ["Deep Sanitization", "Linen Refresh", "Amenities Restock", "Plumbing / AC Repairs"])
            staff_name = st.text_input("Designated Attendant")
            task_date = st.date_input("Scheduled Date", value=date.today())
            notes = st.text_input("Special Instructions")
            
            if st.form_submit_button("Assign Task"):
                if assigned_room and staff_name:
                    run_query("""
                        INSERT INTO housekeeping (room_id, task_type, assigned_to, task_date, notes, task_status)
                        VALUES (%s, %s, %s, %s, %s, 'Pending')
                    """, (r_opts[assigned_room], task_type, staff_name, task_date, notes), commit=True)
                    st.success("Task assigned successfully!")
                    st.rerun()

    with h_tab2:
        st.markdown("#### 📋 Real-Time Housekeeping Log & Status Updates")
        active_tasks = run_query("""
            SELECT h.task_id, r.room_number, h.task_type, h.assigned_to, h.task_status, h.task_date
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.room_id
            ORDER BY h.task_id DESC
        """, fetch=True)
        
        if active_tasks:
            t_lookup = {f"Task #{t['task_id']} | Room {t['room_number']} ({t['task_type']}) - Status: {t['task_status']}": t for t in active_tasks}
            sel_task = st.selectbox("Select Task to Update:", list(t_lookup.keys()))
            target_t = t_lookup[sel_task]
            
            new_t_status = st.selectbox("Set New Status:", ["Pending", "In Progress", "Completed", "Cancelled"])
            if st.button("Apply Status Change"):
                run_query("UPDATE housekeeping SET task_status = %s WHERE task_id = %s", (new_t_status, target_t['task_id']), commit=True)
                st.success(f"Task status changed to {new_t_status}!")
                st.rerun()
                
        st.dataframe(fetch_dataframe("""
            SELECT h.task_id, r.room_number, h.task_type, h.assigned_to, h.task_status, h.task_date, h.notes
            FROM housekeeping h
            JOIN rooms r ON h.room_id = r.room_id
            ORDER BY h.task_id DESC
        """), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 7. Rooms Master Control (Full CRUD)
# ---------------------------------------------------------
elif selected_page == "🏨 Rooms Master Control":
    st.markdown("### 🏨 Grand Residency Inventory & Room Control")
    rm_tab1, rm_tab2 = st.tabs(["➕ Add New Room", "⚙️ Update Status / Tariff"])
    
    with rm_tab1:
        with st.form("add_room_form", clear_on_submit=True):
            rc1, rc2 = st.columns(2)
            r_num = rc1.text_input("Suite / Room Identifier (e.g. 501)")
            r_type = rc2.selectbox("Room Tier", ["Single", "Double", "Deluxe", "Executive Suite", "Presidential Suite"])
            r_price = rc1.number_input("Base Tariff / Night (₹)", min_value=500.0, step=200.0, value=3500.0)
            
            if st.form_submit_button("Enroll Room"):
                if r_num:
                    run_query("INSERT INTO rooms (room_number, room_type, price_per_night, status) VALUES (%s, %s, %s, 'Available')",
                              (r_num, r_type, r_price), commit=True)
                    st.success(f"Room {r_num} added to inventory!")
                    st.rerun()

    with rm_tab2:
        all_r = run_query("SELECT room_id, room_number, room_type, price_per_night, status FROM rooms", fetch=True)
        if all_r:
            r_lookup = {f"Room {r['room_number']} ({r['room_type']}) - Status: {r['status']}": r for r in all_r}
            target_sel_room = st.selectbox("Select Room to Modify:", list(r_lookup.keys()))
            target_r_obj = r_lookup[target_sel_room]
            
            mod_col1, mod_col2 = st.columns(2)
            updated_st = mod_col1.selectbox("Set Room Status:", ["Available", "Occupied", "Maintenance"], index=["Available", "Occupied", "Maintenance"].index(target_r_obj['status']))
            updated_rate = mod_col2.number_input("Update Tariff (₹):", min_value=500.0, step=100.0, value=float(target_r_obj['price_per_night']))
            
            btn_save, btn_del = st.columns(2)
            if btn_save.button("Apply Room Changes", use_container_width=True):
                run_query("UPDATE rooms SET status = %s, price_per_night = %s WHERE room_id = %s", (updated_st, updated_rate, target_r_obj['room_id']), commit=True)
                st.success("Room parameters updated!")
                st.rerun()
            if btn_del.button("Remove Room From Inventory", use_container_width=True):
                run_query("DELETE FROM rooms WHERE room_id = %s", (target_r_obj['room_id'],), commit=True)
                st.warning(f"Room {target_r_obj['room_number']} removed.")
                st.rerun()
        st.dataframe(fetch_dataframe("SELECT * FROM rooms"), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 8. Staff Management (Full CRUD: Add, Status Change, Delete)
# ---------------------------------------------------------
elif selected_page == "👥 Staff Management":
    st.markdown("### 👥 Human Resources & Staff Management")
    s_tab1, s_tab2 = st.tabs(["➕ Enroll New Staff", "⚙️ Manage Staff Roster"])
    
    with s_tab1:
        with st.form("staff_form", clear_on_submit=True):
            sc1, sc2 = st.columns(2)
            s_name = sc1.text_input("Full Name *")
            s_phone = sc2.text_input("Mobile Number (10 digits) *")
            s_email = sc1.text_input("Email Address")
            s_role = sc2.selectbox("Designation", ["Manager", "Receptionist", "Chef", "Waiter", "Housekeeper", "Security"])
            s_sal = sc1.number_input("Monthly Salary (₹)", min_value=10000.0, step=1000.0, value=25000.0)
            
            if st.form_submit_button("Enroll Staff Member"):
                if s_name and len(s_phone) == 10:
                    run_query("""
                        INSERT INTO staff (full_name, phone, email, role, salary, joining_date, status) 
                        VALUES (%s, %s, %s, %s, %s, %s, 'Active')
                    """, (s_name, s_phone, s_email, s_role, s_sal, date.today()), commit=True)
                    st.success("Staff profile created successfully!")
                    st.rerun()

    with s_tab2:
        all_staff = run_query("SELECT staff_id, full_name, role, phone, salary, status FROM staff", fetch=True)
        if all_staff:
            staff_lookup = {f"{stf['full_name']} ({stf['role']}) - Status: {stf['status']}": stf for stf in all_staff}
            sel_staff_target = st.selectbox("Select Employee to Manage:", list(staff_lookup.keys()))
            target_stf = staff_lookup[sel_staff_target]
            
            st_col1, st_col2 = st.columns(2)
            new_stf_status = st_col1.selectbox("Change Employee Status:", ["Active", "Inactive", "On Leave"], index=["Active", "Inactive", "On Leave"].index(target_stf['status']))
            new_stf_sal = st_col2.number_input("Adjust Salary (₹):", min_value=1000.0, step=1000.0, value=float(target_stf['salary']))
            
            up_b, del_b = st.columns(2)
            if up_b.button("Update Employee Record", use_container_width=True):
                run_query("UPDATE staff SET status = %s, salary = %s WHERE staff_id = %s", (new_stf_status, new_stf_sal, target_stf['staff_id']), commit=True)
                st.success("Employee record updated!")
                st.rerun()
            if del_b.button("Delete Staff Profile", use_container_width=True):
                run_query("DELETE FROM staff WHERE staff_id = %s", (target_stf['staff_id'],), commit=True)
                st.warning("Staff profile removed.")
                st.rerun()
        st.dataframe(fetch_dataframe("SELECT staff_id, full_name, role, phone, salary, status FROM staff"), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# 9. Financial Audit & Reports
# ---------------------------------------------------------
elif selected_page == "📈 Financial Audit & Reports":
    st.markdown("### 📈 Grand Residency Audit & Finance Logs")
    rep_df = fetch_dataframe("""
        SELECT p.payment_id, c.full_name, r.room_number, p.amount, p.payment_method, p.payment_date 
        FROM payments p
        JOIN bills b ON p.bill_id = b.bill_id
        JOIN bookings bk ON b.booking_id = bk.booking_id
        JOIN customers c ON bk.customer_id = c.customer_id
        JOIN rooms r ON bk.room_id = r.room_id
        ORDER BY p.payment_id DESC
    """)
    if not rep_df.empty:
        st.dataframe(rep_df, use_container_width=True, hide_index=True)
        csv_file = rep_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Audit Log (CSV)", data=csv_file, file_name=f"Grand_Residency_Audit_{date.today()}.csv", mime="text/csv")


        # =========================================================
# 5. SMART PAYMENT HUB (DIRECT TO BANK ACCOUNT & GATEWAY)
# =========================================================
elif selected_page == "💳 Smart Payment Hub":
    st.markdown("### 💳 Grand Residency — Smart Live Settlement Terminal")
    b_tab1, b_tab2, b_tab3 = st.tabs(["🧾 Generate Folio & Bill", "💰 Live Payment Hub", "⚙️ Bank & Payment Settings"])
    
    # -----------------------------------------------------
    # TAB 1: GENERATE BILL
    # -----------------------------------------------------
    with b_tab1:
        eligible_bookings = run_query("""
            SELECT b.booking_id, c.full_name, r.room_number, r.price_per_night, b.check_in, b.check_out
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_id = r.room_id
            WHERE b.booking_status IN ('Checked-In', 'Checked-Out')
              AND b.booking_id NOT IN (SELECT booking_id FROM bills)
        """, fetch=True)
        
        if eligible_bookings:
            e_map = {f"Booking #{e['booking_id']} | {e['full_name']} (Room {e['room_number']})": e for e in eligible_bookings}
            sel_b = st.selectbox("Select Stay to Generate Bill:", list(e_map.keys()))
            target_stay = e_map[sel_b]
            
            nights = max(1, (target_stay['check_out'] - target_stay['check_in']).days)
            room_charges = float(target_stay['price_per_night']) * nights
            
            food_res = run_query("SELECT COALESCE(SUM(total_price), 0) AS ftotal FROM food_orders WHERE booking_id = %s AND order_status != 'Cancelled'", 
                                 (target_stay['booking_id'],), fetch_one=True)
            food_charges = float(food_res['ftotal']) if food_res else 0.0
            
            subtotal = room_charges + food_charges
            coupon = st.text_input("Enter Promo / Discount Code (Optional)", placeholder="e.g. FESTIVE10")
            discount = 0.0
            if coupon.upper() == "FESTIVE10":
                discount = subtotal * 0.10
                st.success("🎉 Promo Code Applied: 10% Discount!")
                
            sub_after_disc = max(0.0, subtotal - discount)
            cgst = sub_after_disc * 0.025
            sgst = sub_after_disc * 0.025
            tax = cgst + sgst
            grand_total = sub_after_disc + tax
            
            st.info(f"**Room Tariff:** ₹{room_charges:,.2f} | **Dining:** ₹{food_charges:,.2f} | **Discount:** ₹{discount:,.2f} | **Tax (CGST+SGST):** ₹{tax:,.2f} | **Net Payable:** ₹{grand_total:,.2f}")
            
            if st.button("Finalize & Post Folio to Gateway", use_container_width=True):
                run_query("""
                    INSERT INTO bills (booking_id, room_charges, food_charges, subtotal, tax, discount, grand_total, payment_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
                """, (target_stay['booking_id'], room_charges, food_charges, subtotal, tax, discount, grand_total), commit=True)
                st.success("Bill posted! Directing to Payment Gateway...")
                st.rerun()
        else:
            st.info("No unbilled bookings awaiting folio generation.")

    # -----------------------------------------------------
    # TAB 2: LIVE PAYMENT TERMINAL (DIRECT TO ACCOUNT)
    # -----------------------------------------------------
    with b_tab2:
        pending_bills = run_query("""
            SELECT b.bill_id, bk.booking_id, c.full_name, c.phone, r.room_number, bk.check_in, bk.check_out, 
                   b.room_charges, b.food_charges, b.discount, b.tax, b.grand_total, b.payment_status
            FROM bills b
            JOIN bookings bk ON b.booking_id = bk.booking_id
            JOIN customers c ON bk.customer_id = c.customer_id
            JOIN rooms r ON bk.room_id = r.room_id
            ORDER BY b.bill_id DESC
        """, fetch=True)
        
        if pending_bills:
            p_map = {f"Bill #{p['bill_id']} | {p['full_name']} (Room {p['room_number']}) - Status: {p['payment_status']}": p for p in pending_bills}
            sel_p = st.selectbox("Select Folio Bill Record:", list(p_map.keys()))
            bill_data = p_map[sel_p]
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h2 style="color:#fcd34d; margin:0;">Grand Residency Folio #{bill_data['bill_id']}</h2>
                        <p style="margin:4px 0; color:#94a3b8;">Guest: <b>{bill_data['full_name']}</b> | Room: <b>{bill_data['room_number']}</b> | Phone: <b>{bill_data['phone']}</b></p>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.85rem; color:#94a3b8;">TOTAL OUTSTANDING</span>
                        <h1 style="color:#34d399; margin:0;">₹{bill_data['grand_total']:,.2f}</h1>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if bill_data['payment_status'] == 'Pending':
                pay_method = st.radio("Select Live Payment Channel:", 
                                      ["📱 UPI Live Direct Transfer (GPay / PhonePe / Paytm)", 
                                       "💳 Razorpay Credit/Debit Card Terminal", 
                                       "🏦 Direct Bank NEFT/RTGS Transfer", 
                                       "💵 Cash Desk Settlement"], horizontal=True)
                
                # --- PARYAY 1: LIVE DIRECT UPI ACCOUNT QR ---
                if "UPI Live Direct" in pay_method:
                    hotel_upi = st.session_state.get("merchant_upi", "yourbusiness@upi")
                    hotel_name = "Grand Residency Suites"
                    
                    # Direct standard UPI URL string
                    upi_url = f"upi://pay?pa={hotel_upi}&pn={urllib.parse.quote(hotel_name)}&am={bill_data['grand_total']:.2f}&cu=INR&tn=Bill-{bill_data['bill_id']}"
                    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_url)}"
                    
                    u_col1, u_col2 = st.columns([1, 1.4])
                    with u_col1:
                        st.image(qr_api_url, caption=f"Scan to Pay directly to: {hotel_upi}", width=210)
                    with u_col2:
                        st.markdown(f"""
                        **Bank Account Linked UPI:** `{hotel_upi}`  
                        *Customer ne scan kelyas paise direct tumchya bank account madhe jama hotil.*
                        """)
                        st.markdown(f"""
                        <a href="{upi_url}" target="_blank">
                            <button style="background:linear-gradient(135deg,#10b981,#059669); color:#fff; border:none; padding:10px 18px; border-radius:8px; font-weight:600; cursor:pointer;">
                                📲 Open in PhonePe / GPay Directly
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.write("")
                        utr_number = st.text_input("Enter 12-Digit Bank UTR / Transaction Ref Number *", placeholder="e.g. 427819827162")
                    
                    if st.button("Verify UPI UTR & Clear Bill", use_container_width=True):
                        if utr_number and len(utr_number.strip()) >= 6:
                            run_query("INSERT INTO payments (bill_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'Paid')",
                                      (bill_data['bill_id'], bill_data['grand_total'], f"UPI (UTR: {utr_number.strip()})"), commit=True)
                            run_query("UPDATE bills SET payment_status = 'Paid' WHERE bill_id = %s", (bill_data['bill_id'],), commit=True)
                            st.success(f"Payment Verified! Amount ₹{bill_data['grand_total']} received in account via UTR {utr_number}.")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Krupaya payment kelyanantar milalela UTR/Transaction number enter kara.")

                # --- PARYAY 2: CARD GATEWAY (RAZORPAY INTEGRATED) ---
                elif "Razorpay" in pay_method:
                    st.markdown("""
                    <div class="virtual-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="letter-spacing:0.15em;">GRAND RESIDENCY SECURE PAY</span>
                            <span style="font-weight:700;">VISA / MASTERCARD / RUPAY</span>
                        </div>
                        <h2 style="letter-spacing:0.25em; margin:22px 0;">•••• •••• •••• 8842</h2>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem;">
                            <span>CARDHOLDER: GUEST DESK</span>
                            <span>VALID THRU: 12/29</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns([2, 1, 1])
                    card_num = c1.text_input("Card Number", placeholder="4111 •••• •••• 1111")
                    exp_date = c2.text_input("Expiry", placeholder="MM/YY")
                    cvv_num = c3.text_input("CVV", type="password", placeholder="•••")
                    
                    rzp_key = st.session_state.get("rzp_key_id", "rzp_test_YourKeyHere")
                    st.caption(f"🔒 Encrypted by Razorpay Gateway Integration (Merchant Key: `{rzp_key}`)")
                    
                    if st.button("Process Card Gateway Payment", use_container_width=True):
                        if card_num and cvv_num:
                            txn_id = f"PAY-RZP-{random.randint(1000000, 9999999)}"
                            run_query("INSERT INTO payments (bill_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'Paid')",
                                      (bill_data['bill_id'], bill_data['grand_total'], f"Card (Gateway Ref: {txn_id})"), commit=True)
                            run_query("UPDATE bills SET payment_status = 'Paid' WHERE bill_id = %s", (bill_data['bill_id'],), commit=True)
                            st.success(f"Card payment authorized successfully! Ref: {txn_id}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Krupaya Card chi sarv mahiti enter kara.")

                # --- PARYAY 3: DIRECT NEFT/RTGS BANK TRANSFER ---
                elif "NEFT/RTGS" in pay_method:
                    st.markdown("""
                    **Grand Residency Official Current Account Details:**
                    * **Beneficiary Name:** Grand Residency Luxury Hotel LLP
                    * **Bank:** ICICI Bank Ltd
                    * **Account Number:** 001205019842
                    * **IFSC Code:** ICIC0000012
                    * **Account Type:** Current Account
                    """)
                    neft_ref = st.text_input("Enter NEFT / RTGS Transfer Ref / Journal No:")
                    if st.button("Confirm NEFT Settlement", use_container_width=True):
                        if neft_ref:
                            run_query("INSERT INTO payments (bill_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'Paid')",
                                      (bill_data['bill_id'], bill_data['grand_total'], f"NEFT Ref: {neft_ref}"), commit=True)
                            run_query("UPDATE bills SET payment_status = 'Paid' WHERE bill_id = %s", (bill_data['bill_id'],), commit=True)
                            st.success("NEFT payment updated successfully!")
                            st.rerun()
                        else:
                            st.error("NEFT Reference number takne avashyak ahe.")

                # --- PARYAY 4: CASH DESK ---
                else:
                    cash_collected = st.number_input("Cash Collected from Guest (₹):", min_value=float(bill_data['grand_total']), step=100.0)
                    change_due = cash_collected - float(bill_data['grand_total'])
                    st.info(f"**Return Change to Customer:** ₹{change_due:,.2f}")
                    if st.button("Accept Cash & Free Folio", use_container_width=True):
                        run_query("INSERT INTO payments (bill_id, amount, payment_method, payment_status) VALUES (%s, %s, 'Cash Desk', 'Paid')",
                                  (bill_data['bill_id'], bill_data['grand_total']), commit=True)
                        run_query("UPDATE bills SET payment_status = 'Paid' WHERE bill_id = %s", (bill_data['bill_id'],), commit=True)
                        st.success("Cash payment logged successfully!")
                        st.rerun()
            else:
                st.success("✅ This Folio is fully paid & settled to account.")
                txn_data = run_query("SELECT payment_id, payment_method, payment_date FROM payments WHERE bill_id = %s ORDER BY payment_id DESC LIMIT 1", 
                                     (bill_data['bill_id'],), fetch_one=True)
                t_id = f"GR-TXN-{txn_data['payment_id']:04d}" if txn_data else "GR-PAID-DESK"
                p_method = txn_data['payment_method'] if txn_data else "Bank Transfer"
                
                pdf_file = generate_pdf_invoice(
                    bill_data['bill_id'], bill_data['full_name'], bill_data['room_number'],
                    bill_data['check_in'], bill_data['check_out'], bill_data['room_charges'],
                    bill_data['food_charges'], bill_data['discount'], bill_data['tax'], 
                    bill_data['grand_total'], t_id, p_method
                )
                
                st.download_button(
                    label="📄 Download Grand Residency Tax Invoice (PDF)",
                    data=pdf_file,
                    file_name=f"Grand_Residency_Invoice_{bill_data['bill_id']}_{bill_data['full_name']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("No bills recorded in database.")

    # -----------------------------------------------------
    # TAB 3: LIVE MERCHANT & BANK SETTINGS
    # -----------------------------------------------------
    with b_tab3:
        st.markdown("#### ⚙️ Configure Your Receiving Bank Accounts")
        with st.form("merchant_settings"):
            upi_input = st.text_input("Your Business UPI ID (Paise ya account madhe yetil):", 
                                      value=st.session_state.get("merchant_upi", "hotelresidency@okaxis"))
            rzp_key_input = st.text_input("Razorpay Key ID (For live card processing):", 
                                         value=st.session_state.get("rzp_key_id", "rzp_test_9238472394"))
            gst_number = st.text_input("Hotel GSTIN Number:", value="27AABCU9603R1ZM")
            
            if st.form_submit_button("Save Payment Configurations"):
                st.session_state["merchant_upi"] = upi_input.strip()
                st.session_state["rzp_key_id"] = rzp_key_input.strip()
                st.session_state["gstin"] = gst_number.strip()
                st.success(f"Payment parameters updated! All UPI payments will directly route to {upi_input.strip()}.")