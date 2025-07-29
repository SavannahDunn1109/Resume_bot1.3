
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.folders.folder import Folder

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"
PATH_OPTIONS = [
    "Documents",
    "/Documents",
    "Shared Documents",
    "/Shared Documents",
    "/sites/Recruiting/Documents",
    "/sites/Recruiting/Shared Documents"
]
TARGET_EXTENSIONS = (".pdf", ".docx")

# ========== AUTH ==========
@st.cache_resource
def connect_to_sharepoint():
    ctx_auth = AuthenticationContext(SITE_URL)
    if not ctx_auth.acquire_token_for_user(
        st.secrets["sharepoint"]["username"],
        st.secrets["sharepoint"]["password"]
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
st.write("Trying multiple known SharePoint root paths...")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

for path in PATH_OPTIONS:
    st.subheader(f"🔎 Trying path: `{path}`")
    try:
        list_all_folders_and_files(ctx, path)
    except Exception as e:
        st.error(f"❌ Failed at `{path}`: {e}")
