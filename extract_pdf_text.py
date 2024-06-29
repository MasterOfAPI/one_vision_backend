import pytesseract
from PIL import Image
from pdf2image import convert_from_path

# Define the path to the PDF
pdf_path = '/Users/yoon/Downloads/backend/translated_document.pdf'

# Function to extract text from PDF using OCR
def extract_text_from_pdf_with_ocr(pdf_path):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)

    # Initialize text variable
    text = ""

    # Iterate through images and extract text using OCR
    for i, img in enumerate(images):
        print(f"Extracting text from page {i+1}")
        text += pytesseract.image_to_string(img, lang='kor')  # Set language to Korean

    return text

# Extract text from the PDF
extracted_text = extract_text_from_pdf_with_ocr(pdf_path)

# Print the extracted text
print("Extracted Text:")
print(extracted_text)
