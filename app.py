import streamlit as st
import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urlparse, urljoin

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def scrape_page(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator='\n')
    except Exception as e:
        return ""

def scrape_website(url, max_depth=3, current_depth=0, visited=None):
    if visited is None:
        visited = set()

    if current_depth > max_depth or url in visited:
        return ""
    
    visited.add(url)
    text = scrape_page(url)

    if current_depth < max_depth:
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            if is_valid_url(full_url) and urlparse(url).netloc == urlparse(full_url).netloc:
                text += scrape_website(full_url, max_depth, current_depth + 1, visited)

    return text

def create_pdf(text, filename="scraped_content.pdf"):
    pdfkit.from_string(text, filename)
    return filename

st.title("Website Text Scraper")
input_url = st.text_input("Enter a Website URL")

# Dropdown for depth control
depth_options = [1, 2, 3, 4, 5] # Define the depth options
max_depth = st.selectbox("Select Maximum Depth for Crawling", depth_options)

if st.button("Scrape"):
    if is_valid_url(input_url):
        with st.spinner('Scraping...'):
            scraped_text = scrape_website(input_url, max_depth=max_depth)
            if scraped_text:
                pdf_file = create_pdf(scraped_text)
                st.success('Scraping Done! Download the PDF below.')
                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=pdf_file,
                        mime="application/octet-stream"
                    )
            else:
                st.error("Failed to scrape the website.")
    else:
        st.error("Invalid URL provided.")

if __name__ == "__main__":
    st.run()
