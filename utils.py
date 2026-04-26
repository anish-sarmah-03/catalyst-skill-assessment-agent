import fitz  # PyMuPDF

#To read a pdf file and extract the text from it
def extract_text_from_pdf(uploaded_file):
    
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text
