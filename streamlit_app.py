import streamlit as st
import os
import base64
import tempfile
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from gtts import gTTS
from PIL import Image
import qrcode
import moviepy.editor as mp

# Title of the application
st.title("Crazy PDF Tool with Mind-Blasting Features")

# Upload PDF file
uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

# Function for PDF text extraction
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
        return text
    except Exception as e:
        return f"Error during text extraction: {e}"

# Function for OCR Text Extraction from Image
def ocr_from_image(image):
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error during OCR extraction: {e}"

# Function for PDF to Image conversion
def pdf_to_images(file):
    try:
        images = convert_from_path(file)
        return images
    except Exception as e:
        return f"Error during PDF to Image conversion: {e}"

# Function for QR code generation
def generate_qr_code(data):
    try:
        qr = qrcode.make(data)
        return qr
    except Exception as e:
        return f"Error during QR code generation: {e}"

# Function to generate speech from text
def generate_speech_from_text(text):
    try:
        tts = gTTS(text)
        tts.save("speech.mp3")
        return "speech.mp3"
    except Exception as e:
        return f"Error during speech generation: {e}"

# Function for displaying images and PDFs
def display_images(images):
    for img in images:
        st.image(img)

# If a file is uploaded
if uploaded_file is not None:
    st.write("File uploaded: ", uploaded_file.name)
    
    # Text Extraction
    if st.button("Extract Text from PDF"):
        text = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text", text, height=200)

    # OCR from PDF Images
    if st.button("OCR Text from PDF Images"):
        images = pdf_to_images(uploaded_file)
        if isinstance(images, list):
            ocr_text = ""
            for img in images:
                ocr_text += ocr_from_image(img)
            st.text_area("OCR Text", ocr_text, height=200)
        else:
            st.error(images)

    # Generate Speech from Text
    if st.button("Convert Extracted Text to Speech"):
        text = extract_text_from_pdf(uploaded_file)
        if text:
            audio_file = generate_speech_from_text(text)
            audio_file_bytes = open(audio_file, 'rb').read()
            audio_data = base64.b64encode(audio_file_bytes).decode()
            st.markdown(f'<audio controls><source src="data:audio/mp3;base64,{audio_data}" type="audio/mpeg"></audio>', unsafe_allow_html=True)

    # QR Code Generation
    qr_code_input = st.text_input("Enter Text for QR Code")
    if st.button("Generate QR Code") and qr_code_input:
        qr_image = generate_qr_code(qr_code_input)
        if isinstance(qr_image, Image.Image):
            st.image(qr_image, caption="Generated QR Code", use_column_width=True)

    # Clean up temporary files
    temp_files = ["speech.mp3"]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    # Handling video (if needed, convert to mp4)
    video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    if video_file:
        video_clip = mp.VideoFileClip(video_file)
        video_clip_resized = video_clip.resize(height=360)
        video_clip_resized.write_videofile("resized_video.mp4")
        st.video("resized_video.mp4")

