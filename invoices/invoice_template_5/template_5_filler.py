import csv
import json
from docxtpl import DocxTemplate
import os


# Read the CSV file and load the data
with open('data.csv', 'r', newline='') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    rows = [row for row in csv_reader]

# create the folder if it doesn't already exist
if not os.path.exists('generated_docx'):
    os.makedirs('generated_docx')

template = DocxTemplate('5.docx')


# Render the invoices using the docx template
for i, row in enumerate(rows):
    row["data"] = json.loads(row["data"])  # Convert the JSON string to a list
    # Render the invoice using the data
    template.render(row)

    # Save the invoice to a docx file
    template.save(f'generated_docx/{i + 1}.docx')

