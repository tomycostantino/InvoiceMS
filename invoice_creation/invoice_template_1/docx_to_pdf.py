import os
from docx2pdf import convert
import subprocess


def convert_docx_to_pdf(docx_directory: str, pdf_directory: str):

    # create the pdf directory if it doesn't exist
    os.makedirs(pdf_directory, exist_ok=True)

    # loop through all the docx files in the directory
    for filename in os.listdir(docx_directory):
        if filename.endswith('.docx'):
            # convert the docx file to PDF
            docx_path = os.path.join(docx_directory, filename)
            pdf_path = os.path.join(pdf_directory, filename.replace('.docx', '.pdf'))
            convert(docx_path, pdf_path)


print('Conversion complete.')


def main():
    # specify the directory containing the docx files
    docx_directory = 'generated_docx'

    # create a new directory for the converted PDFs
    pdf_directory = 'generated_pdf'

    convert_docx_to_pdf(docx_directory, pdf_directory)


if __name__ == '__main__':
    main()
