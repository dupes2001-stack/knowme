import streamlit as st
import json
import os
import hashlib
import uuid
import base64
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(
    page_title="KnowMe",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Quicksand:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }
h1, h2, h3 { font-family: 'Nunito', sans-serif; font-weight: 800; }

.main { background-color: #f0f7ff; }
.stApp { background: linear-gradient(135deg, #e8f4fd 0%, #f0f9f0 50%, #e8f4fd 100%); }

.knowme-header {
    background: linear-gradient(135deg, #2196F3 0%, #4CAF50 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(33,150,243,0.3);
}
.knowme-header h1 { font-size: 3rem; margin: 0; letter-spacing: -1px; }
.knowme-header p { font-size: 1.1rem; opacity: 0.9; margin: 0.5rem 0 0; }

.card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border-left: 5px solid #2196F3;
}
.card-green { border-left-color: #4CAF50; }
.card-red { border-left-color: #f44336; background: #fff5f5; }
.card-amber { border-left-color: #FF9800; background: #fffbf0; }
.card-blue { border-left-color: #2196F3; }

.emergency-banner {
    background: linear-gradient(135deg, #f44336, #e91e63);
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
}

.child-card {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    border: 2px solid transparent;
}

.share-box {
    background: #e3f2fd;
    border: 2px dashed #2196F3;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin: 1rem 0;
}

.log-entry {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    border-left: 4px solid #2196F3;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    line-height: 1.8;
}

.stButton > button {
    border-radius: 12px !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 700 !important;
}

/* ── Mobile optimisation ── */
@media (max-width: 768px) {
    .knowme-header h1 { font-size: 2rem !important; }
    .knowme-header { padding: 1.5rem !important; }
    .card { padding: 1rem !important; }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    .stButton > button {
        min-height: 55px !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input {
        font-size: 16px !important;
    }

    .knowme-header p { font-size: 0.95rem !important; }
    .log-entry { font-size: 0.9rem !important; }
    .card h3 { font-size: 1rem !important; }
    .card p { font-size: 0.9rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Data helpers ──────────────────────────────────────────────────────────────
DATA_FILE = "knowme_data.json"

def load_data():
    # Try Streamlit cloud storage first
    try:
        raw = st.session_state.get("_db")
        if raw:
            return json.loads(raw)
    except:
        pass
    # Fall back to local file
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            st.session_state["_db"] = json.dumps(d)
            return d
    empty = {"users": {}, "children": {}, "logs": {}, "share_tokens": {}}
    st.session_state["_db"] = json.dumps(empty)
    return empty

def save_data(data):
    # Always keep in session state
    st.session_state["_db"] = json.dumps(data)
    # Also write to local file when possible (local dev)
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_age(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        delta = relativedelta(today, dob)
        if delta.years > 0:
            return f"{delta.years} years, {delta.months} months"
        else:
            return f"{delta.months} months"
    except:
        return dob_str

def age_years(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        return relativedelta(today, dob).years
    except:
        return ""

def format_dob_uk(dob_str):
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        return dob.strftime("%d/%m/%Y")
    except:
        return dob_str

def encode_photo(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        encoded = base64.b64encode(bytes_data).decode()
        return f"data:{uploaded_file.type};base64,{encoded}"
    return None

def show_photo(photo_data, name, size=80):
    if photo_data:
        return f'<img src="{photo_data}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.2);">'
    initials = "".join([w[0].upper() for w in name.split()[:2]])
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:linear-gradient(135deg,#2196F3,#4CAF50);display:flex;align-items:center;justify-content:center;color:white;font-size:{size//3}px;font-weight:800;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.2);">{initials}</div>'

def create_user(data, email, password, name):
    if email in data["users"]:
        return False
    data["users"][email] = {
        "name": name, "email": email,
        "password": hash_password(password), "children": []
    }
    save_data(data)
    return True

def login_user(data, email, password):
    user = data["users"].get(email)
    if user and user["password"] == hash_password(password):
        return user
    return None

def save_child(data, child_id, child_data):
    data["children"][child_id] = child_data
    save_data(data)

def get_child(data, child_id):
    return data["children"].get(child_id)

def add_log_entry(data, child_id, entry):
    if child_id not in data["logs"]:
        data["logs"][child_id] = []
    data["logs"][child_id].append(entry)
    save_data(data)

def get_logs(data, child_id):
    return data["logs"].get(child_id, [])

def create_share_token(data, child_id):
    token = str(uuid.uuid4())[:8].upper()
    data["share_tokens"][token] = child_id
    save_data(data)
    return token

def get_child_from_token(data, token):
    child_id = data["share_tokens"].get(token.upper())
    if child_id:
        return child_id, get_child(data, child_id)
    return None, None

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("logged_in", False), ("user", None),
    ("page", "home"), ("selected_child", None), ("share_view", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Initialise DB in session if not present
if "_db" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state["_db"] = f.read()
    else:
        st.session_state["_db"] = json.dumps({"users": {}, "children": {}, "logs": {}, "share_tokens": {}})

data = load_data()

# ── Key worker share view ─────────────────────────────────────────────────────
def show_share_view(token):
    child_id, child = get_child_from_token(data, token)
    if not child:
        st.error("❌ Invalid or expired share code. Please ask the parent for a new one.")
        return

    photo_html = show_photo(child.get('photo'), child.get('name','?'), size=80)
    dob_uk = format_dob_uk(child.get('dob','')) if child.get('dob') else 'Not set'
    age_num = age_years(child.get('dob','')) if child.get('dob') else ''
    age_full = calculate_age(child.get('dob','')) if child.get('dob') else child.get('age','Not set')

    st.markdown(f"""
    <div class="knowme-header" style="display:flex;align-items:center;justify-content:center;gap:1.5rem;flex-wrap:wrap;">
        {photo_html}
        <div>
            <h1 style="margin:0;">💙 KnowMe</h1>
            <p style="margin:0.3rem 0 0;">Key Worker View — {child.get('name','Child')} | DOB: <strong>{dob_uk}</strong> | Age: <strong>{age_num}</strong></p>
        </div>
    </div>
    <div class="emergency-banner">🚨 EMERGENCY INFORMATION — READ FIRST</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card card-red">
            <h3>🆘 Emergency Contacts</h3>
            <p><strong>Parent/Guardian:</strong> {child.get('emergency_contact_1_name','Not provided')} — {child.get('emergency_contact_1_phone','')}</p>
            <p><strong>Secondary:</strong> {child.get('emergency_contact_2_name','Not provided')} — {child.get('emergency_contact_2_phone','')}</p>
            <p><strong>GP:</strong> {child.get('gp_name','Not provided')} — {child.get('gp_phone','')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card card-red">
            <h3>💊 Medical Info</h3>
            <p><strong>Allergies:</strong> {child.get('allergies','None recorded')}</p>
            <p><strong>Medications:</strong> {child.get('medications','None recorded')}</p>
            <p><strong>Epilepsy/Seizures:</strong> {child.get('epilepsy','No')}</p>
            <p><strong>Medical notes:</strong> {child.get('medical_notes','None')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card card-amber">
        <h3>⚠️ Triggers — Things that cause distress</h3>
        <p>{child.get('triggers','No triggers recorded')}</p>
    </div>
    <div class="card card-green">
        <h3>✅ Calming Strategies — What helps</h3>
        <p>{child.get('calming_strategies','No calming strategies recorded')}</p>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="card card-blue">
            <h3>😊 About {child.get('name','Child')}</h3>
            <p><strong>Age:</strong> {child.get('age','Not provided')}</p>
            <p><strong>Diagnosis:</strong> {child.get('diagnosis','Not provided')}</p>
            <p><strong>Communication:</strong> {child.get('communication','Not provided')}</p>
            <p><strong>Loves:</strong> {child.get('likes','Not provided')}</p>
            <p><strong>Dislikes:</strong> {child.get('dislikes','Not provided')}</p>
            <p><strong>Comforters:</strong> {child.get('comforters','Not provided')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="card card-green">
            <h3>🍽️ Food & Drink</h3>
            <p><strong>Favourite foods:</strong> {child.get('favourite_foods','Not provided')}</p>
            <p><strong>Favourite drinks:</strong> {child.get('favourite_drinks','Not provided')}</p>
            <p><strong>Avoid:</strong> {child.get('foods_to_avoid','None recorded')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <h3>📅 Daily Routine</h3>
        <p>{child.get('daily_routine','Not recorded')}</p>
    </div>
    <div class="card">
        <h3>📋 Important Notes for Carers</h3>
        <p>{child.get('carer_notes','No additional notes')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📖 Add a Journal Entry")
    with st.form("keyworker_log"):
        log_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        carer_name = st.text_input("Your name")
        mood = st.selectbox("How was today?", [
            "😄 Great day", "🙂 Good day", "😐 Okay day",
            "😟 Difficult day", "😢 Very difficult day"
        ])
        food_drink = st.text_area("Food and drink today")
        sleep = st.text_input("Sleep (hours and quality)")
        notes = st.text_area("Notes and observations")
        incidents = st.text_area("Any incidents or concerns (leave blank if none)")
        medication_given = st.checkbox("Medication given today")
        medication_times = st.text_input("💊 Medication times and doses", placeholder="e.g. 8am — 5mg Melatonin, 12pm — 10mg Ritalin")
        submitted = st.form_submit_button("💙 Save Journal Entry", use_container_width=True)
        if submitted:
            if carer_name:
                entry = {
                    "date": str(log_date), "carer": carer_name, "mood": mood,
                    "food_drink": food_drink, "sleep": sleep, "notes": notes,
                    "incidents": incidents, "medication_given": medication_given,
                    "medication_times": medication_times,
                    "timestamp": datetime.now().isoformat()
                }
                add_log_entry(data, child_id, entry)
                st.success("✅ Journal entry saved! The parent will be able to see this.")
            else:
                st.error("Please enter your name.")

    st.divider()
    st.subheader("📖 Recent Journal Entries")
    logs = get_logs(data, child_id)
    if logs:
        for log in reversed(logs[-10:]):
            try:
                log_date_uk = datetime.strptime(log['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                log_date_uk = log['date']
            food_html = f"<strong>Food & Drink:</strong> {log.get('food_drink','')}<br>" if log.get('food_drink') else ""
            sleep_html = f"<strong>Sleep:</strong> {log.get('sleep','')}<br>" if log.get('sleep') else ""
            notes_html = f"<strong>Notes:</strong> {log.get('notes','')}<br>" if log.get('notes') else ""
            med_html = f"<strong>💊 Medication:</strong> {log.get('medication_times','')}<br>" if log.get('medication_given') and log.get('medication_times') else ""
            inc_html = f"<strong>⚠️ Incidents:</strong> {log.get('incidents','')}" if log.get('incidents') else ""
            st.markdown(f"""
            <div class="log-entry">
                <strong>📅 {log_date_uk}</strong> — Written by <strong>{log['carer']}</strong><br>
                <strong>Mood:</strong> {log['mood']}<br>
                {food_html}{sleep_html}{notes_html}{med_html}{inc_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No journal entries yet.")

# ── Login / Register ──────────────────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Know me before you care for me</p>
    </div>
    """, unsafe_allow_html=True)

    # Landing page content
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 2rem;">
        <p style="font-size:1.2rem; color:#444; max-width:700px; margin:0 auto; line-height:1.8;">
        KnowMe is a care profile app designed for families of children with Special Educational 
        Needs and Disabilities (SEND). It gives every key worker, carer and teacher instant access 
        to everything they need to know about your child — before they even walk through the door.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="card card-blue" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem;">👶</div>
            <h3 style="color:#1a1a1a;">Child Profiles</h3>
            <p style="color:#333333;">Store everything about your child in one place. Likes, dislikes, triggers, calming strategies, food preferences, routines and more.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card card-green" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem;">🔗</div>
            <h3 style="color:#1a1a1a;">Instant Sharing</h3>
            <p style="color:#333333;">Share a unique code with any key worker, teacher or carer. They get instant access to your child's full profile — no account needed.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="card card-amber" style="text-align:center; padding:1.5rem;">
            <div style="font-size:2.5rem;">📝</div>
            <h3 style="color:#1a1a1a;">Daily Logs</h3>
            <p style="color:#333333;">Parents and carers can add daily journal entries. Track mood, food, sleep and behaviour — all in one shared place everyone can see.</p>
        </div>
        """, unsafe_allow_html=True)

    # Why KnowMe
    st.markdown("""
    <div class="card" style="margin-top:1rem; text-align:center;">
        <h3 style="color:#1a1a1a;">💙 Why KnowMe?</h3>
        <p style="line-height:1.8; color:#333333;">
        For families of children with SEND, every new carer, key worker or teacher means starting from scratch —
        repeating the same information over and over, hoping nothing important gets missed.
        KnowMe changes that. Whether your child has autism, ADHD, learning disabilities, physical disabilities,
        sensory needs or any other SEND diagnosis — build their profile once and share it instantly 
        with anyone who needs it. From emergency contacts to sensory triggers, from favourite foods 
        to calming strategies — everything is in one place, always up to date, always accessible.
        </p>
        <p style="font-weight:700; color:#2196F3; font-size:1.1rem;">
        Built by a SEND parent. Designed for families like yours. 💙
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Who is it for
    st.markdown("""
    <div class="card card-blue" style="margin-top:0.5rem;">
        <h3 style="color:#1a1a1a;">👨‍👩‍👧‍👦 Who is KnowMe for?</h3>
        <p style="color:#333333;">KnowMe is for any family of a child with SEND including:</p>
        <p style="color:#333333;">🧩 Autism Spectrum Condition &nbsp;|&nbsp; ⚡ ADHD &nbsp;|&nbsp; 🧠 Learning Disabilities &nbsp;|&nbsp; 👂 Sensory Processing Disorders &nbsp;|&nbsp; 🦽 Physical Disabilities &nbsp;|&nbsp; 💬 Speech and Language Needs &nbsp;|&nbsp; 🌈 Any other SEND diagnosis</p>
    </div>
    """, unsafe_allow_html=True)

    # Emergency section highlight
    st.markdown("""
    <div class="card card-red" style="margin-top:0.5rem;">
        <h3 style="color:#b71c1c;">🚨 Emergency Ready</h3>
        <p style="color:#333333;">Emergency contacts, medical information, allergies, medications and seizure information are always shown first — clearly highlighted so anyone can find what they need instantly in a crisis.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Get started")

    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Create Account", "🔗 Key Worker Access"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = login_user(data, email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("❌ Incorrect email or password.")

    with tab2:
        with st.form("register_form"):
            name = st.text_input("Your full name")
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            password2 = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not name or not email or not password:
                    st.error("Please fill in all fields.")
                elif password != password2:
                    st.error("Passwords don't match.")
                elif create_user(data, email, password, name):
                    st.success("✅ Account created! Please login.")
                else:
                    st.error("An account with this email already exists.")

    with tab3:
        st.markdown("""
        <div class="card">
            <h3>🔗 Key Worker / Carer Access</h3>
            <p>If a parent has shared a KnowMe code with you, enter it below to view the child's profile and add journal entries.</p>
        </div>
        """, unsafe_allow_html=True)
        share_code = st.text_input("Enter share code (e.g. ABC12345)")
        if st.button("View Profile", use_container_width=True):
            if share_code:
                child_id, child = get_child_from_token(data, share_code)
                if child:
                    st.session_state.share_view = share_code
                    st.rerun()
                else:
                    st.error("❌ Invalid share code. Please check with the parent.")

# ── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard():
    user = st.session_state.user
    data = load_data()

    st.markdown(f"""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Welcome back, {user['name'].split()[0]}! 👋</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("👶 My Children", use_container_width=True):
            st.session_state.page = "children"
            st.rerun()
    with col2:
        if st.button("➕ Add Child", use_container_width=True):
            st.session_state.page = "add_child"
            st.rerun()
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    st.divider()
    user_children = user.get("children", [])

    if not user_children:
        st.markdown("""
        <div class="card">
            <h3>👶 No children added yet</h3>
            <p>Click "Add Child" above to create your first child profile. Once created you can share it instantly with key workers, teachers and carers.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("👶 Your Children")
        for child_id in user_children:
            child = get_child(data, child_id)
            if child:
                logs = get_logs(data, child_id)
                col_a, col_b, col_c = st.columns([3,1,1])
                with col_a:
                    photo_html = show_photo(child.get('photo'), child.get('name','?'), size=60)
                    dob_uk = format_dob_uk(child.get('dob','')) if child.get('dob') else ''
                    age_num = age_years(child.get('dob','')) if child.get('dob') else child.get('age','')
                    st.markdown(f"""
                    <div class="child-card" style="display:flex;align-items:center;gap:1rem;">
                        {photo_html}
                        <div>
                            <h3 style="margin:0;">💙 {child.get('name','Unknown')}</h3>
                            <p style="margin:0;color:#666;">DOB: {dob_uk} | Age: {age_num} | {len(logs)} journal entries</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("View", key=f"view_{child_id}", use_container_width=True):
                        st.session_state.selected_child = child_id
                        st.session_state.page = "view_child"
                        st.rerun()
                with col_c:
                    if st.button("📖 Journal", key=f"log_{child_id}", use_container_width=True):
                        st.session_state.selected_child = child_id
                        st.session_state.page = "add_log"
                        st.rerun()

# ── Add Child ─────────────────────────────────────────────────────────────────
def show_add_child():
    st.markdown("""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Add a Child Profile</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    with st.form("add_child_form"):
        st.subheader("👶 Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's name *")
            dob = st.date_input("Date of birth", 
                min_value=date(2000,1,1), 
                max_value=date.today(),
                value=date(2018,1,1))
        with col2:
            diagnosis = st.text_input("Diagnosis")
            communication = st.text_input("Communication methods they use")
        
        photo = st.file_uploader("📷 Upload a photo of your child (optional)", 
                                  type=["jpg","jpeg","png"],
                                  help="This photo will be shown on their profile")

        st.subheader("😊 Personality & Preferences")
        col3, col4 = st.columns(2)
        with col3:
            likes = st.text_area("Things they love and enjoy")
            favourite_foods = st.text_area("Favourite foods")
            favourite_drinks = st.text_area("Favourite drinks")
        with col4:
            dislikes = st.text_area("Things they dislike or find difficult")
            foods_to_avoid = st.text_area("Foods/drinks to avoid or allergies")
            comforters = st.text_area("Favourite objects or comforters")

        st.subheader("⚠️ Triggers & Calming")
        col5, col6 = st.columns(2)
        with col5:
            triggers = st.text_area("Sensory triggers — what causes distress")
        with col6:
            calming_strategies = st.text_area("Calming strategies — what helps when upset")

        st.subheader("📋 Routine & Notes")
        col7, col8 = st.columns(2)
        with col7:
            daily_routine = st.text_area("Daily routine information")
            sleep_patterns = st.text_area("Sleep patterns")
        with col8:
            carer_notes = st.text_area("Important notes for new carers")

        st.subheader("🚨 Emergency Information")
        col9, col10 = st.columns(2)
        with col9:
            emergency_contact_1_name = st.text_input("Emergency contact 1 — name & relationship")
            emergency_contact_1_phone = st.text_input("Emergency contact 1 — phone number")
            emergency_contact_2_name = st.text_input("Emergency contact 2 — name & relationship")
            emergency_contact_2_phone = st.text_input("Emergency contact 2 — phone number")
        with col10:
            gp_name = st.text_input("GP name")
            gp_phone = st.text_input("GP phone number")
            key_worker_name = st.text_input("Key worker name")
            key_worker_phone = st.text_input("Key worker phone number")

        st.subheader("💊 Medical Information")
        col11, col12 = st.columns(2)
        with col11:
            allergies = st.text_area("Allergies (food and medication)")
            medications = st.text_area("Current medications and doses")
        with col12:
            epilepsy = st.selectbox("Epilepsy or seizures?", ["No", "Yes — see notes below"])
            medical_notes = st.text_area("Medical notes for emergency situations")
            hospital_notes = st.text_area("How child reacts in medical environments")

        submitted = st.form_submit_button("💙 Save Child Profile", use_container_width=True)
        if submitted:
            if not name:
                st.error("Please enter the child's name.")
            else:
                child_id = str(uuid.uuid4())
                photo_data = encode_photo(photo)
                child_data = {
                    "name": name, "dob": str(dob),
                    "age": calculate_age(str(dob)),
                    "photo": photo_data,
                    "diagnosis": diagnosis,
                    "communication": communication, "likes": likes,
                    "dislikes": dislikes, "favourite_foods": favourite_foods,
                    "favourite_drinks": favourite_drinks,
                    "foods_to_avoid": foods_to_avoid, "comforters": comforters,
                    "triggers": triggers, "calming_strategies": calming_strategies,
                    "daily_routine": daily_routine, "sleep_patterns": sleep_patterns,
                    "carer_notes": carer_notes,
                    "emergency_contact_1_name": emergency_contact_1_name,
                    "emergency_contact_1_phone": emergency_contact_1_phone,
                    "emergency_contact_2_name": emergency_contact_2_name,
                    "emergency_contact_2_phone": emergency_contact_2_phone,
                    "gp_name": gp_name, "gp_phone": gp_phone,
                    "key_worker_name": key_worker_name,
                    "key_worker_phone": key_worker_phone,
                    "allergies": allergies, "medications": medications,
                    "epilepsy": epilepsy, "medical_notes": medical_notes,
                    "hospital_notes": hospital_notes,
                    "created": datetime.now().isoformat()
                }
                save_child(data, child_id, child_data)
                user_email = st.session_state.user["email"]
                data["users"][user_email]["children"].append(child_id)
                save_data(data)
                st.session_state.user = data["users"][user_email]
                st.success(f"✅ Profile created for {name}!")
                st.session_state.page = "dashboard"
                st.rerun()

# ── PDF Generator ─────────────────────────────────────────────────────────────
def generate_person_centred_pdf(child):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    # Colours
    BLUE = colors.HexColor("#2196F3")
    GREEN = colors.HexColor("#4CAF50")
    RED = colors.HexColor("#f44336")
    AMBER = colors.HexColor("#FF9800")
    LIGHT_BLUE = colors.HexColor("#e3f2fd")
    LIGHT_GREEN = colors.HexColor("#e8f5e9")
    LIGHT_RED = colors.HexColor("#fff5f5")
    LIGHT_AMBER = colors.HexColor("#fffbf0")
    DARK = colors.HexColor("#1a1a1a")
    GREY = colors.HexColor("#666666")

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("title", fontSize=28, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle("subtitle", fontSize=13, textColor=colors.white,
        fontName="Helvetica", alignment=TA_CENTER)
    section_style = ParagraphStyle("section", fontSize=13, textColor=colors.white,
        fontName="Helvetica-Bold", spaceAfter=2)
    body_style = ParagraphStyle("body", fontSize=10, textColor=DARK,
        fontName="Helvetica", leading=16, spaceAfter=4)
    label_style = ParagraphStyle("label", fontSize=9, textColor=GREY,
        fontName="Helvetica-Bold", spaceAfter=2)
    name = child.get("name", "")
    dob_uk = format_dob_uk(child.get("dob","")) if child.get("dob") else ""
    age_num = age_years(child.get("dob","")) if child.get("dob") else ""
    diagnosis = child.get("diagnosis","")
    generated = datetime.now().strftime("%d/%m/%Y")

    story = []

    # ── Header banner ──
    header_data = [[
        Paragraph(f"Person Centred Overview", title_style),
        Paragraph(f"{name}", title_style),
    ]]
    header_table = Table(header_data, colWidths=[85*mm, 85*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [8,8,8,8]),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4*mm))

    # ── Subtitle info bar ──
    info_text = f"Date of Birth: {dob_uk}  |  Age: {age_num}  |  Diagnosis: {diagnosis}  |  Document date: {generated}"
    info_data = [[Paragraph(info_text, ParagraphStyle("info", fontSize=9,
        textColor=colors.white, fontName="Helvetica", alignment=TA_CENTER))]]
    info_table = Table(info_data, colWidths=[170*mm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GREEN),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [6,6,6,6]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))

    def section_header(text, colour):
        data = [[Paragraph(text, section_style)]]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colour),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("ROUNDEDCORNERS", (0,0), (-1,-1), [6,6,6,6]),
        ]))
        return t

    def info_row(label, value, bg=colors.white):
        if not value or value.strip() == "":
            return None
        data = [
            [Paragraph(label, label_style), Paragraph(value, body_style)]
        ]
        t = Table(data, colWidths=[45*mm, 125*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("LINEBELOW", (0,0), (-1,-1), 0.3, colors.HexColor("#e0e0e0")),
        ]))
        return t

    def full_row(label, value, bg=colors.white):
        if not value or value.strip() == "":
            return None
        data = [[Paragraph(f"<b>{label}</b><br/>{value}", body_style)]]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("LINEBELOW", (0,0), (-1,-1), 0.3, colors.HexColor("#e0e0e0")),
        ]))
        return t

    def add(item):
        if item:
            story.append(item)

    # ── About me ──
    story.append(section_header("About Me", BLUE))
    story.append(Spacer(1, 2*mm))
    add(full_row("My name is:", name, LIGHT_BLUE))
    add(info_row("Date of Birth:", dob_uk, LIGHT_BLUE))
    add(info_row("My age:", str(age_num), LIGHT_BLUE))
    add(info_row("My diagnosis:", diagnosis, LIGHT_BLUE))
    add(info_row("How I communicate:", child.get("communication",""), LIGHT_BLUE))
    story.append(Spacer(1, 5*mm))

    # ── What makes me, me ──
    story.append(section_header("What I Love — Things That Make Me Happy", GREEN))
    story.append(Spacer(1, 2*mm))
    add(full_row("I love:", child.get("likes",""), LIGHT_GREEN))
    add(full_row("My favourite foods are:", child.get("favourite_foods",""), LIGHT_GREEN))
    add(full_row("My favourite drinks are:", child.get("favourite_drinks",""), LIGHT_GREEN))
    add(full_row("My favourite objects and comforters are:", child.get("comforters",""), LIGHT_GREEN))
    story.append(Spacer(1, 5*mm))

    # ── What I find difficult ──
    story.append(section_header("What I Find Difficult", AMBER))
    story.append(Spacer(1, 2*mm))
    add(full_row("I find it hard when:", child.get("dislikes",""), LIGHT_AMBER))
    add(full_row("Please avoid giving me:", child.get("foods_to_avoid",""), LIGHT_AMBER))
    story.append(Spacer(1, 5*mm))

    # ── Triggers ──
    story.append(section_header("Things That Cause Me Distress — Please Be Aware", AMBER))
    story.append(Spacer(1, 2*mm))
    add(full_row("Things that trigger distress for me:", child.get("triggers",""), LIGHT_AMBER))
    story.append(Spacer(1, 5*mm))

    # ── Calming ──
    story.append(section_header("How Best To Support Me — What Helps", GREEN))
    story.append(Spacer(1, 2*mm))
    add(full_row("When I am distressed, this helps me:", child.get("calming_strategies",""), LIGHT_GREEN))
    story.append(Spacer(1, 5*mm))

    # ── My day ──
    story.append(section_header("My Day — Routine and Sleep", BLUE))
    story.append(Spacer(1, 2*mm))
    add(full_row("My daily routine:", child.get("daily_routine",""), LIGHT_BLUE))
    add(full_row("My sleep patterns:", child.get("sleep_patterns",""), LIGHT_BLUE))
    story.append(Spacer(1, 5*mm))

    # ── Important notes ──
    story.append(section_header("Important Notes For Anyone Supporting Me", BLUE))
    story.append(Spacer(1, 2*mm))
    add(full_row("Please know:", child.get("carer_notes",""), LIGHT_BLUE))
    story.append(Spacer(1, 5*mm))

    # ── Emergency ──
    story.append(section_header("EMERGENCY INFORMATION — PLEASE READ", RED))
    story.append(Spacer(1, 2*mm))
    add(info_row("Emergency Contact 1:", f"{child.get('emergency_contact_1_name','')} — {child.get('emergency_contact_1_phone','')}", LIGHT_RED))
    add(info_row("Emergency Contact 2:", f"{child.get('emergency_contact_2_name','')} — {child.get('emergency_contact_2_phone','')}", LIGHT_RED))
    add(info_row("GP:", f"{child.get('gp_name','')} — {child.get('gp_phone','')}", LIGHT_RED))
    add(info_row("Key Worker:", f"{child.get('key_worker_name','')} — {child.get('key_worker_phone','')}", LIGHT_RED))
    add(info_row("Allergies:", child.get("allergies","None"), LIGHT_RED))
    add(info_row("Medications:", child.get("medications","None"), LIGHT_RED))
    add(info_row("Epilepsy/Seizures:", child.get("epilepsy","No"), LIGHT_RED))
    add(full_row("Medical notes:", child.get("medical_notes",""), LIGHT_RED))
    add(full_row("In a medical environment:", child.get("hospital_notes",""), LIGHT_RED))
    story.append(Spacer(1, 8*mm))

    # ── Footer ──
    footer_data = [[Paragraph(
        f"This document was created using KnowMe — Know me before you care for me | Generated {generated}",
        ParagraphStyle("footer", fontSize=8, textColor=colors.white,
            fontName="Helvetica", alignment=TA_CENTER))]]
    footer_table = Table(footer_data, colWidths=[170*mm])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [6,6,6,6]),
    ]))
    story.append(footer_table)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ── PDF Generator V2 ──────────────────────────────────────────────────────────
def generate_person_centred_pdf(child):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    import io

    buffer = io.BytesIO()
    W = 180*mm
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm)

    BLUE       = colors.HexColor("#1976D2")
    BLUE_DARK  = colors.HexColor("#0D47A1")
    GREEN      = colors.HexColor("#388E3C")
    RED        = colors.HexColor("#C62828")
    AMBER      = colors.HexColor("#E65100")
    PURPLE     = colors.HexColor("#6A1B9A")
    TEAL       = colors.HexColor("#00695C")
    LIGHT_BLUE = colors.HexColor("#E3F2FD")
    LIGHT_GRN  = colors.HexColor("#E8F5E9")
    LIGHT_RED  = colors.HexColor("#FFEBEE")
    LIGHT_AMB  = colors.HexColor("#FFF3E0")
    LIGHT_PURP = colors.HexColor("#F3E5F5")
    LIGHT_TEAL = colors.HexColor("#E0F2F1")
    DARK       = colors.HexColor("#212121")
    MID        = colors.HexColor("#555555")

    def ps(nm, **kw):
        d = dict(fontName="Helvetica", fontSize=10, textColor=DARK, leading=15)
        d.update(kw)
        return ParagraphStyle(nm, **d)

    h_title = ps("ht", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white, alignment=TA_LEFT,  leading=24)
    h_name  = ps("hn", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white, alignment=TA_RIGHT, leading=24)
    h_sub   = ps("hs", fontName="Helvetica", fontSize=9, textColor=colors.white, alignment=TA_CENTER, leading=13)
    sec_hdr = ps("sh", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white, alignment=TA_LEFT, leading=14)
    lbl_s   = ps("lb", fontName="Helvetica-Bold", fontSize=9, textColor=MID, leading=13)
    body_s  = ps("bd", fontName="Helvetica", fontSize=10, textColor=DARK, leading=15)
    foot_s  = ps("ft", fontName="Helvetica", fontSize=8, textColor=colors.white, alignment=TA_CENTER, leading=11)

    name      = child.get("name", "")
    dob_uk    = format_dob_uk(child.get("dob","")) if child.get("dob") else "Not recorded"
    age_num   = str(age_years(child.get("dob",""))) if child.get("dob") else ""
    diagnosis = child.get("diagnosis","Not recorded")
    generated = datetime.now().strftime("%d/%m/%Y")

    story = []

    # Header
    hdr = Table([[Paragraph("My KnowMe Passport", h_title), Paragraph(name, h_name)]],
                colWidths=[W*0.55, W*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE),
        ("TOPPADDING",(0,0),(-1,-1),12), ("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),12), ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(hdr)

    sub = Table([[Paragraph(
        f"Date of Birth: <b>{dob_uk}</b> &nbsp;|&nbsp; Age: <b>{age_num}</b>"
        f" &nbsp;|&nbsp; Diagnosis: <b>{diagnosis}</b>"
        f" &nbsp;|&nbsp; Document date: <b>{generated}</b>", h_sub)]],
        colWidths=[W])
    sub.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(sub)
    story.append(Spacer(1, 5*mm))

    def sec(icon, title, colour):
        t = Table([[Paragraph(f"{icon}  {title}", sec_hdr)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colour),
            ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
        ]))
        story.append(t)

    LINE = colors.HexColor("#BDBDBD")

    def r2(label, value, bg):
        if not value or not str(value).strip(): return
        t = Table([[Paragraph(label, lbl_s), Paragraph(str(value), body_s)]],
                  colWidths=[W*0.30, W*0.70])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),bg),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("LINEBELOW",(0,0),(-1,-1),0.3,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        story.append(t)

    def r1(label, value, bg):
        if not value or not str(value).strip(): return
        t = Table([[Paragraph(f"<b>{label}</b>  {value}", body_s)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),bg),
            ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("LINEBELOW",(0,0),(-1,-1),0.3,LINE),
        ]))
        story.append(t)

    def gap(): story.append(Spacer(1, 4*mm))

    sec("👤", "About Me", BLUE)
    r2("My name is:", name, LIGHT_BLUE)
    r2("Date of Birth:", dob_uk, LIGHT_BLUE)
    r2("My age:", age_num, LIGHT_BLUE)
    r2("My diagnosis:", diagnosis, LIGHT_BLUE)
    r2("How I communicate:", child.get("communication",""), LIGHT_BLUE)
    gap()

    sec("❤️", "What I Love — Things That Make Me Happy", GREEN)
    r1("I love:", child.get("likes",""), LIGHT_GRN)
    r1("My favourite foods are:", child.get("favourite_foods",""), LIGHT_GRN)
    r1("My favourite drinks are:", child.get("favourite_drinks",""), LIGHT_GRN)
    r1("My favourite objects and comforters are:", child.get("comforters",""), LIGHT_GRN)
    gap()

    sec("💛", "What I Find Difficult", AMBER)
    r1("I find it hard when:", child.get("dislikes",""), LIGHT_AMB)
    r1("Please avoid giving me:", child.get("foods_to_avoid",""), LIGHT_AMB)
    gap()

    sec("⚠️", "Things That Cause Me Distress — Please Be Aware", AMBER)
    r1("Things that trigger distress for me:", child.get("triggers",""), LIGHT_AMB)
    gap()

    sec("✅", "How Best To Support Me — What Helps", GREEN)
    r1("When I am distressed, this helps me:", child.get("calming_strategies",""), LIGHT_GRN)
    gap()

    sec("📅", "My Day — Routine and Sleep", TEAL)
    r1("My daily routine:", child.get("daily_routine",""), LIGHT_TEAL)
    r1("My sleep patterns:", child.get("sleep_patterns",""), LIGHT_TEAL)
    gap()

    sec("📋", "Important Notes For Anyone Supporting Me", PURPLE)
    r1("Please know:", child.get("carer_notes",""), LIGHT_PURP)
    gap()

    sec("🚨", "EMERGENCY INFORMATION — PLEASE READ FIRST", RED)
    r2("Emergency Contact 1:", f"{child.get('emergency_contact_1_name','')}  {child.get('emergency_contact_1_phone','')}", LIGHT_RED)
    r2("Emergency Contact 2:", f"{child.get('emergency_contact_2_name','')}  {child.get('emergency_contact_2_phone','')}", LIGHT_RED)
    r2("GP:", f"{child.get('gp_name','')}  {child.get('gp_phone','')}", LIGHT_RED)
    r2("Key Worker:", f"{child.get('key_worker_name','')}  {child.get('key_worker_phone','')}", LIGHT_RED)
    r2("Allergies:", child.get("allergies","None"), LIGHT_RED)
    r2("Medications:", child.get("medications","None"), LIGHT_RED)
    r2("Epilepsy/Seizures:", child.get("epilepsy","No"), LIGHT_RED)
    r1("Medical notes:", child.get("medical_notes",""), LIGHT_RED)
    r1("In a medical environment:", child.get("hospital_notes",""), LIGHT_RED)
    gap()

    ft = Table([[Paragraph(
        f"My KnowMe Passport  |  Created with KnowMe — Know me before you care for me  |  Generated {generated}  |  CONFIDENTIAL",
        foot_s)]], colWidths=[W])
    ft.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
        ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(ft)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ── Journal Report PDF ────────────────────────────────────────────────────────────
def generate_log_report_pdf(child, logs, from_str, to_str):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io

    buffer = io.BytesIO()
    W = 180*mm
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm)

    BLUE      = colors.HexColor("#1976D2")
    BLUE_DARK = colors.HexColor("#0D47A1")
    GREEN     = colors.HexColor("#388E3C")
    RED       = colors.HexColor("#C62828")
    AMBER     = colors.HexColor("#E65100")
    LIGHT_BL  = colors.HexColor("#E3F2FD")
    LIGHT_GRN = colors.HexColor("#E8F5E9")
    LIGHT_RED = colors.HexColor("#FFEBEE")
    LIGHT_AMB = colors.HexColor("#FFF3E0")
    GREY_LT   = colors.HexColor("#F5F5F5")
    DARK      = colors.HexColor("#212121")
    MID       = colors.HexColor("#555555")
    LINE      = colors.HexColor("#BDBDBD")

    def ps(nm, **kw):
        d = dict(fontName="Helvetica", fontSize=10, textColor=DARK, leading=15)
        d.update(kw)
        return ParagraphStyle(nm, **d)

    h_title = ps("ht", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white, leading=24)
    h_name  = ps("hn", fontName="Helvetica-Bold", fontSize=20, textColor=colors.white, leading=24)
    h_sub   = ps("hs", fontName="Helvetica", fontSize=9, textColor=colors.white, alignment=TA_CENTER, leading=13)
    sec_hdr = ps("sh", fontName="Helvetica-Bold", fontSize=11, textColor=colors.white, leading=14)
    lbl_s   = ps("lb", fontName="Helvetica-Bold", fontSize=9, textColor=MID, leading=13)
    body_s  = ps("bd", fontName="Helvetica", fontSize=10, textColor=DARK, leading=15)
    foot_s  = ps("ft", fontName="Helvetica", fontSize=8, textColor=colors.white, alignment=TA_CENTER, leading=11)
    stat_s  = ps("st", fontName="Helvetica-Bold", fontSize=14, textColor=DARK, alignment=TA_CENTER, leading=18)
    stat_l  = ps("sl", fontName="Helvetica", fontSize=9, textColor=MID, alignment=TA_CENTER, leading=12)

    name      = child.get("name", "")
    generated = datetime.now().strftime("%d/%m/%Y")

    story = []

    # Header
    hdr = Table([[Paragraph("KnowMe Journal Report", h_title), Paragraph(name, h_name)]],
                colWidths=[W*0.55, W*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE),
        ("TOPPADDING",(0,0),(-1,-1),12), ("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),12), ("RIGHTPADDING",(0,0),(-1,-1),12),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story.append(hdr)

    sub = Table([[Paragraph(
        f"Date Range: <b>{from_str}</b> to <b>{to_str}</b>"
        f" &nbsp;|&nbsp; Total Entries: <b>{len(logs)}</b>"
        f" &nbsp;|&nbsp; Generated: <b>{generated}</b>", h_sub)]],
        colWidths=[W])
    sub.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
        ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(sub)
    story.append(Spacer(1, 5*mm))

    # Summary stats
    mood_counts = {}
    incident_days = 0
    for log in logs:
        mood = log.get("mood","")
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        if log.get("incidents","").strip():
            incident_days += 1

    great = mood_counts.get("😄 Great day", 0)
    good  = mood_counts.get("🙂 Good day", 0)
    okay  = mood_counts.get("😐 Okay day", 0)
    diff  = mood_counts.get("😟 Difficult day", 0)
    vdiff = mood_counts.get("😢 Very difficult day", 0)

    sec_t = Table([[Paragraph("📊  Summary", sec_hdr)]], colWidths=[W])
    sec_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(sec_t)

    stats = Table([
        [Paragraph(str(len(logs)), stat_s), Paragraph(str(great), stat_s),
         Paragraph(str(good), stat_s),  Paragraph(str(okay), stat_s),
         Paragraph(str(diff+vdiff), stat_s), Paragraph(str(incident_days), stat_s)],
        [Paragraph("Total Entries", stat_l), Paragraph("Great Days", stat_l),
         Paragraph("Good Days", stat_l), Paragraph("Okay Days", stat_l),
         Paragraph("Difficult Days", stat_l), Paragraph("Incident Days", stat_l)],
    ], colWidths=[W/6]*6)
    stats.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),LIGHT_BL),
        ("BACKGROUND",(5,0),(5,-1),LIGHT_RED),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("LINEAFTER",(0,0),(4,-1),0.5,LINE),
    ]))
    story.append(stats)
    story.append(Spacer(1, 5*mm))

    # ── Mood Chart ────────────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from reportlab.platypus import Image as RLImage
        import io as chart_io

        mood_score = {
            "😄 Great day": 5,
            "🙂 Good day": 4,
            "😐 Okay day": 3,
            "😟 Difficult day": 2,
            "😢 Very difficult day": 1,
        }
        mood_colour_map = {
            5: "#4CAF50", 4: "#8BC34A", 3: "#FF9800",
            2: "#F44336", 1: "#B71C1C",
        }

        sorted_logs_chart = sorted(logs, key=lambda x: x['date'])
        dates_labels = [
            datetime.strptime(l['date'], "%Y-%m-%d").strftime("%d/%m")
            for l in sorted_logs_chart
        ]
        scores = [mood_score.get(l.get("mood", ""), 3) for l in sorted_logs_chart]
        bar_cols = [mood_colour_map.get(s, "#FF9800") for s in scores]
        inc_marks = [bool(l.get("incidents", "").strip()) for l in sorted_logs_chart]

        fig, ax = plt.subplots(figsize=(10, 3))
        bars = ax.bar(range(len(scores)), scores, color=bar_cols, width=0.55,
                      zorder=2, edgecolor='white', linewidth=0.8)

        # Value labels on bars
        for i, s in enumerate(scores):
            label = {5:"Great",4:"Good",3:"Okay",2:"Difficult",1:"Very Difficult"}.get(s,"")
            ax.text(i, s/2, label, ha='center', va='center',
                    fontsize=6.5, color='white', fontweight='bold', zorder=5)

        for i, (s, inc) in enumerate(zip(scores, inc_marks)):
            if inc:
                ax.plot(i, s + 0.25, 'D', color='#B71C1C', markersize=6,
                        markeredgecolor='white', markeredgewidth=0.8, zorder=3)
                ax.text(i, s + 0.55, 'INCIDENT', ha='center', va='bottom',
                        fontsize=5.5, color='#B71C1C', fontweight='bold', zorder=4)

        ax.set_xticks(range(len(dates_labels)))
        ax.set_xticklabels(
            dates_labels, fontsize=7,
            rotation=45 if len(dates_labels) > 12 else 0
        )
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["Very Difficult", "Difficult", "Okay", "Good", "Great"], fontsize=7)
        ax.set_ylim(0, 6.5)
        ax.set_xlim(-0.5, max(len(scores) - 0.5, 0.5))
        ax.grid(axis='y', linestyle='--', alpha=0.4, zorder=1)
        ax.set_facecolor("#F8F9FA")
        fig.patch.set_facecolor("#FFFFFF")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_title(f"Mood Chart — {from_str} to {to_str}", fontsize=10, fontweight='bold', pad=10)

        patches = [
            mpatches.Patch(color="#4CAF50", label="Great"),
            mpatches.Patch(color="#8BC34A", label="Good"),
            mpatches.Patch(color="#FF9800", label="Okay"),
            mpatches.Patch(color="#F44336", label="Difficult"),
            mpatches.Patch(color="#B71C1C", label="Very Difficult"),
        ]
        ax.legend(handles=patches, loc='upper right', fontsize=7,
                  ncol=5, framealpha=0.8)

        plt.tight_layout()
        chart_buf = chart_io.BytesIO()
        plt.savefig(chart_buf, format='PNG', dpi=150, bbox_inches='tight',
                    facecolor='white')
        plt.close(fig)
        chart_buf.seek(0)

        img = RLImage(chart_buf, width=W, height=65*mm)
        story.append(img)
        story.append(Spacer(1, 2*mm))

        if any(inc_marks):
            note = Table([[Paragraph(
                "● Red diamond markers above bars indicate days where incidents were recorded",
                ps("note", fontSize=8, textColor=RED,
                   fontName="Helvetica-Oblique")
            )]], colWidths=[W])
            story.append(note)
        story.append(Spacer(1, 4*mm))

    except Exception as chart_err:
        story.append(Paragraph(
            f"Mood chart could not be generated: {chart_err}",
            ps("cerr", fontSize=8, textColor=RED)
        ))
        story.append(Spacer(1, 4*mm))

    # Journal entries
    sec_t2 = Table([[Paragraph("📋  Journal Entries", sec_hdr)]], colWidths=[W])
    sec_t2.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE),
        ("TOPPADDING",(0,0),(-1,-1),8), ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(sec_t2)

    for log in sorted(logs, key=lambda x: x['date']):
        has_incident = bool(log.get("incidents","").strip())
        bg = LIGHT_RED if has_incident else GREY_LT

        date_uk = datetime.strptime(log['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
        incident_marker = "  ⚠️ INCIDENT RECORDED" if has_incident else ""

        # Entry header row
        hrow = Table([[
            Paragraph(f"<b>📅 {date_uk}</b>{incident_marker}", ps("eh", fontName="Helvetica-Bold", fontSize=10, textColor=colors.white, leading=14)),
            Paragraph(f"Written by: {log.get('carer','')}", ps("ec", fontName="Helvetica", fontSize=9, textColor=colors.white, leading=14))
        ]], colWidths=[W*0.6, W*0.4])
        entry_colour = RED if has_incident else colors.HexColor("#455A64")
        hrow.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),entry_colour),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),8),
        ]))
        story.append(hrow)

        # Entry body
        def erow(label, value, bg=GREY_LT):
            if not value or not str(value).strip(): return
            t = Table([[Paragraph(label, lbl_s), Paragraph(str(value), body_s)]],
                      colWidths=[W*0.25, W*0.75])
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),bg),
                ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),8),
                ("LINEBELOW",(0,0),(-1,-1),0.3,LINE), ("VALIGN",(0,0),(-1,-1),"TOP"),
            ]))
            story.append(t)

        erow("Mood:", log.get("mood",""))
        erow("Food & Drink:", log.get("food_drink",""))
        erow("Sleep:", log.get("sleep",""))
        erow("Activities:", log.get("activities",""))
        erow("Notes:", log.get("notes",""))
        if log.get("medication_given") and log.get("medication_times","").strip():
            erow("💊 Medication:", log.get("medication_times",""), LIGHT_BL)
        if has_incident:
            erow("⚠️ Incidents:", log.get("incidents",""), LIGHT_RED)

        story.append(Spacer(1, 3*mm))

    # Footer
    ft = Table([[Paragraph(
        f"KnowMe Journal Report  |  {name}  |  {from_str} to {to_str}  |  Generated {generated}  |  CONFIDENTIAL",
        foot_s)]], colWidths=[W])
    ft.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLUE_DARK),
        ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(ft)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ── View Child ────────────────────────────────────────────────────────────────
