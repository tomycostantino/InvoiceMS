import csv
import random
from faker import Faker

fake = Faker()

# create a list of product names and descriptions
product_list = [
    {'name': 'Parallels Desktop for Mac Pro Edition (1 Year)',
     'description': 'Run Windows on your Mac! Duration: 12 month(s)'},
    {'name': 'Parallels Toolbox (INCLUDED FOR FREE)',
     'description': 'All-in-one solution with over 30 tools for macOS and Windows'},
    {'name': 'Parallels Access (INCLUDED FOR FREE)',
     'description': 'Access your desktop applications like they were made for your iOS or Android device'}
]

# create a set of unique invoice numbers
invoice_numbers = set()
while len(invoice_numbers) < 100:
    invoice_numbers.add('AKD-' + str(random.randint(100000000, 999999999)) + str(random.randint(10, 99)))

# create a list of invoices
invoices = []
for i in range(100):
    # generate random invoice information
    full_name = fake.name()
    city_postcode = fake.city() + ' ' + fake.postcode()
    country = fake.country()
    reference_n = fake.random_int(min=100000, max=999999)
    invoice_date = fake.date_between(start_date='-1y', end_date='today')
    invoice_n = invoice_numbers.pop()
    product_items = []
    for j in range(random.randint(1, 5)):
        product = random.choice(product_list)
        product_items.append(
            {'n': j + 1, 'name': product['name'], 'delivery': 'electronic', 'qty': random.randint(1, 5),
             'price': 'AU$ ' + str(random.randint(50, 200)), 'description': product['description']})
    subtotal = sum([item['qty'] * int(item['price'].split('$ ')[1]) for item in product_items])
    gst = round(subtotal * 0.1, 2)
    total = round(subtotal + gst, 2)

    # add the invoice to the list
    invoices.append(
        {'full_name': full_name, 'city_postcode': city_postcode, 'country': country, 'reference_n': reference_n,
         'invoice_date': invoice_date, 'invoice_n': invoice_n, 'product_items': product_items, 'subtotal': subtotal,
         'gst': gst, 'total': total})

# write the invoices to a CSV file
with open('invoices.csv', mode='w', newline='') as csv_file:
    fieldnames = ['full_name', 'city_postcode', 'country', 'reference_n', 'invoice_date', 'invoice_n', 'product_n',
                  'product_name', 'delivery', 'qty', 'price', 'description', 'subtotal', 'gst', 'total']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    # create a set to keep track of invoice numbers that have been generated_docx
    used_invoice_numbers = set()
    for invoice in invoices:
        # keep generating a new invoice number until it is unique
        while invoice['invoice_n'] in used_invoice_numbers:
            invoice['invoice_n'] = 'AKD-' + str(random.randint(100000000, 999999999)) + str(random.randint(10, 99))
        used_invoice_numbers.add(invoice['invoice_n'])
        for product_item in invoice['product_items']:
            writer.writerow({'full_name': invoice['full_name'], 'city_postcode': invoice['city_postcode'],
                             'country': invoice['country'], 'reference_n': invoice['reference_n'],
                             'invoice_date': invoice['invoice_date'], 'invoice_n': invoice['invoice_n'],
                             'product_n': product_item['n'], 'product_name': product_item['name'],
                             'delivery': product_item['delivery'], 'qty': product_item['qty'],
                             'price': product_item['price'], 'description': product_item['description'],
                             'subtotal': invoice['subtotal'], 'gst': invoice['gst'], 'total': invoice['total']})
