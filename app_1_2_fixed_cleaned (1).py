
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"

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

# ========== MAIN ==========
st.title("🔍 SharePoint Top-Level Folder Scanner")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

try:
    web = ctx.web
    ctx.load(web)
    root_folder = web.root_folder
    ctx.load(root_folder)
    ctx.load(root_folder.folders)
    ctx.execute_query()

    st.subheader("📁 Top-Level Folders at Site Root:")
    for folder in root_folder.folders:
        name = folder.properties.get("Name", "Unknown")
        url = folder.properties.get("ServerRelativeUrl", "Unknown")
        st.write(f"📁 `{name}` → `{url}`")
