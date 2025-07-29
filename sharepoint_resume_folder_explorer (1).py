
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# SharePoint connection details
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 Resume Folder Scanner (Improved)")
st.write("📂 Folder: " + FOLDER_PATH)

# --- Connect to SharePoint ---
def connect_to_sharepoint():
    credentials = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(credentials)
    return ctx

# --- Load Resumes ---
def load_files():
    ctx = connect_to_sharepoint()
    folder = ctx.web.get_folder_by_server_relative_url(FOLDER_PATH)
    ctx.load(folder.files)
    ctx.execute_query()
    return folder.files

# --- Display Results ---
try:
    files = load_files()

    if not files:
        st.warning("⚠️ No files found in this folder.")
    else:
        st.success(f"✅ Found {len(files)} files in SharePoint folder.")
        for file in files:
            st.write(f"📄 {file.properties['Name']}")

except Exception as e:
    st.error(f"❌ Error: {e}")

