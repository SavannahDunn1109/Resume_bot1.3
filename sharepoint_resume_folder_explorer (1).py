
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"
FOLDER_PATH = "/sites/Recruiting/Shared Documents"
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

# ========== SCAN CONFIRMED FOLDER ==========
def scan_confirmed_folder(ctx, folder_path):
    try:
        folder = ctx.web.get_folder_by_server_relative_url(folder_path)
        ctx.load(folder)
        ctx.load(folder.files)
        ctx.execute_query()

        st.subheader(f"📂 Folder: {folder_path}")
        if not folder.files:
            st.warning("⚠️ No files found in this folder.")

        for f in folder.files:
            name = f.properties.get("Name", "Unknown")
            if name.lower().endswith(TARGET_EXTENSIONS):
                st.write(f"📄 {name}")

    except Exception as e:
        st.error(f"❌ Could not access folder '{folder_path}': {e}")

# ========== MAIN ==========
st.title("📄 Resume Folder Scanner (Direct Path)")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

scan_confirmed_folder(ctx, FOLDER_PATH)
