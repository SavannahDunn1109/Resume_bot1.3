
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.lists.list_collection import ListCollection

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting"
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

# ========== DISCOVER DOCUMENT LIBRARIES ==========
def get_document_libraries(ctx):
    try:
        lists = ctx.web.lists
        ctx.load(lists)
        ctx.execute_query()

        doc_libs = []
        for sp_list in lists:
            if sp_list.properties.get("BaseTemplate") == 101:  # 101 = Document Library
                doc_libs.append(sp_list.properties.get("Title"))
        return doc_libs
    except Exception as e:
        st.error(f"❌ Failed to fetch document libraries: {e}")
        return []

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
st.title("🔍 Dynamic SharePoint Library Explorer")

ctx = connect_to_sharepoint()
if not ctx:
    st.stop()

all_libraries = get_document_libraries(ctx)
selected_library = st.selectbox("📚 Select a document library to explore:", all_libraries)

if selected_library:
    folder_urls = scan_selected_library(ctx, selected_library)
    if folder_urls:
        selected_folder = st.selectbox("📁 Choose a folder path to use in your app:", folder_urls)
        if selected_folder:
            st.success(f"✅ Copy and use this folder path in your resume app: {selected_folder}")

