import csv
from docxtpl import DocxTemplate
import json


def read_csv(filename):
    # Load the CSV data
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def parse_context_to_data(context, row):
    parsed_context = {}
    for i in context:
        parsed_context[i] = row[i]
    return parsed_context


def fill_template(template, data, context):
    # Loop through the data and generate the invoices

    for i, row in enumerate(data):
        parsed_context = parse_context_to_data(context, row)

        # Render the template with the data and save the resulting file
        filename = f"/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/generated_docx/invoice_{i + 1}.docx"
        template.render(parsed_context)
        template.save(filename)


def main():

    data = read_csv(input('Insert csv filename with extension included: '))
    # Load the template file
    template = DocxTemplate(
        '/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/template_4.docx')

    context = {1: "full_name",
               2: "city_postcode",
               3: "country",
               4: "reference_n",
               5: "invoice_date",
               6: "invoice_n",
               7: "ps",
               8: "subtotal",
               9: "gst",
               10: "total",}

    fill_template(template, data, context)

