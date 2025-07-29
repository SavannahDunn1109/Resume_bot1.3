import streamlit as st
from office365.runtime.auth.user_credential import UserCredential


# --- SharePoint credentials from Streamlit secrets ---
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 Resume Folder Scanner (Direct Path)")
st.write("📂 Folder: " + FOLDER_PATH)

# --- Connect to SharePoint ---
def connect_to_sharepoint():
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)
    return ctx

# --- Load files from SharePoint folder ---
def load_resumes(folder_path):
    ctx = connect_to_sharepoint()
    folder = ctx.web.get_folder_by_server_relative_url(folder_path)
    ctx.load(folder.files)
    ctx.execute_query()
    return folder.files

# --- Main execution ---
try:
    files = load_resumes(FOLDER_PATH)

    if not files:
        st.warning("⚠️ No files found in this folder.")
    else:
        st.success(f"✅ Found {len(files)} files in SharePoint folder.")
        for file in files:
            st.write(f"📄 {file.properties['Name']}")
            st.json(file.properties)  # Optional: shows full metadata

except Exception as e:
    st.error(f"❌ Error: {e}")


