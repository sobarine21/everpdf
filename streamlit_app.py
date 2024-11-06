import streamlit as st
import pdfplumber
import pdfkit
from markdown import markdown
from docx import Document
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import resize as video_resize
import pandas as pd
from PIL import Image
import io
import qrcode
import random
import string
from gtts import gTTS
import os

# Utility Functions

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def create_qr_code(data):
    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def visualize_data(df):
    st.line_chart(df)

# Streamlit App Layout
st.title("Enhanced File Type Converters & Media Processing")

# File Type Conversion Section
st.header("File Type Converters")

# PDF to Word Converter
pdf_file = st.file_uploader("Upload PDF Document for PDF to Word Conversion", type="pdf")
if pdf_file:
    if st.button("Convert PDF to Word"):
        with pdfplumber.open(pdf_file) as pdf:
            doc = Document()
            for page in pdf.pages:
                doc.add_paragraph(page.extract_text())
            word_file = io.BytesIO()
            doc.save(word_file)
            word_file.seek(0)
            st.download_button("Download Word Document", word_file, file_name="converted_document.docx")

# Markdown to HTML Converter
markdown_content = st.text_area("Enter Markdown Content for Conversion to HTML")
if st.button("Convert Markdown to HTML"):
    html_output = markdown(markdown_content)
    st.write("### HTML Output")
    st.code(html_output, language="html")

# Image Format Conversion (Improved Bytes-like object handling)
uploaded_image = st.file_uploader("Upload Image (JPG/PNG) for Format Conversion", type=["jpg", "jpeg", "png"])
if uploaded_image:
    img = Image.open(uploaded_image)
    format_choice = st.selectbox("Convert to Format", options=["PNG", "JPEG"])
    output_buffer = io.BytesIO()
    if st.button("Convert Image Format"):
        img.save(output_buffer, format=format_choice)
        output_buffer.seek(0)
        st.image(output_buffer, caption=f"Converted Image in {format_choice} format", use_column_width=True)

# Media Processing Section
st.header("Media Processing Features")

# Video Resizer
uploaded_video = st.file_uploader("Upload Video File for Resizing", type=["mp4", "avi"])
if uploaded_video:
    video_clip = VideoFileClip(uploaded_video.name)
    scale_factor = st.slider("Select Resize Scale Factor", min_value=0.1, max_value=1.0, value=0.5)
    if st.button("Resize Video"):
        resized_clip = video_clip.fx(video_resize, scale_factor)
        resized_video_buffer = io.BytesIO()
        resized_clip.write_videofile(resized_video_buffer)
        resized_video_buffer.seek(0)
        st.video(resized_video_buffer, format="video/mp4")

# QR Code Generator
qr_data = st.text_input("Enter data for QR Code")
if st.button("Generate QR Code"):
    qr_image = create_qr_code(qr_data)
    st.image(qr_image, caption="QR Code")
    st.download_button("Download QR Code", qr_image, file_name="qrcode.png")

# Random Password Generator
if st.button("Generate Random Password"):
    password = generate_random_password()
    st.write(f"Generated Password: {password}")

# Data Visualization
data_file = st.file_uploader("Upload CSV for Visualization", type="csv")
if data_file:
    df = pd.read_csv(data_file)
    visualize_data(df)

# Speech Conversion (Text-to-Speech)
text_to_speech_input = st.text_area("Enter Text for Text-to-Speech Conversion")
if st.button("Convert Text to Speech"):
    tts = gTTS(text=text_to_speech_input, lang='en')
    audio_buffer = io.BytesIO()
    tts.save(audio_buffer)
    audio_buffer.seek(0)
    st.audio(audio_buffer, format="audio/mp3")

# Clean up temporary files
temp_files = ["converted_html.pdf", "resized_video.mp4"]
for temp_file in temp_files:
    if os.path.exists(temp_file):
        os.remove(temp_file)
