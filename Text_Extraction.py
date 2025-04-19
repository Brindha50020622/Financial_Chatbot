import os
import fitz  # PyMuPDF for PDFs
import docx
import sqlite3
from bs4 import BeautifulSoup

# Connect to SQLite database
conn = sqlite3.connect("financial_data.db")
cursor = conn.cursor()

# Create table for storing extracted text
cursor.execute("""
CREATE TABLE IF NOT EXISTS financial_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    file_name TEXT,
    file_type TEXT,
    extracted_text TEXT
)
""")
conn.commit()

# Define the base directory
base_dir = "Data/financial reports"

# Function to extract text from PDFs
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
    return text

# Function to extract text from HTML
def extract_text_from_html(html_path):
    text = ""
    encodings = ["utf-8", "ISO-8859-1", "windows-1252"]

    for encoding in encodings:
        try:
            with open(html_path, "r", encoding=encoding) as file:
                soup = BeautifulSoup(file, "html.parser")
                text = soup.get_text(separator="\n")
            break  # If successful, exit loop
        except UnicodeDecodeError:
            continue  # Try next encoding
        except Exception as e:
            print(f"Error reading HTML {html_path}: {e}")
            return ""

    return text

# Process all company folders
for company in os.listdir(base_dir):
    company_path = os.path.join(base_dir, company)

    if os.path.isdir(company_path):  # Ensure it's a folder
        # Loop through all files inside the company folder
        for file_name in os.listdir(company_path):
            file_path = os.path.join(company_path, file_name)

            if file_name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(file_path)
                file_type = "pdf"
            elif file_name.endswith(".docx"):
                extracted_text = extract_text_from_docx(file_path)
                file_type = "docx"
            elif file_name.endswith(".html"):
                extracted_text = extract_text_from_html(file_path)
                file_type = "html"
            else:
                continue  # Skip unknown file types

            # Insert extracted text into database
            cursor.execute("""
            INSERT INTO financial_reports (company, file_name, file_type, extracted_text)
            VALUES (?, ?, ?, ?)
            """, (company, file_name, file_type, extracted_text))

conn.commit()
conn.close()

print("Text extraction and storage completed!")
