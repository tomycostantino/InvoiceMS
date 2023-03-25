import csv
from docxtpl import DocxTemplate
import json
import ast
import os


def read_csv(filename):
    # Load the CSV data
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def fill_template(template_filename, rows):
    # Loop through the data and generate the invoices
    # Load the template file
    template = DocxTemplate(template_filename)

    # create the folder if it doesn't already exist
    if not os.path.exists('generated_docx'):
        os.makedirs('generated_docx')

    for i, row in enumerate(rows):

        # the list for the products is a str, so convert it to a literal list
        row['data'] = ast.literal_eval(row['data'])

        # Render the template with the data and save the resulting file
        template.render(row)
        template.save(f"generated_docx/invoice_{i + 1}.docx")


def main():

    rows = read_csv(input('Insert csv filename with extension included: '))

    fill_template('1.docx', rows)


if __name__ == '__main__':
    main()
