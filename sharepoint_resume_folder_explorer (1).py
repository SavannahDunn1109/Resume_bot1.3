import streamlit as st

st.title("🔐 Streamlit Secrets Test")

# Check if 'sharepoint' section exists
if "sharepoint" in st.secrets:
    creds = st.secrets["sharepoint"]

    st.success("✅ SharePoint secrets loaded successfully!")
    st.write("📌 Username:", creds.get("username", "Not found"))
    
    # Optional: Only show masked password length
    password = creds.get("password", "")
    st.write("🔑 Password length:", len(password))
else:
    st.error("❌ 'sharepoint' section not found in secrets.")
