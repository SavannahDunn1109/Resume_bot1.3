import streamlit as st
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import os
import io
import docx2txt
import pdfplumber
import pandas as pd
import re
from io import BytesIO

# SharePoint credentials from Streamlit secrets
SHAREPOINT_SITE = "https://eleven090.sharepoint.com/sites/Recruiting"
USERNAME = st.secrets["sharepoint"]["username"]
PASSWORD = st.secrets["sharepoint"]["password"]
FOLDER_PATH = "/sites/Recruiting/Shared Documents/Active Resumes"

st.title("📄 Resume Scorer from SharePoint")
st.write("Pulling resumes from SharePoint and scoring using keywords + extracting summary info...")

# --- Connect to SharePoint ---
def connect_to_sharepoint():
    creds = UserCredential(USERNAME, PASSWORD)
    ctx = ClientContext(SHAREPOINT_SITE).with_credentials(creds)
    return ctx

# --- Extract text from PDF ---
def extract_text_from_pdf(content):
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# --- Extract text from DOCX ---
def extract_text_from_docx(content):
    with open("temp.docx", "wb") as f:
        f.write(content)
    return docx2txt.process("temp.docx")

# --- Keyword-based scoring ---
def score_resume(text, keywords):
    score = 0
    degree_found = False
    years_exp = 0

    # Degree scoring
    if re.search(r"(?i)bachelor|b\\.s|bs|ba", text):
        score += 50
        degree_found = True
    elif re.search(r"(?i)master|m\\.s|ms", text):
        score += 60
        degree_found = True

    # Experience scoring (e.g., "7 years experience")
    match = re.search(r"(\d{1,2})\\s+years", text, re.IGNORECASE)
    if match:
        years_exp = int(match.group(1))
        score += years_exp * 5

    # Keyword scoring
    for kw in keywords:
        if kw.lower() in text.lower():
            score += 10

    return score, degree_found, years_exp

# --- Load resume files from SharePoint ---
def load_resumes():
    ctx = connect_to_sharepoint()
    folder = ctx.web.get_folder_by_server_relative_url(FOLDER_PATH)
    ctx.load(folder.files)
    ctx.execute_query()
    return folder.files, ctx

# --- Upload keyword list ---
st.subheader("📄 Upload a keyword list (.txt)")
keyword_file = st.file_uploader("Upload Keyword List", type=["txt"])
keywords = []
if keyword_file:
    keywords = [line.strip() for line in keyword_file.read().decode("utf-8").splitlines() if line.strip()]
    st.success(f"✅ Loaded {len(keywords)} keywords")

# --- Process and score resumes ---
if keywords:
    try:
        files, ctx = load_resumes()

        if not files:
            st.warning("⚠️ No files found. Are you sure there are files in this folder?")
        else:
            st.success(f"✅ Found {len(files)} files in SharePoint folder.")
            for file in files:
                st.write(f"📄 {file.properties['Name']}")

        results = []
        for file in files:
            name = file.properties["Name"]
            url = file.properties["ServerRelativeUrl"]
            file_response = ctx.web.get_file_by_server_relative_url(url).download().execute_query()
            file_content = file_response.content

            if name.endswith(".pdf"):
                text = extract_text_from_pdf(file_content)
            elif name.endswith(".docx"):
                text = extract_text_from_docx(file_content)
            else:
                continue

            score, degree, exp = score_resume(text, keywords)

            results.append({
                "Name": name,
                "Degree Found": "Yes" if degree else "No",
                "Years Experience": exp,
                "Score": score
            })

        df = pd.DataFrame(results)
        st.dataframe(df)

        # --- Export option ---
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="📥 Download Results as Excel",
            data=output.getvalue(),
            file_name="resume_scores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error processing resumes: {e}")
else:
    st.warning("⚠️ Please upload a keyword .txt file to begin.")
