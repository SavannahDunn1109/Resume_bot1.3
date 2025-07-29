import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# Credentials and config
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
FOLDER_PATH = "Shared Documents/Active Resumes"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]

st.title("📄 Resume Folder Scanner (Improved)")
st.write(f"📂 Folder: /sites/Recruiting/{FOLDER_PATH}")

try:
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)

    folder_url = f"/sites/Recruiting/{FOLDER_PATH}"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    ctx.load(folder.files)
    ctx.execute_query()

    files = list(folder.files)

    if not files:
        st.warning("⚠️ No files found in this folder.")
    else:
        st.success(f"✅ Found {len(files)} files:")
        for file in files:
            st.write(f"📄 {file.properties['Name']}")

except Exception as e:
    st.error(f"❌ Error: {e}")
