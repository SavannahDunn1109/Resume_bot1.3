import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file import File
from office365.sharepoint.folders.folder import Folder
import io
import pandas as pd
import os
from PyPDF2 import PdfReader
from docx import Document
from urllib.parse import quote

# ========== CONFIG ==========
SITE_URL = "https://eleven090.sharepoint.com/sites/Recruiting/Shared Documents/Active Resumes"
LIBRARY = "Shared Documents"
FOLDER = "Active Resumes"
KEYWORD_FILE = "Senior Software Key words.txt"
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

# ========== FILE HELPERS ==========
def download_file(ctx, file_url):
    response = File.open_binary(ctx, file_url)
    return io.BytesIO(response.content)

def extract_text_from_pdf(file_bytes):
    text = ""
    reader = PdfReader(file_bytes)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_bytes):
    doc = Document(file_bytes)
    return "\n".join([para.text for para in doc.paragraphs])

# ========== KEYWORD LOADING ==========
def load_keywords_from_file(file_path=KEYWORD_FILE):
    keywords = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(("🧠", "💼", "🎯", "👥", "🛡")):
                    keywords.append(line)
    return keywords

KEYWORDS = load_keywords_from_file()

uploaded_keywords = st.file_uploader("📄 Upload a keyword list (.txt)", type="txt")
if uploaded_keywords is not None:
    KEYWORDS = [
        line.strip() for line in uploaded_keywords.getvalue().decode("utf-8").splitlines()
        if line.strip() and not line.startswith(("🧠", "💼", "🎯", "👥", "🛡"))
    ]

# ========== SCORING ==========
def keyword_score_resume(text):
    score = 0
    found_keywords = []
    for kw in KEYWORDS:
        if kw.lower() in text.lower():
            score += 10
            found_keywords.append(kw)
    return score, ", ".join(found_keywords)

# ========== LOCAL SUMMARY (simple extraction) ==========
def extract_summary(text):
    lines = text.split("\n")
    name = "N/A"
    degree = "N/A"
    experience = "N/A"

    for line in lines:
        l = line.lower()
        if "bachelor" in l or "master" in l or "phd" in l:
            degree = line.strip()
        if "years of experience" in l or "experience" in l:
            experience = line.strip()
        if "name" in l and len(line.split()) <= 5:
            name = line.strip()
    return name, degree, experience

# ========== STREAMLIT UI ==========
st.title("📄 Resume Scorer from SharePoint")
st.write("Pulling resumes from SharePoint and scoring using keywords + extracting summary info...")

ctx = connect_to_sharepoint()

if ctx:
    folder_url = f"{LIBRARY}/{FOLDER}"
    folder = ctx.web.get_folder_by_server_relative_url(folder_url)
    files = folder.files
    ctx.load(files)
    ctx.execute_query()
    st.write("📂 Debug — files found:", [f.properties.get("Name") for f in folder.files])


    filenames = [f.properties.get("Name", "Unknown") for f in folder.files]
    if filenames:
        st.success("✅ Files found in SharePoint folder:")
        st.write(filenames)
    else:
        st.warning("⚠️ No files found in SharePoint folder.")
    except Exception as e:
    st.error(f"❌ Failed to access folder: {e}")
    st.stop()

results = []

for file in folder.files:
    filename = file.properties.get("Name", "Unknown")
    try:
        if not filename.endswith((".pdf", ".docx")):
            continue

        st.write(f"📄 Processing: `{filename}`")
        file_url = file.properties["ServerRelativeUrl"]
        file_bytes = download_file(ctx, file_url)
        text = extract_text_from_pdf(file_bytes) if filename.endswith(".pdf") else extract_text_from_docx(file_bytes)

        kw_score, keywords = keyword_score_resume(text)
        name, degree, experience = extract_summary(text)

        results.append({
            "File Name": filename,
            "Name": name,
            "Degree": degree,
            "Experience": experience,
            "Keyword Score": kw_score,
            "Keywords Found": keywords
        })

    except Exception as e:  # ✅ Now properly inside the for loop
        st.error(f"❌ Error processing {filename}: {e}")
        st.write(f"📄 Processing: `{filename}`")
        file_url = file.properties["ServerRelativeUrl"]
        file_bytes = download_file(ctx, file_url)
        text = extract_text_from_pdf(file_bytes) if filename.endswith(".pdf") else extract_text_from_docx(file_bytes)

        kw_score, keywords = keyword_score_resume(text)
        name, degree, experience = extract_summary(text)

        results.append({
            "File Name": filename,
            "Name": name,
            "Degree": degree,
            "Experience": experience,
            "Keyword Score": kw_score,
            "Keywords Found": keywords
        })

    except Exception as e:
        st.error(f"❌ Error processing {filename}: {e}")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    st.download_button("📥 Download Excel Report", output, file_name="resume_scores.xlsx")
else:
    st.info("ℹ️ No resumes were processed.")
