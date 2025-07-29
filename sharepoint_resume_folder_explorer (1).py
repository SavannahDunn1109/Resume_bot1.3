import streamlit as st
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import os

# SharePoint credentials (replace with your Streamlit secrets or secure method)
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]

# Target folder (update as needed)
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 Resume Folder Scanner (Improved)")
st.write(f"📂 Folder: `{FOLDER_PATH}`")

# Connect to SharePoint
def connect_to_sharepoint():
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)
    return ctx

# Load and list files
def list_files(folder_url):
    try:
        ctx = connect_to_sharepoint()
        folder = ctx.web.get_folder_by_server_relative_url(folder_url)
        ctx.load(folder, ["Files"])
        ctx.execute_query()

        files = folder.files
        ctx.load(files)
        ctx.execute_query()

        if not files:
            st.warning("⚠️ No files found in this folder.")
        else:
            st.success(f"✅ Found {len(files)} files:")
            for file in files:
                st.write("📄", file.properties.get("Name", "Unknown"))
                st.json(file.properties)  # Debug output

    except Exception as e:
        st.error(f"❌ Error accessing folder: {e}")

# Run the file scanner
list_files(FOLDER_PATH)
