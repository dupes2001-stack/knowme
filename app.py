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
    st.subheader("📝 Add a Log Entry")
    with st.form("keyworker_log"):
        log_date = st.date_input("Date", value=date.today())
        carer_name = st.text_input("Your name")
        mood = st.selectbox("How was today?", [
            "😄 Great day", "🙂 Good day", "😐 Okay day",
            "😟 Difficult day", "😢 Very difficult day"
        ])
        food_drink = st.text_area("Food and drink today")
        sleep = st.text_input("Sleep (hours and quality)")
        notes = st.text_area("Notes and observations")
        incidents = st.text_area("Any incidents or concerns (leave blank if none)")
        submitted = st.form_submit_button("💙 Save Log Entry", use_container_width=True)
        if submitted:
            if carer_name:
                entry = {
                    "date": str(log_date), "carer": carer_name, "mood": mood,
                    "food_drink": food_drink, "sleep": sleep, "notes": notes,
                    "incidents": incidents, "timestamp": datetime.now().isoformat()
                }
                add_log_entry(data, child_id, entry)
                st.success("✅ Log entry saved! The parent will be able to see this.")
            else:
                st.error("Please enter your name.")

    st.divider()
    st.subheader("📖 Recent Log Entries")
    logs = get_logs(data, child_id)
    if logs:
        for log in reversed(logs[-10:]):
            st.markdown(f"""
            <div class="log-entry">
                <strong>📅 {log['date']}</strong> — Written by <strong>{log['carer']}</strong><br>
                <strong>Mood:</strong> {log['mood']}<br>
                {f"<strong>Food & Drink:</strong> {log['food_drink']}<br>" if log.get('food_drink') else ""}
                {f"<strong>Sleep:</strong> {log['sleep']}<br>" if log.get('sleep') else ""}
                {f"<strong>Notes:</strong> {log['notes']}<br>" if log.get('notes') else ""}
                {f"<strong>⚠️ Incidents:</strong> {log['incidents']}" if log.get('incidents') else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No log entries yet.")

# ── Login / Register ──────────────────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Know me before you care for me</p>
    </div>
    """, unsafe_allow_html=True)

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
            <p>If a parent has shared a KnowMe code with you, enter it below to view the child's profile and add log entries.</p>
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
                            <p style="margin:0;color:#666;">DOB: {dob_uk} | Age: {age_num} | {len(logs)} log entries</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("View", key=f"view_{child_id}", use_container_width=True):
                        st.session_state.selected_child = child_id
                        st.session_state.page = "view_child"
                        st.rerun()
                with col_c:
                    if st.button("📝 Log", key=f"log_{child_id}", use_container_width=True):
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
        if st.button("📝 Add Log", use_container_width=True):
            st.session_state.page = "add_log"
            st.rerun()
    with col_share:
        if st.button("🔗 Share Profile", use_container_width=True):
            st.session_state.page = "share_child"
            st.rerun()

    # PDF Download
    logs = get_logs(data, child_id)
    pdf_content = f"""KNOWME — CARE PROFILE
====================
Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')}

CHILD: {child.get('name','').upper()}
Age: {child.get('age','')}
Diagnosis: {child.get('diagnosis','')}
Communication: {child.get('communication','')}

EMERGENCY CONTACTS
------------------
Contact 1: {child.get('emergency_contact_1_name','')} — {child.get('emergency_contact_1_phone','')}
Contact 2: {child.get('emergency_contact_2_name','')} — {child.get('emergency_contact_2_phone','')}
GP: {child.get('gp_name','')} — {child.get('gp_phone','')}
Key Worker: {child.get('key_worker_name','')} — {child.get('key_worker_phone','')}

MEDICAL INFORMATION
-------------------
Allergies: {child.get('allergies','None')}
Medications: {child.get('medications','None')}
Epilepsy/Seizures: {child.get('epilepsy','No')}
Medical Notes: {child.get('medical_notes','None')}
Hospital Notes: {child.get('hospital_notes','None')}

TRIGGERS — THINGS THAT CAUSE DISTRESS
--------------------------------------
{child.get('triggers','None recorded')}

CALMING STRATEGIES — WHAT HELPS
---------------------------------
{child.get('calming_strategies','None recorded')}

ABOUT {child.get('name','').upper()}
{'—' * 30}
Loves: {child.get('likes','')}
Dislikes: {child.get('dislikes','')}
Comforters: {child.get('comforters','')}

FOOD & DRINK
------------
Favourite Foods: {child.get('favourite_foods','')}
Favourite Drinks: {child.get('favourite_drinks','')}
Avoid: {child.get('foods_to_avoid','None')}

DAILY ROUTINE
-------------
{child.get('daily_routine','Not recorded')}

SLEEP PATTERNS
--------------
{child.get('sleep_patterns','Not recorded')}

IMPORTANT NOTES FOR CARERS
---------------------------
{child.get('carer_notes','No additional notes')}

LOG ENTRIES ({len(logs)} total)
{'—' * 30}
"""
    for log in reversed(logs[-20:]):
        pdf_content += f"""
Date: {log['date']} — Written by: {log['carer']}
Mood: {log['mood']}
Food & Drink: {log.get('food_drink','')}
Sleep: {log.get('sleep','')}
Notes: {log.get('notes','')}
Incidents: {log.get('incidents','None')}
{'—' * 20}
"""

    st.download_button(
        label="📄 Download Profile as Text File",
        data=pdf_content,
        file_name=f"KnowMe_{child.get('name','profile').replace(' ','_')}_{datetime.now().strftime('%d%m%Y')}.txt",
        mime="text/plain",
        use_container_width=True
    )

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
    st.subheader("📖 Log Entries")
    logs = get_logs(data, child_id)
    if logs:
        for log in reversed(logs):
            st.markdown(f"""
            <div class="log-entry">
                <strong>📅 {log['date']}</strong> — Written by <strong>{log['carer']}</strong><br>
                <strong>Mood:</strong> {log['mood']}<br>
                {f"<strong>Food & Drink:</strong> {log['food_drink']}<br>" if log.get('food_drink') else ""}
                {f"<strong>Sleep:</strong> {log['sleep']}<br>" if log.get('sleep') else ""}
                {f"<strong>Activities:</strong> {log['activities']}<br>" if log.get('activities') else ""}
                {f"<strong>Notes:</strong> {log['notes']}<br>" if log.get('notes') else ""}
                {f"<strong>⚠️ Incidents:</strong> {log['incidents']}" if log.get('incidents') else ""}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No log entries yet. Add the first one!")

# ── Add Log ───────────────────────────────────────────────────────────────────
def show_add_log():
    data = load_data()
    child_id = st.session_state.selected_child
    child = get_child(data, child_id)

    st.markdown(f"""
    <div class="knowme-header">
        <h1>💙 KnowMe</h1>
        <p>Add Log Entry — {child.get('name','Child')}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Back"):
        st.session_state.page = "view_child"
        st.rerun()

    with st.form("add_log_form"):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", value=date.today())
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

        submitted = st.form_submit_button("💙 Save Log Entry", use_container_width=True)
        if submitted:
            entry = {
                "date": str(log_date), "carer": carer_name, "mood": mood,
                "sleep": sleep, "food_drink": food_drink, "activities": activities,
                "notes": notes, "incidents": incidents,
                "medication_given": medication_given,
                "timestamp": datetime.now().isoformat()
            }
            add_log_entry(data, child_id, entry)
            st.success("✅ Log entry saved!")
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
        They can use it to view the full profile and add daily log entries without needing an account.</p>
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
