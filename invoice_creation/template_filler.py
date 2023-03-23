import csv
from docxtpl import DocxTemplate
import json


def read_csv(filename):
    # Load the CSV data
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def generate_context(data):
    context = {}
    for idx, value in enumerate(data[0]):   # data[0] is the header of the csv
        context[idx] = value

    return context


def fill_template(template, data):
    # Loop through the data and generate the invoices

    context = generate_context(data)

    for i, row in enumerate(data):

        # Render the template with the data and save the resulting file
        filename = f"/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/temp_1/generated_docx/invoice_{i + 1}.docx"
        template.render(row)
        template.save(filename)


def main():

    data = read_csv(input('Insert csv filename with extension included: '))
    # Load the template file
    template = DocxTemplate(
        '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/temp_1/1.docx')

    fill_template(template, data)


if __name__ == '__main__':
    main()
