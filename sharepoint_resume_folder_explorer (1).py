

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

# ========== SCAN LIBRARY ==========
def scan_library(ctx, name):
    try:
        library = ctx.web.lists.get_by_title(name).root_folder
        ctx.load(library)
        ctx.load(library.folders)
        ctx.load(library.files)
        ctx.execute_query()

        st.subheader(f"📂 Library: {name}")
        if not library.folders and not library.files:
            st.warning("⚠️ No folders or files found.")

        for folder in library.folders:
            fname = folder.properties.get("Name", "Unknown")
            furl = folder.properties.get("ServerRelativeUrl", "")
            st.write(f"📁 `{fname}` → `{furl}`")

        for file in library.files:
            fname = file.properties.get("Name", "Unknown")
            if fname.lower().endswith(TARGET_EXTENSIONS):
                st.write(f"📄 {fname}")

    except Exception as e:
        st.error(f"❌ Could not access library '{name}': {e}")

# ========== MAIN ==========
st.title("📚 SharePoint Real Library Scanner")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

for lib in LIBRARIES:
    scan_library(ctx, lib)


