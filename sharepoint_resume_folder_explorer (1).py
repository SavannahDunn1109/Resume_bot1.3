import streamlit as st
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# SharePoint credentials from Streamlit secrets
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 SharePoint Resume File Lister")
st.write("Pulling resume filenames from SharePoint folder...")

# --- Connect to SharePoint ---
def connect_to_sharepoint():
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)
    return ctx

# --- Load resume files from SharePoint ---
def load_resumes():
    ctx = connect_to_sharepoint()
    folder = ctx.web.get_folder_by_server_relative_url(FOLDER_PATH)
    ctx.load(folder.files)
    ctx.execute_query()
    return list(folder.files), ctx

# --- List resume files ---
try:
    files, ctx = load_resumes()

    if not files:
        st.warning("⚠️ No files found. Are you sure there are files in this folder?")
    else:
        st.success(f"✅ Found {len(files)} files in SharePoint folder.")
        for file in files:
            st.write(f"📄 {file.properties['Name']}")

except Exception as e:
    st.error(f"❌ Error accessing SharePoint: {e}")
