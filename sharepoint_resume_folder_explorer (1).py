import streamlit as st
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# SharePoint credentials from Streamlit secrets
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 Resume Folder Scanner (Improved)")
st.write("📂 Folder: " + FOLDER_PATH)

# --- Connect to SharePoint ---
def connect_to_sharepoint():
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)
    return ctx

# --- Load resume files from SharePoint ---
def load_resumes():
    ctx = connect_to_sharepoint()
folder = ctx.web.get_folder_by_server_relative_url(folder_url)
ctx.load(folder, ["Files"])
ctx.execute_query()

files = folder.files
ctx.load(files)
ctx.execute_query()




# --- Display resume file info ---
try:
    files, ctx = load_resumes()

    if not files:
        st.warning("⚠️ No files found in this folder.")
    else:
        st.success(f"✅ Found {len(files)} files:")
        for file in files:
            st.write(f"\n📄 {file.properties['Name']}")
            st.json({key: file.properties[key] for key in file.properties if key in [
                "Name", "ServerRelativeUrl", "TimeCreated", "TimeLastModified", "Length"
            ]})

except Exception as e:
    st.error(f"❌ Error: {e}")
