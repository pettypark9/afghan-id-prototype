import streamlit as st
import pandas as pd
import os
import random
import datetime
from PIL import Image

# --- CONFIGURATION & SETUP ---
ST_PAGE_TITLE = "National ID Registry System"
DB_FILE = "database.csv"
PHOTO_DIR = "citizen_photos"

# Ensure directories exist
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Initialize CSV if it doesn't exist
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["NationalID", "FirstName", "FatherName", "Province", "RegDate", "PhotoPath"])
    df_init.to_csv(DB_FILE, index=False)

# List of Provinces (Sample)
PROVINCES = [
    "Kabul", "Herat", "Kandahar", "Balkh", "Nangarhar", 
    "Bamyan", "Kunduz", "Helmand", "Badakhshan", "Ghazni"
]

# --- UTILITY FUNCTIONS ---
def load_data():
    return pd.read_csv(DB_FILE, dtype={"NationalID": str})

def save_citizen(first_name, father_name, province, photo_bytes):
    # Generate random 12-digit ID
    nid = "".join([str(random.randint(0, 9)) for _ in range(12)])
    reg_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # Save Photo
    photo_filename = f"{nid}.jpg"
    photo_path = os.path.join(PHOTO_DIR, photo_filename)
    with open(photo_path, "wb") as f:
        f.write(photo_bytes)
        
    # Append to CSV
    new_data = pd.DataFrame({
        "NationalID": [nid],
        "FirstName": [first_name],
        "FatherName": [father_name],
        "Province": [province],
        "RegDate": [reg_date],
        "PhotoPath": [photo_path]
    })
    
    # Load existing, append, and save
    current_df = load_data()
    updated_df = pd.concat([current_df, new_data], ignore_index=True)
    updated_df.to_csv(DB_FILE, index=False)
    
    return nid, photo_path

# --- PAGE STYLING ---
st.set_page_config(page_title=ST_PAGE_TITLE, layout="centered")

st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        font-family: 'Helvetica', sans-serif;
        margin-bottom: 20px;
    }
    .id-card {
        background-color: #f8f9fa;
        border: 2px solid #1E3A8A;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        margin-top: 20px;
    }
    .card-title {
        color: #1E3A8A;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #ddd;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- MAIN APP LOGIC ---

st.markdown(f"<h1 class='main-header'>🏛️ {ST_PAGE_TITLE}</h1>", unsafe_allow_html=True)

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", ["New Registration", "Search Citizen", "Admin Stats"])

# 1. NEW REGISTRATION PAGE
if menu == "New Registration":
    st.subheader("📝 New Citizen Registration")
    
    with st.form("reg_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            f_name = st.text_input("First Name")
        with col2:
            father_name = st.text_input("Father's Name")
            
        province = st.selectbox("Province of Residence", PROVINCES)
        
        st.write("📸 **Capture Photo**")
        picture = st.camera_input("Take a picture")
        
        submitted = st.form_submit_button("Submit Registration")
        
        if submitted:
            if f_name and father_name and picture:
                # Save Data
                nid, p_path = save_citizen(f_name, father_name, province, picture.getbuffer())
                
                st.success("✅ Citizen Registered Successfully!")
                
                # Display Digital ID Card Preview
                st.markdown("### 🆔 Generated Digital ID Card")
                
                # Create a container that looks like a card
                with st.container():
                    st.markdown('<div class="id-card">', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(p_path, width=150)
                    with c2:
                        st.markdown(f"<h3 style='margin:0;'>NATIONAL IDENTITY CARD</h3>", unsafe_allow_html=True)
                        st.markdown(f"**ID Number:** `{nid}`")
                        st.markdown(f"**Name:** {f_name}")
                        st.markdown(f"**Father's Name:** {father_name}")
                        st.markdown(f"**Province:** {province}")
                        st.markdown(f"**Date:** {datetime.date.today()}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Please fill all text fields and take a photo.")

# 2. SEARCH CITIZEN PAGE
elif menu == "Search Citizen":
    st.subheader("🔍 Search Citizen Database")
    
    search_query = st.text_input("Enter 12-Digit National ID to Search")
    
    if st.button("Search"):
        df = load_data()
        result = df[df['NationalID'] == search_query]
        
        if not result.empty:
            record = result.iloc[0]
            st.success("Citizen Found!")
            
            # Display Card
            st.markdown('<div class="id-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([1, 2])
            with c1:
                if os.path.exists(record['PhotoPath']):
                    st.image(record['PhotoPath'], width=150)
                else:
                    st.warning("Photo not found on server.")
            with c2:
                st.markdown(f"**ID Number:** `{record['NationalID']}`")
                st.markdown(f"**Name:** {record['FirstName']}")
                st.markdown(f"**Father's Name:** {record['FatherName']}")
                st.markdown(f"**Province:** {record['Province']}")
                st.markdown(f"**Reg Date:** {record['RegDate']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.error("❌ No citizen found with that ID.")

# 3. ADMIN STATS PAGE
elif menu == "Admin Stats":
    st.subheader("📊 Administrative Statistics")
    
    df = load_data()
    
    if not df.empty:
        # High-level metrics
        total_citizens = len(df)
        unique_provinces = df['Province'].nunique()
        
        col1, col2 = st.columns(2)
        col1.metric("Total Registered Citizens", total_citizens)
        col2.metric("Provinces Covered", unique_provinces)
        
        st.markdown("---")
        
        # Province Breakdown Chart
        st.write("### Registrations by Province")
        prov_counts = df['Province'].value_counts()
        st.bar_chart(prov_counts)
        
        # Raw Data View
        with st.expander("View Raw Database Records"):
            st.dataframe(df)
    else:
        st.info("No data available yet. Go to 'New Registration' to add citizens.")

# Footer
st.markdown("---")
st.caption("© 2023 National Registry Prototype | Secure System")
