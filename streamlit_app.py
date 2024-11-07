import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from fpdf import FPDF
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from gtts import gTTS
import pytesseract
import qrcode
import tempfile
import io
import os
import requests
import camelot

# Set up the Streamlit application with a title and description
st.title("PDF Utility Tool: A Comprehensive Application")
st.write("Upload a PDF to perform various actions such as text extraction, image conversion, merging, splitting, and more.")

# File uploader to allow PDF input
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_pdf_path = temp_file.name

    # Function to reload the PDF for each action
    def reload_pdf():
        return PdfReader(temp_pdf_path)

    # Sidebar with tool options
    st.sidebar.title("PDF Tools")

    # 1. Extract and display text from the PDF
    if st.sidebar.checkbox("Extract PDF Text"):
        pdf = reload_pdf()
        extracted_text = ""
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""
        st.text_area("Extracted Text", extracted_text, height=300)

    # 2. Show PDF Metadata
    if st.sidebar.checkbox("Show PDF Metadata"):
        pdf = reload_pdf()
        metadata = pdf.metadata
        st.write("PDF Metadata:")
        for key, value in metadata.items():
            st.write(f"{key}: {value}")

    # 3. Display total number of pages
    if st.sidebar.checkbox("Display PDF Page Count"):
        pdf = reload_pdf()
        st.write(f"Total Pages: {len(pdf.pages)}")

    # 4. Extract images from each PDF page and display them
    if st.sidebar.checkbox("Extract Images from PDF"):
        images = convert_from_path(temp_pdf_path)
        st.write(f"Extracted {len(images)} images from PDF:")
        for i, img in enumerate(images):
            # Convert image to bytes for display or download
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="PNG")
            st.image(img_buffer, caption=f"Page {i+1}")

    # 5. Merge PDFs
    if st.sidebar.checkbox("Merge PDFs"):
        additional_files = st.file_uploader("Upload additional PDFs to merge", type="pdf", accept_multiple_files=True)
        if st.button("Merge PDFs"):
            writer = PdfWriter()
            pdf_files = [temp_pdf_path] + [temp_file.name for temp_file in additional_files]
            for pdf_file in pdf_files:
                pdf = PdfReader(pdf_file)
                for page in pdf.pages:
                    writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as merged_pdf:
                writer.write(merged_pdf)
                st.download_button("Download Merged PDF", merged_pdf.name)

    # 6. Split PDF by selecting start and end pages
    if st.sidebar.checkbox("Split PDF"):
        start_page = st.number_input("Start Page", min_value=1, max_value=len(reload_pdf().pages), value=1)
        end_page = st.number_input("End Page", min_value=start_page, max_value=len(reload_pdf().pages), value=len(reload_pdf().pages))
        if st.button("Split PDF"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page_num in range(start_page - 1, end_page):
                writer.add_page(pdf.pages[page_num])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as split_pdf:
                writer.write(split_pdf)
                st.download_button("Download Split PDF", split_pdf.name)

    # 7. Convert PDF to Audio
    if st.sidebar.checkbox("Convert PDF to Audio"):
        pdf = reload_pdf()
        text = "".join(page.extract_text() for page in pdf.pages)
        tts = gTTS(text)
        audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(audio_file.name)
        st.audio(audio_file.name, format="audio/mp3")

    # 8. Convert PDF Pages to Images
    if st.sidebar.checkbox("Convert PDF to Images"):
        images = convert_from_path(temp_pdf_path)
        with tempfile.TemporaryDirectory() as tmp_dir:
            image_paths = []
            for i, img in enumerate(images):
                img_path = os.path.join(tmp_dir, f"page_{i + 1}.png")
                img.save(img_path)
                image_paths.append(img_path)
                st.image(img, caption=f"Page {i+1}")
            # Provide ZIP download option
            st.write("Download all images as ZIP not implemented yet.")

    # 9. Add a Watermark to the PDF
    if st.sidebar.checkbox("Add Watermark to PDF"):
        watermark_text = st.text_input("Enter Watermark Text")
        if watermark_text and st.button("Apply Watermark"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in pdf.pages:
                writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as watermarked_pdf:
                c = canvas.Canvas(watermarked_pdf.name)
                c.setFont("Helvetica", 36)
                c.drawString(100, 500, watermark_text)
                c.save()
                st.download_button("Download Watermarked PDF", watermarked_pdf.name)

    # 10. Generate QR Code for any text or URL
    if st.sidebar.checkbox("Generate QR Code"):
        qr_text = st.text_input("Enter text for QR Code")
        if st.button("Generate QR Code"):
            qr_img = qrcode.make(qr_text)
            # Convert QR image to bytes for display
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            st.image(qr_buffer, caption="Generated QR Code")

    # 11. Perform OCR on Images within the PDF
    if st.sidebar.checkbox("Perform OCR on PDF Images"):
        images = convert_from_path(temp_pdf_path)
        extracted_text = ""
        for img in images:
            extracted_text += pytesseract.image_to_string(img)
        st.text_area("Extracted OCR Text", extracted_text)

    # 12. Convert PDF Tables to CSV using Camelot
    if st.sidebar.checkbox("Convert PDF Tables to CSV"):
        try:
            # Read tables from the PDF using Camelot
            tables = camelot.read_pdf(temp_pdf_path, pages='all', flavor='stream')

            # For each table, convert it to CSV and provide a download button
            for i, table in enumerate(tables):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as csv_file:
                    table.to_csv(csv_file.name, index=False)
                    st.download_button(f"Download Table {i+1} as CSV", csv_file.name)

        except Exception as e:
            st.error(f"Error converting PDF to CSV: {str(e)}")

    # 13. Generate PDF from Input Text
    if st.sidebar.checkbox("Generate PDF from Text"):
        text_input = st.text_area("Enter text to generate PDF")
        if st.button("Generate PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text_input)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as generated_pdf:
                pdf.output(generated_pdf.name)
                st.download_button("Download Generated PDF", generated_pdf.name)

    # 14. Rotate PDF Pages
    if st.sidebar.checkbox("Rotate PDF Pages"):
        rotation_angle = st.selectbox("Select Rotation Angle", [90, 180, 270])
        if st.button("Rotate PDF"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in pdf.pages:
                page.rotate(rotation_angle)
                writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as rotated_pdf:
                writer.write(rotated_pdf)
                st.download_button("Download Rotated PDF", rotated_pdf.name)

    # 15. Encrypt PDF with a Password
    if st.sidebar.checkbox("Encrypt PDF"):
        password = st.text_input("Enter password", type="password")
        if password and st.button("Encrypt PDF"):
            pdf = reload_pdf()
            writer = PdfWriter()
            for page in pdf.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as encrypted_pdf:
                writer.write(encrypted_pdf)
                st.download_button("Download Encrypted PDF", encrypted_pdf.name)

    # 16. Decrypt Password-Protected PDF
    if st.sidebar.checkbox("Decrypt PDF"):
        password = st.text_input("Enter password for decryption", type="password")
        if password and st.button("Decrypt PDF"):
            pdf = reload_pdf()
            pdf.decrypt(password)
            writer = PdfWriter()
            for page in pdf.pages:
                writer.add_page(page)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as decrypted_pdf:
                writer.write(decrypted_pdf)
                st.download_button("Download Decrypted PDF", decrypted_pdf.name) 
