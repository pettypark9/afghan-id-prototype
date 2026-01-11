import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="National Identity System",
    page_icon="🇦🇫",
    layout="wide"
)

# File to store data
DB_FILE = "afghan_id_database.csv"

# --- 2. CSS STYLING (The Makeover) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header Style */
    .main-header {
        font-family: 'Arial', sans-serif;
        color: #1a1a1a;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #000000 33%, #be0000 33%, #be0000 66%, #009900 66%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    /* ID Card Style */
    .id-card {
        border: 2px solid #333;
        border-radius: 15px;
        padding: 0;
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        max-width: 500px;
        margin: auto;
        overflow: hidden;
        font-family: 'Courier New', monospace;
    }
    .card-header {
        background-color: #000;
        color: white;
        padding: 15px;
        text-align: center;
        border-bottom: 5px solid #be0000;
    }
    .card-body {
        padding: 20px;
        display: flex;
        align-items: center;
    }
    .photo-box {
        width: 120px;
        height: 150px;
        border: 2px dashed #ccc;
        background-color: #eee;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
    }
    .info-box {
        flex-grow: 1;
    }
    .card-footer {
        background-color: #009900;
        height: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. BACKEND FUNCTIONS ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["National ID", "Full Name", "Father Name", "Province", "DOB", "Gender", "Date"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def generate_id(province, year):
    # Generates a realistic ID: PROVINCE-YEAR-RANDOM
    prov_code = abs(hash(province)) % 99 + 1
    rand = random.randint(10000, 99999)
    return f"{prov_code:02d}-{year}-{rand}"

# --- 4. THE APP INTERFACE ---

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Emblem_of_Afghanistan_%282013%E2%80%932021%29.svg/200px-Emblem_of_Afghanistan_%282013%E2%80%932021%29.svg.png", width=100)
    st.title("Admin Panel")
    menu = st.radio("Navigation", ["✍️ New Registration", "🔍 Search Citizen", "📊 Database Stats"])
    st.info("System Status: 🟢 Online")

df = load_data()

# --- HEADER ---
st.markdown('<div class="main-header"><h1>Islamic Republic of Afghanistan<br>National Electronic ID (E-Tazkira)</h1></div>', unsafe_allow_html=True)

# --- PAGE: NEW REGISTRATION ---
if menu == "✍️ New Registration":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Citizen Details")
        with st.form("reg_form"):
            name = st.text_input("Full Name")
            father = st.text_input("Father's Name")
            
            c1, c2 = st.columns(2)
            with c1:
                dob = st.date_input("Date of Birth", min_value=datetime(1950, 1, 1))
            with c2:
                gender = st.selectbox("Gender", ["Male", "Female"])
                
            province = st.selectbox("Province", ["Kabul", "Herat", "Kandahar", "Balkh", "Nangarhar", "Helmand", "Bamyan"])
            
            st.markdown("---")
            st.subheader("2. Biometrics")
            photo = st.camera_input("Capture Face Photo")
            
            submit = st.form_submit_button("Generate Digital ID")

    with col2:
        st.subheader("3. Identity Preview")
        if submit and name and father and photo:
            # Generate ID
            new_id = generate_id(province, dob.year)
            
            # Save Data
            new_record = {
                "National ID": new_id, "Full Name": name, "Father Name": father,
                "Province": province, "DOB": str(dob), "Gender": gender,
                "Date": str(datetime.now().date())
            }
            df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
            save_data(df)
            
            # SHOW THE PRO CARD
            st.markdown(f"""
            <div class="id-card">
                <div class="card-header">
                    <h3>🇦🇫 NATIONAL IDENTITY CARD</h3>
                </div>
                <div class="card-body">
                    <div class="photo-box">
                        <img src="https://cdn-icons-png.flaticon.com/512/1077/1077114.png" width="80">
                    </div>
                    <div class="info-box">
                        <p><strong>ID Number:</strong> {new_id}</p>
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Father:</strong> {father}</p>
                        <p><strong>Province:</strong> {province}</p>
                        <p><strong>DOB:</strong> {dob}</p>
                    </div>
                </div>
                <div class="card-footer"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ Citizen Registered in National Database")
        else:
            st.info("👈 Fill out the form to preview the ID card.")

# --- PAGE: SEARCH ---
elif menu == "🔍 Search Citizen":
    st.subheader("Verify Identity")
    search_query = st.text_input("Enter National ID Number")
    
    if st.button("Search"):
        result = df[df['National ID'] == search_query]
        if not result.empty:
            st.success("✅ Verified: Valid ID Found")
            st.table(result)
        else:
            st.error("❌ Alert: ID Not Found")

# --- PAGE: STATS ---
elif menu == "📊 Database Stats":
    st.subheader("National Statistics")
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Citizens", len(df))
    m2.metric("Provinces Active", df['Province'].nunique())
    m3.metric("System Uptime", "99.9%")
    
    # Show Data
    with st.expander("View Full Registry"):
        st.dataframe(df)
        # Download Button
        st.download_button("Download CSV Backup", df.to_csv(index=False), "backup.csv")
