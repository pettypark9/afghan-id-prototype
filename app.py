
import streamlit as st
import pandas as pd
import hashlib
import random
from datetime import datetime
import os

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="E-Tazkira Afghanistan",
    page_icon="🇦🇫",
    layout="centered"
)

# File to store data (simulated database)
DB_FILE = "afghan_id_database.csv"

# --- 2. BACKEND FUNCTIONS (The Logic) ---
def load_data():
    """Loads the citizen database from the CSV file."""
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Create a new empty database if one doesn't exist
        return pd.DataFrame(columns=[
            "National ID", "Full Name", "Father's Name", 
            "Province", "Date of Birth", "Gender", "Photo_Hash", "Registration Date"
        ])

def save_data(df):
    """Saves the database to the CSV file."""
    df.to_csv(DB_FILE, index=False)

def generate_national_id(province, birth_year):
    """Generates a realistic looking 13-digit ID based on province and birth year."""
    # Format: [Province Code][Year][Random Digits]
    # Example: 01-1990-837482
    prov_code = abs(hash(province)) % 99 + 1
    random_part = random.randint(100000, 999999)
    return f"{prov_code:02d}-{birth_year}-{random_part}"

# --- 3. FRONTEND INTERFACE (The Design) ---

# Sidebar Menu
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/5c/Emblem_of_Afghanistan_%282013%E2%80%932021%29.svg", width=100)
st.sidebar.title("National Identity System")
menu = st.sidebar.radio("Select Service", ["New Registration", "Verify ID", "Admin Dashboard"])

# Load Database
df = load_data()

# --- PAGE 1: NEW REGISTRATION ---
if menu == "New Registration":
    st.title("🇦🇫 New E-Tazkira Registration")
    st.markdown("---")
    
    with st.form("register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name (English/Dari)")
            father_name = st.text_input("Father's Name")
            grandfather_name = st.text_input("Grandfather's Name")
        
        with col2:
            dob = st.date_input("Date of Birth", min_value=datetime(1920, 1, 1))
            gender = st.selectbox("Gender", ["Male", "Female"])
            province = st.selectbox("Province of Origin", [
                "Kabul", "Herat", "Kandahar", "Balkh", "Nangarhar", 
                "Badakhshan", "Bamyan", "Kunduz", "Helmand", "Ghazni"
            ])

        st.markdown("### 📸 Biometric Capture")
        st.warning("Please look directly at the camera.")
        photo = st.camera_input("Take Official Photo")

        submitted = st.form_submit_button("Submit Application")

        if submitted:
            if full_name and father_name and photo:
                # 1. Generate ID
                new_id = generate_national_id(province, dob.year)
                
                # 2. Process Photo (In real life we save the image, here we just save a marker)
                photo_status = "Uploaded" 

                # 3. Create Record
                new_record = {
                    "National ID": new_id,
                    "Full Name": full_name,
                    "Father's Name": father_name,
                    "Province": province,
                    "Date of Birth": str(dob),
                    "Gender": gender,
                    "Photo_Hash": "biometric_data_secured",
                    "Registration Date": str(datetime.now())
                }
                
                # 4. Save to Database
                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                save_data(df)

                # 5. Success Message
                st.success("✅ Application Submitted Successfully!")
                st.balloons()
                
                # 6. Show the Digital Card
                st.info(f"Your National ID Number is: **{new_id}**")
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; border-radius: 10px; background-color: #f0f2f6;">
                    <h3>🇦🇫 Islamic Republic of Afghanistan</h3>
                    <h4>National Identity Card (E-Tazkira)</h4>
                    <hr>
                    <p><b>ID Number:</b> {new_id}</p>
                    <p><b>Name:</b> {full_name}</p>
                    <p><b>Father Name:</b> {father_name}</p>
                    <p><b>Province:</b> {province}</p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.error("❌ Please fill all fields and take a photo.")

# --- PAGE 2: VERIFY ID (Public Check) ---
elif menu == "Verify ID":
    st.title("🔍 Verify Citizen Identity")
    st.write("Enter a National ID number to verify if it exists in the central database.")
    
    search_id = st.text_input("Enter National ID Number (e.g., 12-1990-123456)")
    
    if st.button("Search Database"):
        result = df[df['National ID'] == search_id]
        
        if not result.empty:
            person = result.iloc[0]
            st.success("✅ Identity Verified")
            
            # Digital ID Card Display
            st.markdown(f"""
            <div style="background-color: #d1fae5; padding: 20px; border-radius: 10px; border: 2px solid #10b981;">
                <h2 style="color: #065f46;">✔ VALID ID</h2>
                <p><b>Name:</b> {person['Full Name']}</p>
                <p><b>Father's Name:</b> {person["Father's Name"]}</p>
                <p><b>Province:</b> {person['Province']}</p>
                <p><b>Status:</b> Active Citizen</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ ID Not Found in National Database.")

# --- PAGE 3: ADMIN DASHBOARD (Protected) ---
elif menu == "Admin Dashboard":
    st.title("🔐 Minister/Admin View")
    
    # Simple Password Check
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":
        st.success("Access Granted")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Citizens", len(df))
        col2.metric("Provinces Covered", df['Province'].nunique())
        col3.metric("Pending Updates", "0")
        
        # Data Table
        st.subheader("Central Database Records")
        st.dataframe(df)
        
        # Download Data
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full Database (CSV)", csv, "national_db.csv", "text/csv")
    elif password:
        st.error("Incorrect Password")
