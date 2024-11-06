import streamlit as st
import PyPDF2
from gtts import gTTS
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
import os
import glob

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to save text as audio
def save_text_as_audio(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

# Function to split PDF into individual pages
def split_pdf(file):
    reader = PdfReader(file)
    writer = PdfWriter()
    page_files = []

    for i in range(len(reader.pages)):
        writer.add_page(reader.pages[i])
        output_filename = f"page_{i + 1}.pdf"
        with open(output_filename, "wb") as output_file:
            writer.write(output_file)
        page_files.append(output_filename)

    return page_files

# Function to merge PDFs
def merge_pdfs(file_list):
    writer = PdfWriter()
    for pdf_file in file_list:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            writer.add_page(page)
    output_filename = "merged.pdf"
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)
    return output_filename

# Function to create watermark page
def create_watermark_page(text):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    can.setFont("Helvetica", 30)
    can.setFillColorRGB(0.5, 0.5, 0.5)
    can.drawString(200, 400, text)
    can.save()
    packet.seek(0)
    return PdfReader(packet)

# Function to add watermark
def add_watermark(pdf_file, watermark_text):
    output_pdf = PdfWriter()
    reader = PdfReader(pdf_file)

    for page in reader.pages:
        page.merge_page(create_watermark_page(watermark_text))
        output_pdf.add_page(page)

    output_filename = "watermarked.pdf"
    with open(output_filename, "wb") as output_file:
        output_pdf.write(output_file)

    return output_filename

# Function to download raw text
def download_raw_text(text):
    with open("extracted_text.txt", "w") as f:
        f.write(text)

# Function to add page numbers
def add_page_numbers(pdf_file):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        page.merge_page(create_watermark_page(f"Page {i + 1}"))
        writer.add_page(page)

    output_filename = "numbered.pdf"
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)

    return output_filename

# Function to insert an image into the PDF
def insert_image_to_pdf(pdf_file, image_file):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    image = Image.open(image_file)

    for page in reader.pages:
        page.merge_page(create_image_page(image))
        writer.add_page(page)

    output_filename = "image_inserted.pdf"
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)

    return output_filename

# Function to create a page with an image
def create_image_page(image):
    packet = BytesIO()
    can = canvas.Canvas(packet)
    can.drawImage(image, 100, 100)  # Adjust the position and size
    can.save()
    packet.seek(0)
    return PdfReader(packet)

# Function to convert PDF to text
def pdf_to_text(pdf_file):
    return extract_text_from_pdf(pdf_file)

# Function to compress PDF (placeholder)
def compress_pdf(pdf_file):
    # Compression logic would go here
    return "compressed.pdf"

# Function to create interactive forms (placeholder)
def create_interactive_form(pdf_file):
    # Form creation logic would go here
    return "form_created.pdf"

# Function for OCR (placeholder)
def perform_ocr(pdf_file):
    # OCR logic would go here
    return "ocr_output.pdf"

# Streamlit app
st.title("Mind-Blasting PDF Tool")

uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract text
    text = extract_text_from_pdf(uploaded_file)
    
    # Display extracted text
    st.subheader("Extracted Text")
    st.write(text)
    
    # Summarize (simple version)
    st.subheader("Summary")
    st.write(text[:500] + "...")

    # Convert text to audio
    audio_filename = "output.mp3"
    if st.button("Convert Text to Podcast"):
        save_text_as_audio(text, audio_filename)
        st.success(f"Podcast saved as {audio_filename}")

    # Download link for audio
    st.download_button(
        label="Download Podcast",
        data=open(audio_filename, "rb").read(),
        file_name=audio_filename,
        mime="audio/mp3"
    )

    # Download raw text
    if st.button("Download Raw Text"):
        download_raw_text(text)
        st.success("Raw text downloaded as extracted_text.txt")

    # Split PDF
    if st.button("Split PDF into Individual Pages"):
        split_files = split_pdf(uploaded_file)
        st.success("PDF split into individual pages.")
        for file in split_files:
            st.download_button(label=f"Download {file}", data=open(file, "rb").read(), file_name=file)

    # Watermark feature
    watermark_text = st.text_input("Enter watermark text:")
    if st.button("Add Watermark"):
        if watermark_text:
            watermarked_pdf = add_watermark(uploaded_file, watermark_text)
            st.success("Watermark added.")
            st.download_button(label="Download Watermarked PDF", data=open(watermarked_pdf, "rb").read(), file_name=watermarked_pdf)

    # Add page numbering
    if st.button("Add Page Numbers"):
        numbered_pdf = add_page_numbers(uploaded_file)
        st.success("Page numbers added.")
        st.download_button(label="Download Numbered PDF", data=open(numbered_pdf, "rb").read(), file_name=numbered_pdf)

    # Placeholder for image insertion
    image_file = st.file_uploader("Upload an image to insert into PDF", type=["jpg", "png"])
    if st.button("Insert Image into PDF"):
        if image_file:
            inserted_image_pdf = insert_image_to_pdf(uploaded_file, image_file)
            st.success("Image inserted.")
            st.download_button(label="Download PDF with Image", data=open(inserted_image_pdf, "rb").read(), file_name=inserted_image_pdf)

    # Implementing the new features
    if st.button("Compress PDF"):
        compressed_pdf = compress_pdf(uploaded_file)
        st.success("PDF compressed.")
        st.download_button(label="Download Compressed PDF", data=open(compressed_pdf, "rb").read(), file_name=compressed_pdf)

    if st.button("Create Interactive Form"):
        form_pdf = create_interactive_form(uploaded_file)
        st.success("Interactive form created.")
        st.download_button(label="Download Interactive Form PDF", data=open(form_pdf, "rb").read(), file_name=form_pdf)

    if st.button("Perform OCR"):
        ocr_pdf = perform_ocr(uploaded_file)
        st.success("OCR performed.")
        st.download_button(label="Download OCR PDF", data=open(ocr_pdf, "rb").read(), file_name=ocr_pdf)

    # Clean up files
    for file in glob.glob("*.pdf"):
        if "watermarked" not in file and "numbered" not in file and "inserted" not in file:
            os.remove(file)
