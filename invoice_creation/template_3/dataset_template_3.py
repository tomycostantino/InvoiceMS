import csv
import random
import datetime
import json
from faker import Faker

fake = Faker()


def generate_data(rows=200):
    data = []
    for _ in range(rows):
        issuer = fake.company()
        issuer_address = fake.address()
        issuer_number = fake.phone_number()
        business_code = ' '.join([str(random.randint(10**8, 10**9 - 1)) for _ in range(3)])
        invoice_n = random.randint(1, 99999)
        date = fake.date_between(start_date='-5y', end_date='today')
        billed_to = fake.name()
        email = fake.email()
        website = fake.url()
        deadline = random.randint(1, 60)

        product_rows = random.randint(1, 10)
        product_data = []
        subtotal = 0
        for _ in range(product_rows):
            description = fake.bs()
            rate = round(random.uniform(10, 500), 2)
            qty = random.randint(1, 10)
            total = rate * qty
            subtotal += total
            product_data.append([description, rate, qty, total])

        tax_rate = random.uniform(0.05, 0.2)
        tax = round(subtotal * tax_rate, 2)
        total = subtotal + tax

        row = {
            "issuer": issuer,
            "issuer_address": issuer_address,
            "issuer_number": issuer_number,
            "business_code": business_code,
            "invoice_n": invoice_n,
            "date": date,
            "billed_to": billed_to,
            "email": email,
            "website": website,
            "deadline": deadline,
            "data": json.dumps(product_data),
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
        }
        data.append(row)

    return data


dataset = generate_data()

with open('data.csv', 'w', newline='') as csvfile:
    fieldnames = list(dataset[0].keys())
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()
    for row in dataset:
        csv_writer.writerow(row)

