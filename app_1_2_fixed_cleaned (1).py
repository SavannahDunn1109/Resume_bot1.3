
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.folders.folder import Folder
import os

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"
ROOT_PATH = "Documents"
TARGET_EXTENSIONS = (".pdf", ".docx")

# ========== AUTH ==========
@st.cache_resource
def connect_to_sharepoint():
    from streamlit.runtime.secrets import secrets
    ctx_auth = AuthenticationContext(SITE_URL)
    if not ctx_auth.acquire_token_for_user(
        secrets["sharepoint"]["username"],
        secrets["sharepoint"]["password"]
    ):
        st.error("Authentication failed")
        return None
    return ClientContext(SITE_URL, ctx_auth)

# ========== RECURSIVE LISTING ==========
def list_all_folders_and_files(ctx, folder_url, depth=0):
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    ctx.load(folder)
    ctx.load(folder.folders)
    ctx.load(folder.files)
    ctx.execute_query()

    indent = "  " * depth
    st.write(f"{indent}📁 `{folder_url}`")

    for f in folder.files:
        name = f.properties.get("Name", "Unknown")
        if name.lower().endswith(TARGET_EXTENSIONS):
            st.write(f"{indent}  📄 {name}")

    for subfolder in folder.folders:
        sub_url = subfolder.properties["ServerRelativeUrl"]
        list_all_folders_and_files(ctx, sub_url, depth + 1)

# ========== MAIN ==========
st.title("📂 SharePoint Folder & Resume File Scanner")
st.write("Recursively listing all folders and .docx/.pdf files under 'Documents'...")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

try:
    list_all_folders_and_files(ctx, ROOT_PATH)
except Exception as e:
    st.error(f"❌ Failed to list folders and files: {e}")


    output.seek(0)
    st.download_button("📥 Download Excel Report", output, file_name="resume_scores.xlsx")
else:
    st.info("ℹ️ No resumes were processed.")

