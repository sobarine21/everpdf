import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from gtts import gTTS
from PIL import Image
import pytesseract
import qrcode
import moviepy.editor as mp
import tempfile
import os
import requests
import base64

# 1. Title of the Web Application
st.title("Comprehensive PDF Utility Tool")

# 2. File Uploader for PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name

    # 3. Reload PDF for processing after any modification
    def reload_pdf():
        return PdfReader(temp_pdf_path)

    # 4. Sidebar for selecting various functionalities
    st.sidebar.title("Select Functionality")

    # 5. Show PDF Text
    if st.sidebar.checkbox("Show PDF Text"):
        pdf = reload_pdf()
        text_output = ""
        for page in pdf.pages:
            text_output += page.extract_text() + "\n"
        st.text_area("PDF Text Content", text_output, height=300)

    # 6. Show PDF Metadata
    if st.sidebar.checkbox("Show PDF Metadata"):
        pdf = reload_pdf()
        metadata = pdf.metadata
        st.write(metadata)

    # 7. PDF Page Count
    if st.sidebar.checkbox("Show PDF Page Count"):
        pdf = reload_pdf()
        st.write(f"Number of pages: {len(pdf.pages)}")

    # 8. Extract Images from PDF Pages
    if st.sidebar.checkbox("Extract Images from PDF"):
        images = convert_from_path(temp_pdf_path)
        st.write(f"Extracted {len(images)} images")
        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1}")

    # 9. Merge PDFs
    if st.sidebar.checkbox("Merge PDFs"):
        uploaded_files = st.file_uploader("Upload additional PDFs to merge", type="pdf", accept_multiple_files=True)
        if st.button("Merge PDFs"):
            writer = PdfWriter()
            pdf_files = [temp_pdf_path] + [file.name for file in uploaded_files]
            for pdf_file in pdf_files:
                pdf = PdfReader(pdf_file)
                for page in pdf.pages:
                    writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_file:
                writer.write(output_file)
                st.success("PDFs merged successfully!")
                st.download_button("Download Merged PDF", output_file.name)

    # 10. Split PDF by Pages
    if st.sidebar.checkbox("Split PDF by Pages"):
        start_page = st.number_input("Start Page", min_value=1, max_value=len(reload_pdf().pages), value=1)
        end_page = st.number_input("End Page", min_value=1, max_value=len(reload_pdf().pages), value=len(reload_pdf().pages))
        if st.button("Split PDF"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in range(start_page - 1, end_page):
                writer.add_page(pdf.pages[page])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_file:
                writer.write(output_file)
                st.success("PDF split successfully!")
                st.download_button("Download Split PDF", output_file.name)

    # 11. Convert PDF to Audio
    if st.sidebar.checkbox("Convert PDF to Audio"):
        pdf = reload_pdf()
        text_output = "".join([page.extract_text() for page in pdf.pages])
        tts = gTTS(text_output)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        st.audio(audio_file.name, format="audio/mp3")

    # 12. Convert PDF to Images
    if st.sidebar.checkbox("Convert PDF to Images"):
        images = convert_from_path(temp_pdf_path)
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_paths = []
            for i, img in enumerate(images):
                img_path = os.path.join(tmp_dir, f"page_{i + 1}.png")
                img.save(img_path)
                image_paths.append(img_path)
                st.image(img, caption=f"Page {i+1}")
            st.write("Download images as ZIP:")
            st.download_button("Download Images as ZIP", tmp_dir, mime="application/zip")

    # 13. Add Watermark to PDF
    if st.sidebar.checkbox("Add Watermark to PDF"):
        watermark_text = st.text_input("Enter Watermark Text")
        if watermark_text and st.button("Apply Watermark"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page_num, page in enumerate(pdf.pages):
                writer.add_page(page)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_pdf:
                    c = canvas.Canvas(output_pdf.name)
                    c.setFont("Helvetica", 36)
                    c.drawString(100, 500, watermark_text)
                    c.save()
                    st.success("Watermark added to PDF.")
                    st.download_button("Download Watermarked PDF", output_pdf.name)

    # 14. Generate QR Code for a PDF or URL
    if st.sidebar.checkbox("Generate QR Code"):
        qr_text = st.text_input("Enter text for QR Code")
        if st.button("Generate QR Code"):
            qr = qrcode.make(qr_text)
            st.image(qr, caption="Generated QR Code")

    # 15. Perform OCR on PDF Images
    if st.sidebar.checkbox("Perform OCR on PDF Images"):
        images = convert_from_path(temp_pdf_path)
        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img)
        st.text_area("Extracted Text from Images", ocr_text, height=300)

    # 16. Generate PDF from Text
    if st.sidebar.checkbox("Generate PDF from Text"):
        input_text = st.text_area("Enter text to generate PDF", height=200)
        if st.button("Generate PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, input_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_pdf:
                pdf.output(output_pdf.name)
                st.download_button("Download Generated PDF", output_pdf.name)

    # 17. Rotate PDF Pages
    if st.sidebar.checkbox("Rotate PDF Pages"):
        rotation_angle = st.number_input("Enter rotation angle (90, 180, 270)", value=90, step=90)
        if st.button("Rotate"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in pdf.pages:
                page.rotateClockwise(rotation_angle)
                writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_pdf:
                writer.write(output_pdf)
                st.download_button("Download Rotated PDF", output_pdf.name)

    # 18. Resize Images in PDF
    if st.sidebar.checkbox("Resize Images in PDF"):
        new_width = st.number_input("Enter new width for images", min_value=100, max_value=2000, value=600)
        if st.button("Resize Images"):
            images = convert_from_path(temp_pdf_path)
            resized_images = []
            for img in images:
                resized_img = img.resize((new_width, int(img.height * new_width / img.width)))
                resized_images.append(resized_img)
                st.image(resized_img)
            with tempfile.TemporaryDirectory() as tmp_dir:
                resized_image_paths = []
                for i, resized_img in enumerate(resized_images):
                    img_path = os.path.join(tmp_dir, f"page_{i+1}_resized.png")
                    resized_img.save(img_path)
                    resized_image_paths.append(img_path)
                st.download_button("Download Resized Images", tmp_dir, mime="application/zip")

    # 19. Encrypt PDF with Password
    if st.sidebar.checkbox("Encrypt PDF with Password"):
        password = st.text_input("Enter a password")
        if st.button("Encrypt"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in pdf.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_pdf:
                writer.write(output_pdf)
                st.success("PDF encrypted successfully!")
                st.download_button("Download Encrypted PDF", output_pdf.name)

    # 20. Decrypt PDF
    if st.sidebar.checkbox("Decrypt PDF"):
        password = st.text_input("Enter the password")
        if st.button("Decrypt"):
            pdf = reload_pdf()
            pdf.decrypt(password)
            decrypted_pdf_writer = PdfWriter()
            for page in pdf.pages:
                decrypted_pdf_writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_pdf:
                decrypted_pdf_writer.write(output_pdf)
                st.success("PDF decrypted successfully!")
                st.download_button("Download Decrypted PDF", output_pdf.name)

    # ... Add more features up to 50 functionalities (such as adding metadata, converting formats, etc.)
