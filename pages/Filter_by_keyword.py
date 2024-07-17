import netlify.streamlit as st
from PyPDF2 import PdfWriter, PdfReader
import tempfile
import os
import zipfile
import pdfplumber
import fitz

def filter_by_keyword():
    def extract_pdf_pages(original_pdf_path, output_pdf_path, pages):
        with open(original_pdf_path, 'rb') as original_file:
            pdf_reader = PdfReader(original_file)
            pdf_writer = PdfWriter()
            for page_num in pages:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])

            with open(output_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
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

    def search_pages_with_keyword(pdf_path, keyword):
        found_pages = []
        pdf_doc = fitz.open(pdf_path)

        for page_num in range(pdf_doc.page_count):
            page = pdf_doc[page_num]
            text = page.get_text("text")
            if any(word.lower() in text.lower() for word in keyword):
                found_pages.append(page_num + 1)

        pdf_doc.close()
        return found_pages

    st.header('', divider='blue')
    size = 150
    logo = st.image('LOGO.png', width=size)
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    title = st.title("You've chosen to filter by keyword!")
    doc_gif = st.image('FileArrowDown.svg')
    st.write('<p class="sua-classe">The functionality of this option is based on one or more keywords. If the word "Python" is placed, it will search for pages that have that word and export them, ignoring the rest.</p>', unsafe_allow_html=True)
    pdf_files = st.file_uploader("Upload PDF file(s)", type=["pdf"], accept_multiple_files=True)

    if pdf_files:
        
        if len(pdf_files) == 1:
            keyword_input = st.text_input("Enter the keyword(s) to be searched. If more than one, separate by comma. (To update information, click anywhere on the page)", 'Example: X,Y,Z')
            keyword = [p.strip() for p in keyword_input.split(",") if p.strip()]

            if not keyword_input:
                st.warning("Please provide what needs to be extracted.")
                return
            if st.button('Extract Page'):
                progress_bar = st.progress(0)
                waiting_message = st.text("Extracting pages... This might take a while, please wait.")
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

                        found_pages = search_pages_with_keyword(temp_pdf_path, keyword)
                        if found_pages:
                            extract_pdf_pages(temp_pdf_path, temp_pdf_path, found_pages)
                            individual_files.append(temp_pdf_path)
                        if not found_pages:
                                    st.error(
                                        f"The keyword(s) '{keyword}' were not found in the PDF {pdf_file.name}. Please check if you've entered the correct data.")
                                    continue

                        current_progress += 1
                        progress_bar.progress(current_progress / total_pages)
                        
                        file_pdf = PdfWriter()
                        for individual_file in individual_files:
                            file_pdf.append(individual_file)
                        file_name = f"Document.pdf"
                        file_path = os.path.join(temp_dir, file_name)
                        with open(file_path, 'wb') as file_file:
                            file_pdf.write(file_file)
                        st.success(f"The page has been successfully saved to {file_name}.")
                        posi = st.image('CheckCircle.svg')
                        st.download_button(
                            label='Download item',
                            data=open(file_path, 'rb').read(),
                            file_name=file_name,
                            key='one.pdf'
                        )
        else:
            file_names = [pdf_file.name for pdf_file in pdf_files]
            reordered_files = st.multiselect("Reorder PDFs, if desired. (Download button will only be available when all files are here)", options=file_names, default=file_names, format_func=lambda x: x)
            keyword_input = st.text_input("Enter the keyword(s) to be searched. If more than one, separate by comma. (To update information, click anywhere on the page)", 'Example: X,Y,Z')
            keyword = [p.strip() for p in keyword_input.split(",") if p.strip()]

            if not keyword_input:
                st.warning("Please provide what needs to be extracted.")
                return
            
            option = st.selectbox("Choose a saving option:", ("Merge PDFs", "Export Individually"))                
            if reordered_files is not None and len(reordered_files) == len(pdf_files):
             if st.button("Extract Pages"):
                progress_bar = st.progress(0)
                waiting_message = st.text("Extracting pages... This might take a while, please wait.")
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

                        found_pages = search_pages_with_keyword(temp_pdf_path, keyword)
                        if found_pages:
                            extract_pdf_pages(temp_pdf_path, temp_pdf_path, found_pages)
                            individual_files.append(temp_pdf_path)
                        if not found_pages:
                                    st.error(
                                        f"The keyword(s) '{keyword}' were not found in the PDF {pdf_file.name}. Please check if you've entered the correct data.")
                                    continue

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
                        st                        .success(f"The pages have been successfully merged to {merged_file_name}.")
                        posi = st.image('CheckCircle.svg')
                        st.download_button(
                            label='Download merged items',
                            data=open(merged_file_path, 'rb').read(),
                            file_name=merged_file_name,
                            key='merged.pdf'
                        )

                    elif option == "Export Individually":
                        zip_file_name = f"Individual_Documents.zip"
                        zip_file_path = os.path.join(temp_dir, zip_file_name)
                        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                            for individual_file in individual_files:
                                zip_file.write(individual_file, os.path.basename(individual_file))
                        st.success(f"The pages have been extracted and grouped into {zip_file_name}.")
                        posi = st.image('CheckCircle.svg')
                        st.download_button(
                            label='Download compressed individual items',
                            data=open(zip_file_path, 'rb').read(),
                            file_name=zip_file_name,
                            key='individuals.zip'
                        )
                    else:
                        st.warning("Invalid option.")
                waiting_message.empty()

    if pdf_files is not None:
        total_pages = 0
        for pdf_file in pdf_files:
            total_pages += len(PdfReader(pdf_file).pages)

        if len(pdf_files) == 1:
            st.write(f"The PDF has {total_pages} page(s).")
        elif len(pdf_files) > 1:
            st.write(f"The PDFs have {total_pages} pages in total.")
    return_button = st.markdown("<a class='goback' href='Home' target='_self'>Back</a>", unsafe_allow_html=True) 
    st.write("<p class='copyright'>©Igor Lins</p>", unsafe_allow_html= True)

filter_by_keyword()

