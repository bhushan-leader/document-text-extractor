import streamlit as st
import pytesseract
import fitz  # This comes from the PyMuPDF library
 # PyMuPDF for PDF handling
import os

from PIL import Image
from docx import Document
from datetime import datetime

# Set Tesseract path (only for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Create folders to save files and texts
os.makedirs("extracted_docs", exist_ok=True)
os.makedirs("extracted_texts", exist_ok=True)

# Function to extract text
def extract_text(file):
    text = ""
    file_type = file.name.lower()

    if file_type.endswith(".docx"):
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])

    elif file_type.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()

    elif file_type.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)

    return text.strip()

# Save function
def save_file_and_text(file, text, source="upload"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if source == "camera":
        base_name = "camera"
        file_path = os.path.join("extracted_docs", f"{timestamp}_{base_name}.jpg")
        text_path = os.path.join("extracted_texts", f"{timestamp}_{base_name}.txt")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    else:
        base_name = os.path.splitext(file.name)[0]
        file_path = os.path.join("extracted_docs", f"{timestamp}_{file.name}")
        file.seek(0)
        with open(file_path, "wb") as f:
            f.write(file.read())
        text_path = os.path.join("extracted_texts", f"{timestamp}_{base_name}.txt")

    # Save text
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    st.success(f"✅ {source.capitalize()} file and extracted text saved!")

# Streamlit UI
st.set_page_config(page_title="Document Extractor", layout="centered")
st.title("📄 Document Text Extractor & Saver")

# Upload Section
uploaded_file = st.file_uploader("📂 Upload Word, PDF, or Image", type=["docx", "pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    extracted = extract_text(uploaded_file)
    st.text_area("📋 Extracted Text", extracted, height=300)
    if st.button("💾 Save Uploaded File and Text"):
        save_file_and_text(uploaded_file, extracted, source="upload")

# Camera Section
st.markdown("---")
st.header("📷 Capture Document via Camera")
camera_photo = st.camera_input("Take a photo")

if camera_photo:
    image = Image.open(camera_photo)
    text = pytesseract.image_to_string(image).strip()
    st.text_area("📋 Extracted Text from Camera", text, height=300)
    if st.button("💾 Save Camera Image and Text"):
        save_file_and_text(camera_photo, text, source="camera")
