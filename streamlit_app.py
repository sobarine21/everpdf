import streamlit as st
import PyPDF2
from fpdf import FPDF
import pytesseract
from PIL import Image
import os
import cv2
import io
from gtts import gTTS
import base64
import tempfile
import qrcode
from pdf2docx import Converter
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas

# Helper functions for new features
def merge_pdfs(pdf_list):
    merger = PyPDF2.PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(output.name)
    return output.name

def split_pdf(pdf_file, start_page, end_page):
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for i in range(start_page-1, end_page):
            writer.add_page(reader.pages[i])
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output.name, "wb") as out_file:
            writer.write(out_file)
    return output.name

def extract_images_from_pdf(pdf_file):
    images = []
    pdf_document = fitz.open(pdf_file)
    for i in range(len(pdf_document)):
        page = pdf_document.load_page(i)
        img_list = page.get_images(full=True)
        for img in img_list:
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            image.save(img_path.name)
            images.append(img_path.name)
    return images

def add_password_to_pdf(pdf_file, password):
    pdf_writer = PyPDF2.PdfWriter()
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            pdf_writer.add_page(reader.pages[page])
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output.name, "wb") as out_file:
            pdf_writer.write(out_file)
        output.close()
        output = PyPDF2.PdfWriter()
        output.append(file)
        output.encrypt(password)
        return output

def rotate_pdf(pdf_file, rotation_angle=90):
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            page.rotate_clockwise(rotation_angle)
            writer.add_page(page)
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output.name, "wb") as out_file:
            writer.write(out_file)
    return output.name

def add_header_footer_to_pdf(pdf_file, header_text, footer_text):
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            # Add header and footer to each page
            pass  # Implement header and footer customization (text, etc.)
        output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        with open(output.name, "wb") as out_file:
            writer.write(out_file)
    return output.name

def pdf_to_html(pdf_file):
    # Convert PDF to HTML - Basic
    pass  # Implement conversion to HTML if necessary

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    audio_file = tempfile.NamedTemporaryFile(delete=False)
    tts.save(audio_file.name)
    return audio_file.name

def text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, text)
    pdf_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_output.name)
    return pdf_output.name

def image_to_text(image_file):
    img = cv2.imread(image_file)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray_image)
    return text

def generate_qr_code(text):
    qr = qrcode.make(text)
    qr_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    qr.save(qr_path.name)
    return qr_path.name

# Streamlit UI setup
st.title("Advanced PDF Tool with Additional Features")
st.sidebar.title("Navigation")
option = st.sidebar.radio("Choose an Action", [
    "Upload PDF", "Upload Image", "Text to PDF", "Text to Speech",
    "Merge PDFs", "Split PDF", "Extract Images", "PDF to Word", 
    "PDF to HTML", "Generate QR Code"
])

# Main functionality
if option == "Upload PDF":
    uploaded_pdf = st.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_pdf:
        with open("uploaded_file.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        st.write("File Uploaded Successfully!")

elif option == "Text to PDF":
    text_input = st.text_area("Enter Text for PDF", height=200)
    if text_input:
        pdf_file = text_to_pdf(text_input)
        st.write("Download the PDF")
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()
            b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="output.pdf">Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

elif option == "Merge PDFs":
    uploaded_pdfs = st.file_uploader("Upload PDFs to Merge", type="pdf", accept_multiple_files=True)
    if uploaded_pdfs:
        pdf_list = [file for file in uploaded_pdfs]
        merged_pdf = merge_pdfs(pdf_list)
        st.write("Download Merged PDF")
        with open(merged_pdf, "rb") as f:
            pdf_data = f.read()
            b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="merged_output.pdf">Download Merged PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

elif option == "Split PDF":
    uploaded_pdf = st.file_uploader("Choose a PDF to Split", type="pdf")
    start_page = st.number_input("Start Page", min_value=1)
    end_page = st.number_input("End Page", min_value=start_page)
    if uploaded_pdf:
        with open("uploaded_file.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        split_pdf_file = split_pdf("uploaded_file.pdf", start_page, end_page)
        st.write("Download Split PDF")
        with open(split_pdf_file, "rb") as f:
            pdf_data = f.read()
            b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
            href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="split_output.pdf">Download Split PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

elif option == "Extract Images":
    uploaded_pdf = st.file_uploader("Upload PDF to Extract Images", type="pdf")
    if uploaded_pdf:
        with open("uploaded_file.pdf", "wb") as f:
            f.write(uploaded_pdf.read())
        images = extract_images_from_pdf("uploaded_file.pdf")
        for img in images:
            st.image(img)

elif option == "Generate QR Code":
    text_input = st.text_area("Enter Text for QR Code", height=100)
    if text_input:
        qr_code_path = generate_qr_code(text_input)
        st.image(qr_code_path)

elif option == "Text to Speech":
    text_input = st.text_area("Enter Text for Speech", height=200)
    if text_input:
        audio_file = text_to_speech(text_input)
        st.audio(audio_file)

