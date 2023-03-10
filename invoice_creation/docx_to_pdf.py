import os
from docx2pdf import convert

# specify the directory containing the docx files
docx_directory = '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/generated_docx'

# create a new directory for the converted PDFs
pdf_directory = '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/generated_pdf'
if not os.path.exists(pdf_directory):
    os.makedirs(pdf_directory)

# loop through all the docx files in the directory
for filename in os.listdir(docx_directory):
    print(filename)
    if filename.endswith('.docx'):
        # convert the docx file to PDF
        docx_path = os.path.join(docx_directory, filename)
        pdf_path = os.path.join(pdf_directory, filename.replace('.docx', '.pdf'))
        convert(docx_path, pdf_path)

print('Conversion complete.')
