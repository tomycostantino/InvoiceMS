import csv
from docxtpl import DocxTemplate
import json
import ast
import os


class TemplateFiller:
    def __init__(self):
        pass

    def read_csv(self, file):
        # Load the CSV data
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def fill_template(self, file, rows):
        # Loop through the data and generate the invoices
        # Load the template file
        template = DocxTemplate(file)

        # create the folder if it doesn't already exist
        if not os.path.exists('generated_docx'):
            os.makedirs('generated_docx')

        for i, row in enumerate(rows):
            # the data column is the list of items, and usually comes as a str
            if row['data'] is str:
                row['data'] = ast.literal_eval(row['data'])

            template.render(row)
            template.save(f"generated_docx/invoice_{i + 1}.docx")


