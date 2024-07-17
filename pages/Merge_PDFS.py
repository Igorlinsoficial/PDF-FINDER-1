import streamlit as st
from PyPDF2 import PdfWriter
import os

def merge_pdfs():
    st.header('', divider='blue')
    size = 150
    logo = st.image('LOGO.png', width=size)

    with open('style.css') as f: 
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    title = st.title("You chose to Merge PDFs")

    pdf_files = st.file_uploader("Upload the PDF file", type=["pdf"], accept_multiple_files=True)
    
    if pdf_files:
        file_names = [pdf_file.name for pdf_file in pdf_files]
        reordered_files = st.multiselect("Reorder the PDFs, if desired. (The download button will only be available when all files are here)", options=file_names, default=file_names, format_func=lambda x: x)
        if reordered_files is not None and len(reordered_files) == len(pdf_files):
            if st.button('Extract PDF'):
                progress_bar = st.progress(0)
                waiting_message = st.text("Merging PDFs... Please wait.")
                total_pages = len(pdf_files)
                current_progress = 0
                merged_pdf = PdfWriter()
                for pdf_file_name in reordered_files:
                    for pdf_file in pdf_files:
                        if pdf_file.name == pdf_file_name:
                            merged_pdf.append(pdf_file)
                            break
                merged_file_name = f"Merged_Documents.pdf"
                merged_file_path = os.path.join(merged_file_name)
                with open(merged_file_path, 'wb') as merged_file:
                    merged_pdf.write(merged_file)
                st.success(f"The pages were successfully merged to {merged_file_name}.")
                posi = st.image('CheckCircle.svg')
                st.download_button(
                    label='Download merged items',
                    data=open(merged_file_path, 'rb').read(),
                    file_name=merged_file_name,
                    key='merged.pdf'
                )
                waiting_message.empty()
    return_to_main = st.markdown("<a class='goback' href='Home' target='_self'>Back</a>", unsafe_allow_html=True)
    st.write("<p class='copyright'>©Igor Lins</p>", unsafe_allow_html= True)

merge_pdfs()
