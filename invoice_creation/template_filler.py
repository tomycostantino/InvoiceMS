import csv
from docxtpl import DocxTemplate

# Load the CSV data
with open('invoices.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

# Load the template file
template = DocxTemplate('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/template_4.docx')

# Loop through the data and generate the invoices
for i, row in enumerate(data):
    context = {
        'full_name': row['full_name'],
        'city_postcode': row['city_postcode'],
        'country': row['country'],
        'reference_n': row['reference_n'],
        'invoice_date': row['invoice_date'],
        'invoice_n': row['invoice_n'],
        'ps': {
            'n': row['product_n'],
            'name': row['product_name'],
            'delivery': row['delivery'],
            'qty': row['qty'],
            'price': row['price'],
            'description': row['description']
        },
        'subtotal': row['subtotal'],
        'gst': row['gst'],
        'total': row['total']
    }

    # Render the template with the data and save the resulting file
    filename = f"/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoice_creation/templates/template_4/generated_docx/invoice_{i + 1}.docx"
    template.render(context)
    template.save(filename)
