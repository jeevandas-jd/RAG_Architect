from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):

    reader= PdfReader(pdf_path)
    text = ""

    text_file_name= pdf_path.replace(".pdf", ".txt")

    with open(text_file_name, "w", encoding="utf-8") as text_file:
        for page in reader.pages:
            page_text = page.extract_text()
            text_file.write(page_text + "\n")
            text += page_text + "\n"
    
    return text 

"""if __name__ == "__main__":
    pdf_path = "sample.pdf"  # Replace with your PDF file path
    extracted_text = extract_text_from_pdf(pdf_path)
    print(extracted_text)
"""