import netlify.streamlit as st
from PyPDF2 import PdfWriter, PdfReader
import tempfile
import os
import zipfile
import pdfplumber

def apply_ocr_only():
    def check_ocr_necessity(pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            first_page_text = pdf.pages[0].extract_text()
            if not first_page_text.strip():
                return True
            else:
                return False

    def apply_ocr_and_return_path(pdf_path):
        temp_dir = tempfile.mkdtemp()
        temp_output_pdf = os.path.join(temp_dir, 'document_with_ocr.pdf')

        os.system(f'ocrmypdf --force-ocr "{pdf_path}" "{temp_output_pdf}"')

        return temp_output_pdf

    header = st.header('', divider='blue')

    size = 150
    logo = st.image('LOGO.png', width=size)

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    title = st.title("You chose to apply OCR only!")
    doc_gif = st.image('FileArrowDown.svg')

    st.write('<p class="sua-classe">OCR is an acronym for Optical Character Recognition, it is a technology to recognize characters from an image file or bitmap whether they are scanned, handwritten, typed, or printed. Thus, through OCR it is possible to obtain a text file editable by a computer.', unsafe_allow_html=True)
    pdf_files = st.file_uploader("Upload the PDF file", type=["pdf"], accept_multiple_files=True)

    if pdf_files:
        if len(pdf_files) == 1:
            if st.button("Extract Pages"):
                progress_bar = st.progress(0)
                waiting_message = st.text("Extracting pages... This may take a while, please wait.")
                if pdf_files is not None and len(pdf_files) > 0:
                    total_pages = len(pdf_files)
                    current_progress = 0
                    with tempfile.TemporaryDirectory() as temp_dir:
                        individual_files = []
                        for i, pdf_file in enumerate(pdf_files):
                            temp_pdf_path = os.path.join(temp_dir, f'NewDocument_pdf_{i}.pdf')
                            with open(temp_pdf_path, 'wb') as temp_pdf_file:
                                temp_pdf_file.write(pdf_file.getbuffer())

                            if check_ocr_necessity(temp_pdf_path):
                                temp_pdf_path = apply_ocr_and_return_path(temp_pdf_path)
                                individual_files.append(temp_pdf_path)

                            current_progress += 1
                            progress_bar.progress(current_progress / total_pages)

                        file_pdf = PdfWriter()
                        for individual_file in individual_files:
                            file_pdf.append(individual_file)
                        file_name = f"Document.pdf"
                        file_path = os.path.join(temp_dir, file_name)
                        with open(file_path, 'wb') as file_file:
                            file_pdf.write(file_file)
                        st.success(f"The page was successfully saved to {file_name}.")
                        posi = st.image('CheckCircle.svg')
                        st.download_button(
                            label='Download item',
                            data=open(file_path, 'rb').read(),
                            file_name=file_name,
                            key='one.pdf'
                        )
        else:
            file_names = [pdf_file.name for pdf_file in pdf_files]
            reordered_files = st.multiselect("Reorder the PDFs if desired. (The download button will only be available when all files are here)", options=file_names, default=file_names, format_func=lambda x: x)
            option = st.selectbox("Choose a saving option:", ("Merge PDFs", "Export Individually"))
            if reordered_files is not None and len(reordered_files) == len(pdf_files):
             if st.button("Extract Pages"):
                progress_bar = st.progress(0)
                waiting_message = st.text("Extracting pages... This may take a while, please wait.")
                if pdf_files is not None and len(pdf_files) > 0:
                    total_pages = len(pdf_files)
                    current_progress = 0
                    with tempfile.TemporaryDirectory() as temp_dir:
                        sorted_pdf_files = [pdf_files[file_names.index(name)] for name in reordered_files]
                        individual_files = []
                        for i, pdf_file in enumerate(sorted_pdf_files):
                            temp_pdf_path = os.path.join(temp_dir, f'NewDocument_pdf_{i}.pdf')
                            with open(temp_pdf_path, 'wb') as temp_pdf_file:
                                temp_pdf_file.write(pdf_file.getbuffer())

                            if check_ocr_necessity(temp_pdf_path):
                                temp_pdf_path = apply_ocr_and_return_path(temp_pdf_path)
                                individual_files.append(temp_pdf_path)

                            current_progress += 1
                            progress_bar.progress(current_progress / total_pages)

                        if option == "Merge PDFs":
                            merged_pdf = PdfWriter()
                            for individual_file in individual_files:
                                merged_pdf.append(individual_file)
                            merged_file_name = f"Merged_Documents.pdf"
                            merged_file_path = os.path.join(temp_dir, merged_file_name)
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

                        elif option == "Export Individually":
                            rar_file_name = f"Individual_Documents.zip"
                            rar_file_path = os.path.join(temp_dir, rar_file_name)
                            with zipfile.ZipFile(rar_file_path, 'w') as zip_file:
                                for individual_file in individual_files:
                                    zip_file.write(individual_file, os.path.basename(individual_file))
                            st.success(f"The pages were extracted and grouped in {rar_file_name}.")
                            posi = st.image('CheckCircle.svg')
                            st.download_button(
                                label='Download individual compressed items',
                                data=open(rar_file_path, 'rb').read(),
                                file_name=rar_file_name,
                                key='individuals.zip'
                            )
                        else:
                            st.warning("Invalid option.")
                else:
                    st.warning("Please upload a PDF file.")
                    att = st.image('atenttion.gif')
                waiting_message.empty()

    if pdf_files is not None:
        total_pages = 0
        for pdf_file in pdf_files:
            total_pages += len(PdfReader(pdf_file).pages)

        if len(pdf_files) == 1:
            st.write(f"The PDF has {total_pages} pages.")
        elif len(pdf_files) > 1:
            st.write(f"The PDFs have a total of {total_pages} pages.")
        
        return_to_main = st.markdown("<a class='goback' href='Home' target='_self'>Back</a>", unsafe_allow_html=True) 
        st.write("<p class='copyright'>©Igor Lins</p>", unsafe_allow_html= True)

apply_ocr_only()
