import streamlit as st
st.set_page_config(
    page_title="Dyslexia Friendly Reader",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="auto"
)

st.markdown(
    "<h1 style='text-align: center; color: #41C9E2;'>Dyslexia Friendly Reader</h1>",
    unsafe_allow_html=True
)

# Welcome Message Box
st.markdown(
    """
    <div style='
        background-color: #DCE6F8;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #A3BFFA;
        margin-top: 20px;
        font-family: Comic Sans MS, cursive;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
    '>
        <p style='text-align: center; color: #1B1F3B; font-size: 18px; margin: 0;'>
            Welcome! This tool is designed to support neurodiverse individuals, especially those with dyslexia or ADHD, 
            by providing a comfortable, distraction-free reading experience 🫶.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
import tempfile
import re
from tqdm import tqdm
from pathlib import Path
import subprocess

# Install beautifulsoup4 and ebooklib packages
subprocess.run(["pip", "install", "beautifulsoup4", "ebooklib"])

from bs4 import BeautifulSoup
import bs4
from ebooklib import epub

def _convert_file_path(path, original_name):
    path_obj = Path(path)
    new_name = f"Bionic_{original_name}"
    new_path = path_obj.with_name(new_name)
    return str(new_path)

def convert_to_bionic_str(soup: BeautifulSoup, s: str):
    new_parent = soup.new_tag("span")
    words = re.split(r'.,;:!?-|\s', s)
    for word in words:
        if len(word) >= 2:
            mid = (len(word) // 2) + 1
            first_half, second_half = word[:mid], word[mid:]
            b_tag = soup.new_tag("b")
            b_tag.append(soup.new_string(first_half))
            new_parent.append(b_tag)
            new_parent.append(soup.new_string(second_half + " "))
        else:
            new_parent.append(soup.new_string(word + " "))
    return new_parent

def convert_to_bionic(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    for e in soup.descendants:
        if isinstance(e, bs4.element.Tag):
            if e.name == "p":
                children = list(e.children)
                for child in children:
                    if isinstance(child, bs4.element.NavigableString):
                        if len(child.text.strip()):
                            child.replace_with(convert_to_bionic_str(soup, child.text))
    return str(soup).encode()

def convert_book(book_path, original_name):
    source = epub.read_epub(book_path)
    total_items = len(list(source.items))
    progress_bar = st.progress(0)
    
    for i, item in enumerate(source.items):
        if item.media_type == "application/xhtml+xml":
            content = item.content.decode('utf-8')
            item.content = convert_to_bionic(content)
        progress_bar.progress((i + 1) / total_items)
    
    converted_path = _convert_file_path(book_path, original_name)
    epub.write_epub(converted_path, source)
    
    with open(converted_path, "rb") as f:
        converted_data = f.read()
    
    return converted_data, Path(converted_path).name

def main():
    st.markdown(
    "<h2 style='text-align: center; font-size: 28px; color: #000000;'>Convert your EPUB to Bionic</h2>",
    unsafe_allow_html=True
)

    st.markdown("<hr style='margin-top: -10px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    # 💭 Cloud-style info box
    st.markdown(
        """
        <div style='
            background-color: #F0F8FF;
            padding: 15px;
            border-radius: 15px;
            border: 2px dashed #A3BFFA;
            margin-top: 5px;
            margin-bottom: 20px;
            font-size: 16px;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.05);
        '>
            ☁️ No worries if you don't have an EPUB version of your PDF.<br>
            You can convert it here 👇
        </div>
        """,
        unsafe_allow_html=True
    )

    # 🌐 Redirect button
    st.markdown(
    """
    <div style="text-align: center;">
        <a href="https://cloudconvert.com/epub-to-pdf" target="_blank">
            <button style="
                background-color: #41C9E2;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 14px;
                cursor: pointer;
                margin-bottom: 15px;
            ">
                Convert
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


    # File Upload and Conversion
    st.markdown(
        "<p style='font-size:18px; font-weight:bold; margin-bottom: 0.5px;'>📁 Upload a EPUB file</p>",
        unsafe_allow_html=True
    )
    book_path = st.file_uploader("Upload a file", type=["epub"])

    if book_path is not None:
        original_name = book_path.name
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(book_path.read())
            tmp_file_path = tmp_file.name

        # Check if the uploaded book is different from the previous one
        if 'original_name' not in st.session_state or st.session_state.original_name != original_name:
            # Clear the session state if the book is different
            st.session_state.clear()

        # Perform the conversion only if the converted data is not already in the session state
        if 'converted_data' not in st.session_state:
            with st.spinner("Processing the file..."):
                st.session_state.converted_data, st.session_state.converted_name = convert_book(tmp_file_path, original_name)
            st.success("Conversion completed!")

        # Display the download button using the converted data from the session state
        converted_data = st.session_state.converted_data
        converted_name = st.session_state.converted_name
        st.download_button(
            label="Download Converted Book",
            data=converted_data,
            file_name=converted_name,
            mime="application/epub+zip"
        )

        # Store the original name of the uploaded book in the session state
        st.session_state.original_name = original_name

if __name__ == "__main__":
    main()
