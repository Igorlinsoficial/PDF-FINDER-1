import netlify.streamlit as st
from PyPDF2 import PdfWriter, PdfReader
import tempfile
import os
import zipfile


def filter_by_number():

    ########################################################################
    # FUNCTIONS
    ########################################################################

    # Function to extract PDF pages and open it, starting from the first page
    def extract_pdf_pages(original_pdf_path, output_pdf_path, pages):
        # Open the tempfile and the pages (keyword or numbering), already extracting if OCR is not needed
        with open(original_pdf_path, 'rb') as original_file:
            # Open in binary mode
            pdf_reader = PdfReader(original_file)
            pdf_writer = PdfWriter()  # Copy page read by PDFREADER
            total_pages = len(pdf_reader.pages)
            for page_num in pages:
                
                if page_num < 1 or page_num > total_pages:
                    st.error(f"Error! Check if the number entered does not exceed the number of pages of any PDF. If PDF x has 10 pages and you put 11, this error message will occur! The same goes for 2 or more PDFs, if PDF A is equal to 3 pages and B is equal to 2 and you put the filtering number as 3, it will return an error because B only has 2 pages.")
                    return False 
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])
            with open(output_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)
        return True

    header = st.header('', divider='blue')

    size = (150)
    logo = st.image('LOGO.png', width=size)

    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True) 
        
    st.markdown("<h1 class='title'>You've chosen to filter by page number!</h1>", unsafe_allow_html=True)
    doc_gif = st.image('FileArrowDown.svg')

    st.write('<p class="sua-classe">The functionality of this option is based on filtering by page numbering. Example: If the number entered is 1, the exported page will be only page 1.', unsafe_allow_html=True)
    pdf_files = st.file_uploader("Upload PDF file(s)", type=["pdf"], accept_multiple_files=True)

    if pdf_files:
        
        if len(pdf_files) == 1:
            pages_to_extract = st.text_input("Enter the page(s) to extract. If more than one, separate by comma. (To update information, just click anywhere on the page)", "1,2,3")
            try:
                pages_to_extract = [int(p) for p in pages_to_extract.split(",")]
            except ValueError:
                st.error("Please provide integer numbers for the pages.")
                
            if not pages_to_extract or any(not isinstance(p, int) for p in pages_to_extract):
                st.warning("Please inform the pages to extract.")
                return
            if st.button("Extract Pages"): 
                
                progress_bar = st.progress(0)
                waiting_message = st.text("Extracting pages... This might take a while, please wait.")
                if pdf_files is not None and len(pdf_files) > 0:
                    total_pages = len(pdf_files) * len(pages_to_extract) if pages_to_extract else len(pdf_files)
                    current_progress = 0
                    with tempfile.TemporaryDirectory() as temp_dir:
                        for pdf_file in pdf_files:
                            # Process each PDF file individually
                            temp_pdf_path = os.path.join(temp_dir, f'{pdf_file.name}_pages.pdf')
                            with open(temp_pdf_path, 'wb') as temp_pdf_file:
                                temp_pdf_file.write(pdf_file.getbuffer())

                            # Extract the selected pages
                            if pages_to_extract:
                                success = extract_pdf_pages(temp_pdf_path, temp_pdf_path, pages_to_extract)
                                if not success:
                                    return
                            
                            current_progress += len(pages_to_extract) if pages_to_extract else 1
                            progress_bar.progress(current_progress / total_pages)
                            
                            # Save the PDF file with the extracted pages
                            file_name = f"{pdf_file.name}_pages.pdf"
                            file_path = os.path.join(temp_dir, file_name)
                            st.success(f"The pages have been extracted and saved to {file_name}.")
                            st.download_button(
                                label=f'Download {pdf_file.name}_pages.pdf',
                                data=open(file_path, 'rb').read(),
                                file_name=file_name,
                                key=f'{pdf_file.name}_pages.pdf'
                            )
            
        else:   

            file_names = [pdf_file.name for pdf_file in pdf_files]
            reordered_files = st.multiselect("Reorder PDFs if desired. (Download button will only be available when all files are here)", options=file_names, default=file_names, format_func=lambda x: x)
            pages_to_extract = st.text_input("Enter the pages to extract (To update information, just click anywhere on the page)", "1,2,3")
            try:
                pages_to_extract = [int(p) for p in pages_to_extract.split(",")]
            except ValueError:
                st.error("Please provide integer numbers for the pages.")
            option = st.selectbox("Choose a saving option:", ("Merge PDFs", "Export Individually"))

            # Check if the input field for the pages is empty
            if not pages_to_extract or any(not isinstance(p, int) for p in pages_to_extract):
                st.warning("Please inform the pages to extract.")
                return
            
            if reordered_files is not None and len(reordered_files) == len(pdf_files):
                if st.button("Extract Pages"):
                    progress_bar = st.progress(0)
                    waiting_message = st.text("Extracting pages... This might take a while, please wait.")
                    if pdf_files is not None and len(pdf_files) > 0:
                        total_pages = len(pdf_files) * len(pages_to_extract) if pages_to_extract else len(pdf_files)
                        current_progress = 0
                        with tempfile.TemporaryDirectory() as temp_dir:
                            sorted_pdf_files = [pdf_files[file_names.index(name)] for name in reordered_files]
                            if option == "Merge PDFs":
                                merged_pdf = PdfWriter()
                                for i, pdf_file in enumerate(sorted_pdf_files):
                                    temp_pdf_path = os.path.join(temp_dir, f'NewDocument_pdf_{i}.pdf')
                                    with open(temp_pdf_path, 'wb') as temp_pdf_file:
                                        temp_pdf_file.write(pdf_file.getbuffer())
                                    if pages_to_extract:
                                        success = extract_pdf_pages(temp_pdf_path, temp_pdf_path, temp_pdf_path, pages_to_extract)
                                        if not success:
                                            return
                                    current_progress += len(pages_to_extract) if pages_to_extract else 1
                                    progress_bar.progress(current_progress / total_pages)
                                    merged_pdf.append(temp_pdf_path)
                                merged_file_name = f"Merged_Documents.pdf"
                                merged_file_path = os.path.join(temp_dir, merged_file_name)
                                with open(merged_file_path, 'wb') as merged_file:
                                    merged_pdf.write(merged_file)
                                st.success(f"The pages have been merged successfully to {merged_file_name}.")
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
                                individual_files = []
                                with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                                    for i, pdf_file in enumerate(sorted_pdf_files):
                                        temp_pdf_path = os.path.join(temp_dir, f'NewDocument_pdf_{i}.pdf')
                                        with open(temp_pdf_path, 'wb') as temp_pdf_file:
                                            temp_pdf_file.write(pdf_file.getbuffer())
                                        if pages_to_extract:
                                            success = extract_pdf_pages(temp_pdf_path, temp_pdf_path, pages_to_extract)
                                            if not success:
                                                return
                                        current_progress += len(pages_to_extract) if pages_to_extract else 1
                                        progress_bar.progress(current_progress / total_pages)
                                        individual_files.append(temp_pdf_path)
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
                    else:
                        st.warning("Please upload a PDF file.")
                        att = st.image('attention.gif')
                    waiting_message.empty()

    if pdf_files is not None:
        total_pages = 0
        for pdf_file in pdf_files:
            total_pages += len(PdfReader(pdf_file).pages)

        if len(pdf_files) == 1:
            st.write(f"The PDF has {total_pages} page(s).")
        elif len(pdf_files) > 1:
            st.write(f"The PDFs together have {total_pages} pages in total.")
            
    
    return_button = st.markdown("<a class='goback' href='Home' target='_self'>Return</a>", unsafe_allow_html=True)
    st.write("<p class='copyright'>©Igor Lins</p>", unsafe_allow_html= True)            

filter_by_number()

