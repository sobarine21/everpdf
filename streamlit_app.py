import streamlit as st
from PyPDF2 import PdfReader
import pytesseract
from gtts import gTTS
from PIL import Image
import tempfile
import pdf2image
import qrcode
import moviepy.editor as mp
import os
from fpdf import FPDF
import cv2
import requests
from io import BytesIO

# Function to process PDF and extract text
def extract_pdf_text(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {e}")
        return None

# Function for OCR (Optical Character Recognition) on an image
def ocr_image(image):
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error performing OCR: {e}")
        return None

# Function to create a text-to-speech MP3 file
def text_to_speech(text):
    try:
        tts = gTTS(text)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")
        return None

# Function to convert a PDF to images
def convert_pdf_to_images(uploaded_file):
    try:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        return images
    except Exception as e:
        st.error(f"Error converting PDF to images: {e}")
        return None

# Function to generate a QR code from text
def generate_qrcode(data):
    try:
        img = qrcode.make(data)
        return img
    except Exception as e:
        st.error(f"Error generating QR code: {e}")
        return None

# Function to resize a video (Example of video processing)
def resize_video(uploaded_video):
    try:
        video = mp.VideoFileClip(uploaded_video)
        resized_video = video.resize(height=360)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        resized_video.write_videofile(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error resizing video: {e}")
        return None

# Function to download a file from the URL
def download_file_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Failed to download file from URL: {url}")
            return None
    except Exception as e:
        st.error(f"Error downloading file: {e}")
        return None

# Main Streamlit app
def main():
    st.title("PDF and Media Processing Tool")

    # File uploader
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "png", "jpg", "jpeg", "mp4", "avi"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.write(f"Uploaded file: {file_name}")

        # PDF Processing
        if file_name.endswith(".pdf"):
            st.write("Processing PDF...")
            text = extract_pdf_text(uploaded_file)
            if text:
                st.text_area("Extracted Text", text)

            # Convert PDF to images
            if st.button("Convert PDF to Images"):
                images = convert_pdf_to_images(uploaded_file)
                if images:
                    for i, img in enumerate(images):
                        st.image(img, caption=f"Page {i + 1}", use_column_width=True)

        # Image Processing
        elif file_name.endswith((".png", ".jpg", ".jpeg")):
            st.write("Processing Image...")
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", use_column_width=True)

            # Perform OCR
            if st.button("Extract Text from Image"):
                extracted_text = ocr_image(img)
                if extracted_text:
                    st.text_area("Extracted Text", extracted_text)

            # Generate QR Code
            if st.button("Generate QR Code"):
                qr_img = generate_qrcode(extracted_text)
                if qr_img:
                    st.image(qr_img, caption="Generated QR Code", use_column_width=True)

        # Video Processing
        elif file_name.endswith((".mp4", ".avi")):
            st.write("Processing Video...")
            temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            with open(temp_video_path.name, "wb") as f:
                f.write(uploaded_file.read())

            # Resize Video
            if st.button("Resize Video"):
                resized_video_path = resize_video(temp_video_path.name)
                if resized_video_path:
                    st.video(resized_video_path)

        # Text-to-Speech (For text content or extracted text from PDF/Image)
        if st.button("Convert Text to Speech"):
            text = st.text_area("Enter text or extracted text", "")
            if text:
                audio_file = text_to_speech(text)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")

        # Save and Download PDF with QR Code
        if st.button("Save PDF with QR Code"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Add content to PDF
            pdf.cell(200, 10, txt="Generated PDF with QR Code", ln=True)
            pdf.ln(10)  # Line break
            pdf.multi_cell(0, 10, txt="This is a sample PDF with QR Code generated.")

            # Add QR code to the PDF
            qr_img = generate_qrcode("Sample QR Code")
            qr_img.save("qr_code.png")
            pdf.image("qr_code.png", x=10, y=50, w=30)

            # Save the PDF
            output_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(output_pdf_path.name)
            st.download_button("Download Generated PDF", data=open(output_pdf_path.name, "rb"), file_name="generated.pdf")

if __name__ == "__main__":
    main()