def show_view_child():
    data = load_data()
    child_id = st.session_state.selected_child
    child = get_child(data, child_id)

    if not child:
        st.error("Child not found.")
        return

    photo_html = show_photo(child.get('photo'), child.get('name','?'), size=100)
    dob_uk = format_dob_uk(child.get('dob','')) if child.get('dob') else 'Not set'
    age_num = age_years(child.get('dob','')) if child.get('dob') else ''
    age_full = calculate_age(child.get('dob','')) if child.get('dob') else child.get('age','Not set')

    st.markdown(f"""
    <div class="knowme-header" style="display:flex;align-items:center;justify-content:center;gap:1.5rem;flex-wrap:wrap;">
        {photo_html}
        <div>
            <h1 style="margin:0;">💙 {child.get('name','Child')}</h1>
            <p style="margin:0.3rem 0 0;">📅 Date of Birth: <strong>{dob_uk}</strong> &nbsp;|&nbsp; 🎂 Age: <strong>{age_num}</strong> ({age_full})</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_back, col_edit, col_log, col_share = st.columns(4)
    with col_back:
        if st.button("← Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    with col_edit:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = "edit_child"
            st.rerun()
    with col_log:
        if st.button("📖 Add Journal", use_container_width=True):
            st.session_state.page = "add_log"
            st.rerun()
    with col_share:
        if st.button("🔗 Share Profile", use_container_width=True):
            st.session_state.page = "share_child"
            st.rerun()

    # PDF Download
    logs = get_logs(data, child_id)
    try:
        pdf_bytes = generate_person_centred_pdf(child)
        st.download_button(
            label="📄 Download My KnowMe Passport (PDF)",
            data=pdf_bytes,
            file_name=f"KnowMe_Passport_{child.get('name','').replace(' ','_')}_{datetime.now().strftime('%d%m%Y')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF generation error: {e}")

    st.markdown('<div class="emergency-banner">🚨 EMERGENCY INFORMATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card card-red">
            <h3>🆘 Emergency Contacts</h3>
            <p><strong>Contact 1:</strong> {child.get('emergency_contact_1_name','Not set')} — {child.get('emergency_contact_1_phone','')}</p>
            <p><strong>Contact 2:</strong> {child.get('emergency_contact_2_name','Not set')} — {child.get('emergency_contact_2_phone','')}</p>
            <p><strong>GP:</strong> {child.get('gp_name','Not set')} — {child.get('gp_phone','')}</p>
            <p><strong>Key Worker:</strong> {child.get('key_worker_name','Not set')} — {child.get('key_worker_phone','')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card card-red">
            <h3>💊 Medical Information</h3>
            <p><strong>Allergies:</strong> {child.get('allergies','None')}</p>
            <p><strong>Medications:</strong> {child.get('medications','None')}</p>
            <p><strong>Epilepsy:</strong> {child.get('epilepsy','No')}</p>
            <p><strong>Medical notes:</strong> {child.get('medical_notes','None')}</p>
            <p><strong>Hospital notes:</strong> {child.get('hospital_notes','None')}</p>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="card card-amber">
            <h3>⚠️ Triggers</h3>
            <p>{child.get('triggers','None recorded')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="card card-green">
            <h3>✅ Calming Strategies</h3>
            <p>{child.get('calming_strategies','None recorded')}</p>
        </div>
        """, unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="card card-blue">
            <h3>😊 About {child.get('name')}</h3>
            <p><strong>Date of Birth:</strong> {format_dob_uk(child.get('dob','')) if child.get('dob') else 'Not set'}</p>
            <p><strong>Age:</strong> {age_years(child.get('dob','')) if child.get('dob') else 'Not set'} ({calculate_age(child.get('dob','')) if child.get('dob') else ''})</p>
            <p><strong>Diagnosis:</strong> {child.get('diagnosis','Not set')}</p>
            <p><strong>Communication:</strong> {child.get('communication','Not set')}</p>
            <p><strong>Loves:</strong> {child.get('likes','Not set')}</p>
            <p><strong>Dislikes:</strong> {child.get('dislikes','Not set')}</p>
            <p><strong>Comforters:</strong> {child.get('comforters','Not set')}</p>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="card card-green">
            <h3>🍽️ Food & Drink</h3>
            <p><strong>Favourite foods:</strong> {child.get('favourite_foods','Not set')}</p>
            <p><strong>Favourite drinks:</strong> {child.get('favourite_drinks','Not set')}</p>
            <p><strong>Avoid:</strong> {child.get('foods_to_avoid','None')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <h3>📅 Daily Routine</h3>
        <p>{child.get('daily_routine','Not recorded')}</p>
    </div>
    <div class="card">
        <h3>😴 Sleep Patterns</h3>
        <p>{child.get('sleep_patterns','Not recorded')}</p>
    </div>
    <div class="card">
        <h3>📋 Important Notes for Carers</h3>
        <p>{child.get('carer_notes','No additional notes')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📖 Journal Entries")
    logs = get_logs(data, child_id)
    if logs:
        # Sort all logs newest first
        sorted_logs = sorted(logs, key=lambda x: x['date'], reverse=True)

        # Group by month
        from collections import defaultdict
        months = defaultdict(list)
        for log in sorted_logs:
            try:
                month_key = datetime.strptime(log['date'], "%Y-%m-%d").strftime("%B %Y")
            except:
                month_key = "Unknown"
            months[month_key].append(log)

        # Display each month as an expander
        for month_label, month_logs in months.items():
            incident_count = sum(1 for l in month_logs if l.get('incidents','').strip())
            incident_badge = f" 🔴 {incident_count} incident{'s' if incident_count>1 else ''}" if incident_count else ""
            with st.expander(f"📅 {month_label} — {len(month_logs)} {'entry' if len(month_logs)==1 else 'entries'}{incident_badge}"):
                for log in month_logs:
                    try:
                        log_date_uk = datetime.strptime(log['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        log_date_uk = log['date']
                    food_html = f"<strong>Food & Drink:</strong> {log.get('food_drink','')}<br>" if log.get('food_drink') else ""
                    sleep_html = f"<strong>Sleep:</strong> {log.get('sleep','')}<br>" if log.get('sleep') else ""
                    act_html = f"<strong>Activities:</strong> {log.get('activities','')}<br>" if log.get('activities') else ""
                    notes_html = f"<strong>Notes:</strong> {log.get('notes','')}<br>" if log.get('notes') else ""
                    med_html = f"<strong>💊 Medication:</strong> {log.get('medication_times','')}<br>" if log.get('medication_given') and log.get('medication_times') else ""
                    inc_html = f"<strong>⚠️ Incidents:</strong> {log.get('incidents','')}" if log.get('incidents') else ""
                    border_colour = "#f44336" if log.get('incidents') else "#2196F3"
                    st.markdown(f"""
                    <div class="log-entry" style="border-left-color:{border_colour};">
                        <strong>📅 {log_date_uk}</strong> — Written by <strong>{log['carer']}</strong><br>
                        <strong>Mood:</strong> {log['mood']}<br>
                        {food_html}{sleep_html}{act_html}{notes_html}{med_html}{inc_html}
                    </div>
                    """, unsafe_allow_html=True)

        # ── Journal Report Download ──
        st.divider()
        st.markdown("""
        <div class="card card-blue">
            <h3 style="color:#1a1a1a;">📊 Download Journal Report</h3>
            <p style="color:#333333;">Select a date range to download a PDF report of journal entries for that period. Useful for spotting patterns or sharing with professionals.</p>
        </div>
        """, unsafe_allow_html=True)

        all_dates = sorted([log['date'] for log in logs])
        min_date = datetime.strptime(all_dates[0], "%Y-%m-%d").date()
        max_date = datetime.strptime(all_dates[-1], "%Y-%m-%d").date()

        col_a, col_b = st.columns(2)
        with col_a:
            report_from = st.date_input("From date", value=min_date, min_value=min_date, max_value=max_date, key="report_from", format="DD/MM/YYYY")
        with col_b:
            report_to = st.date_input("To date", value=max_date, min_value=min_date, max_value=max_date, key="report_to", format="DD/MM/YYYY")

        # Inclusive filtering — convert both sides to string for safe comparison
        from_str_filter = report_from.strftime("%Y-%m-%d")
        to_str_filter   = report_to.strftime("%Y-%m-%d")
        filtered_logs   = [log for log in logs if from_str_filter <= log['date'] <= to_str_filter]
        filtered_logs   = sorted(filtered_logs, key=lambda x: x['date'])

        st.info(f"📋 {len(filtered_logs)} log {'entry' if len(filtered_logs)==1 else 'entries'} found in selected date range")

        if filtered_logs:
            try:
                log_pdf = generate_log_report_pdf(child, filtered_logs, report_from.strftime("%d/%m/%Y"), report_to.strftime("%d/%m/%Y"))
                st.download_button(
                    label="📊 Download Journal Report PDF",
                    data=log_pdf,
                    file_name=f"KnowMe_JournalReport_{child.get('name','').replace(' ','_')}_{report_from.strftime('%d%m%Y')}_to_{report_to.strftime('%d%m%Y')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")
        else:
            st.warning("No journal entries in selected date range.")
    else:
        st.info("No journal entries yet. Add the first one!")

# ── Add Journal ───────────────────────────────────────────────────────────────────
def show_add_log():
    data = load_data()
    child_id = st.session_state.selected_child
    child = get_child(data, child_id)

    st.markdown(f"""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Add Journal Entry — {child.get('name','Child')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.page = "view_child"
        st.rerun()

    with st.form("add_log_form"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today(), format="DD/MM/YYYY")
            carer_name = st.text_input("Written by", value=st.session_state.user["name"])
        with col2:
            mood = st.selectbox("How was today?", [
                "😄 Great day", "🙂 Good day", "😐 Okay day",
                "😟 Difficult day", "😢 Very difficult day"
            ])
            sleep = st.text_input("Sleep (hours and quality)")

        food_drink = st.text_area("Food and drink today")
        activities = st.text_area("Activities completed today")
        notes = st.text_area("Notes and observations")
        incidents = st.text_area("Any incidents or concerns (leave blank if none)")
        medication_given = st.checkbox("Medication given today")
        medication_times = st.text_input("💊 Medication times and doses", placeholder="e.g. 8am — 5mg Melatonin, 12pm — 10mg Ritalin")

        submitted = st.form_submit_button("💙 Save Journal Entry", use_container_width=True)
        if submitted:
            entry = {
                "date": str(log_date), "carer": carer_name, "mood": mood,
                "sleep": sleep, "food_drink": food_drink, "activities": activities,
                "notes": notes, "incidents": incidents,
                "medication_given": medication_given,
                "medication_times": medication_times,
                "timestamp": datetime.now().isoformat()
            }
            add_log_entry(data, child_id, entry)
            st.success("✅ Journal entry saved!")
            st.session_state.page = "view_child"
            st.rerun()

# ── Share Profile ─────────────────────────────────────────────────────────────
def show_share_child():
    data = load_data()
    child_id = st.session_state.selected_child
    child = get_child(data, child_id)

    st.markdown(f"""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Share {child.get('name','Child')}'s Profile</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Profile"):
        st.session_state.page = "view_child"
        st.rerun()

    st.markdown("""
    <div class="card">
        <h3>🔗 Share with Key Workers & Carers</h3>
        <p>Generate a unique share code and give it to key workers, teachers, or carers.
        They can use it to view the full profile and add daily journal entries without needing an account.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔗 Generate New Share Code", use_container_width=True):
        token = create_share_token(data, child_id)
        st.markdown(f"""
        <div class="share-box">
            <h2>Share Code: <strong>{token}</strong></h2>
            <p>Give this code to your key worker or carer.<br>
            They enter it on the KnowMe login page under "Key Worker Access".</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"💡 Tell them to enter code: {token} under Key Worker Access on the login page.")

    existing_tokens = [t for t, cid in data.get("share_tokens", {}).items() if cid == child_id]
    if existing_tokens:
        st.subheader("Your existing share codes:")
        for token in existing_tokens:
            st.code(token)

# ── Edit Child ────────────────────────────────────────────────────────────────
def show_edit_child():
    data = load_data()
    child_id = st.session_state.selected_child
    child = get_child(data, child_id)

    if not child:
        st.error("Child not found.")
        return

    st.markdown(f"""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Edit Profile — {child.get('name','Child')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back to Profile"):
        st.session_state.page = "view_child"
        st.rerun()

    with st.form("edit_child_form"):
        st.subheader("👶 Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's name *", value=child.get("name",""))
            try:
                dob_val = datetime.strptime(child.get("dob","2018-01-01"), "%Y-%m-%d").date()
            except:
                dob_val = date(2018,1,1)
            dob = st.date_input("Date of birth",
                value=dob_val,
                min_value=date(2000,1,1),
                max_value=date.today())
        with col2:
            diagnosis = st.text_input("Diagnosis", value=child.get("diagnosis",""))
            communication = st.text_input("Communication methods they use", value=child.get("communication",""))

        if child.get("photo"):
            st.markdown(f'Current photo: {show_photo(child.get("photo"), child.get("name","?"), size=60)}', unsafe_allow_html=True)
        photo = st.file_uploader("📷 Upload new photo (leave blank to keep current)", 
                                  type=["jpg","jpeg","png"])

        st.subheader("😊 Personality & Preferences")
        col3, col4 = st.columns(2)
        with col3:
            likes = st.text_area("Things they love and enjoy", value=child.get("likes",""))
            favourite_foods = st.text_area("Favourite foods", value=child.get("favourite_foods",""))
            favourite_drinks = st.text_area("Favourite drinks", value=child.get("favourite_drinks",""))
        with col4:
            dislikes = st.text_area("Things they dislike or find difficult", value=child.get("dislikes",""))
            foods_to_avoid = st.text_area("Foods/drinks to avoid or allergies", value=child.get("foods_to_avoid",""))
            comforters = st.text_area("Favourite objects or comforters", value=child.get("comforters",""))

        st.subheader("⚠️ Triggers & Calming")
        col5, col6 = st.columns(2)
        with col5:
            triggers = st.text_area("Sensory triggers — what causes distress", value=child.get("triggers",""))
        with col6:
            calming_strategies = st.text_area("Calming strategies — what helps when upset", value=child.get("calming_strategies",""))

        st.subheader("📋 Routine & Notes")
        col7, col8 = st.columns(2)
        with col7:
            daily_routine = st.text_area("Daily routine information", value=child.get("daily_routine",""))
            sleep_patterns = st.text_area("Sleep patterns", value=child.get("sleep_patterns",""))
        with col8:
            carer_notes = st.text_area("Important notes for new carers", value=child.get("carer_notes",""))

        st.subheader("🚨 Emergency Information")
        col9, col10 = st.columns(2)
        with col9:
            emergency_contact_1_name = st.text_input("Emergency contact 1 — name & relationship", value=child.get("emergency_contact_1_name",""))
            emergency_contact_1_phone = st.text_input("Emergency contact 1 — phone number", value=child.get("emergency_contact_1_phone",""))
            emergency_contact_2_name = st.text_input("Emergency contact 2 — name & relationship", value=child.get("emergency_contact_2_name",""))
            emergency_contact_2_phone = st.text_input("Emergency contact 2 — phone number", value=child.get("emergency_contact_2_phone",""))
        with col10:
            gp_name = st.text_input("GP name", value=child.get("gp_name",""))
            gp_phone = st.text_input("GP phone number", value=child.get("gp_phone",""))
            key_worker_name = st.text_input("Key worker name", value=child.get("key_worker_name",""))
            key_worker_phone = st.text_input("Key worker phone number", value=child.get("key_worker_phone",""))

        st.subheader("💊 Medical Information")
        col11, col12 = st.columns(2)
        with col11:
            allergies = st.text_area("Allergies (food and medication)", value=child.get("allergies",""))
            medications = st.text_area("Current medications and doses", value=child.get("medications",""))
        with col12:
            epilepsy_options = ["No", "Yes — see notes below"]
            epilepsy_index = epilepsy_options.index(child.get("epilepsy","No")) if child.get("epilepsy","No") in epilepsy_options else 0
            epilepsy = st.selectbox("Epilepsy or seizures?", epilepsy_options, index=epilepsy_index)
            medical_notes = st.text_area("Medical notes for emergency situations", value=child.get("medical_notes",""))
            hospital_notes = st.text_area("How child reacts in medical environments", value=child.get("hospital_notes",""))

        submitted = st.form_submit_button("💙 Save Changes", use_container_width=True)
        if submitted:
            if not name:
                st.error("Please enter the child's name.")
            else:
                updated = child.copy()
                new_photo = encode_photo(photo)
                updated.update({
                    "name": name, "dob": str(dob),
                    "age": calculate_age(str(dob)),
                    "photo": new_photo if new_photo else child.get("photo"),
                    "diagnosis": diagnosis,
                    "communication": communication, "likes": likes,
                    "dislikes": dislikes, "favourite_foods": favourite_foods,
                    "favourite_drinks": favourite_drinks,
                    "foods_to_avoid": foods_to_avoid, "comforters": comforters,
                    "triggers": triggers, "calming_strategies": calming_strategies,
                    "daily_routine": daily_routine, "sleep_patterns": sleep_patterns,
                    "carer_notes": carer_notes,
                    "emergency_contact_1_name": emergency_contact_1_name,
                    "emergency_contact_1_phone": emergency_contact_1_phone,
                    "emergency_contact_2_name": emergency_contact_2_name,
                    "emergency_contact_2_phone": emergency_contact_2_phone,
                    "gp_name": gp_name, "gp_phone": gp_phone,
                    "key_worker_name": key_worker_name,
                    "key_worker_phone": key_worker_phone,
                    "allergies": allergies, "medications": medications,
                    "epilepsy": epilepsy, "medical_notes": medical_notes,
                    "hospital_notes": hospital_notes,
                    "updated": datetime.now().isoformat()
                })
                save_child(data, child_id, updated)
                st.success(f"✅ Profile updated for {name}!")
                st.session_state.page = "view_child"
                st.rerun()

# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.share_view:
    show_share_view(st.session_state.share_view)
    st.divider()
    if st.button("← Exit Key Worker View"):
        st.session_state.share_view = None
        st.rerun()
elif not st.session_state.logged_in:
    show_auth()
elif st.session_state.page == "dashboard":
    show_dashboard()
elif st.session_state.page == "add_child":
    show_add_child()
elif st.session_state.page == "view_child":
    show_view_child()
elif st.session_state.page == "add_log":
    show_add_log()
elif st.session_state.page == "share_child":
    show_share_child()
elif st.session_state.page == "edit_child":
    show_edit_child()
else:
    show_dashboard()
