import streamlit as st 
def main():
    
    st.header('', divider='blue')

    width = 120
    logo = st.image('LOGO.png', width=width)

    with open('style.css') as f: 
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    title = st.title("Welcome to PDF Finder")
    doc_gif = st.image('FileArrowDown.svg')
    
    st.write('Choose what you want to do with your future PDF')

    st.markdown("<a class='link' href='Filter_by_page_number' target='_self'>Filter by page number</a>", unsafe_allow_html=True)
    st.markdown("<a class='link' href='Filter_by_keyword' target='_self'>Filter by keyword</a>", unsafe_allow_html=True)
    st.markdown("<a class='link' href='Apply_OCR_only' target='_self'>Apply OCR only</a>", unsafe_allow_html=True)
    st.markdown("<a class='link' href='Merge_PDFS' target='_self'>Merge PDF's</a>", unsafe_allow_html=True)
    
    
    st.write("<p class='copyright'>©Igor Lins</p>", unsafe_allow_html= True)
if __name__ == "__main__":
    initial_sidebar_state="collapsed"
    main()
