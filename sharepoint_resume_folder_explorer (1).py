
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"
LIBRARIES = [
    "ResumeScores",
    "Site Assets",
    "Site Pages",
    "User Information List"
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

# ========== SCAN SELECTED LIBRARY ==========
def scan_selected_library(ctx, selected_library):
    try:
        folder = ctx.web.lists.get_by_title(selected_library).root_folder
        ctx.load(folder)
        ctx.load(folder.folders)
        ctx.load(folder.files)
        ctx.execute_query()

        st.subheader(f"📂 Library: {selected_library}")
        if not folder.folders and not folder.files:
            st.warning("⚠️ No folders or files found.")

        folder_paths = []
        for f in folder.folders:
            name = f.properties.get("Name", "Unknown")
            url = f.properties.get("ServerRelativeUrl", "")
            folder_paths.append(url)
            st.write(f"📁 `{name}` → `{url}`")

        for f in folder.files:
            name = f.properties.get("Name", "Unknown")
            if name.lower().endswith(TARGET_EXTENSIONS):
                st.write(f"📄 {name}")

        return folder_paths

    except Exception as e:
        st.error(f"❌ Could not access library '{selected_library}': {e}")
        return []

# ========== MAIN ==========
st.title("🔍 SharePoint Resume Folder Explorer")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

selected_library = st.selectbox("📚 Select a document library to explore:", LIBRARIES)
if selected_library:
    folder_urls = scan_selected_library(ctx, selected_library)
    if folder_urls:
        selected_folder = st.selectbox("📁 Choose a folder path to use in your app:", folder_urls)
        if selected_folder:
            st.success(f"✅ Copy and use this folder path in your resume app: {selected_folder}")




