import csv
import random
import datetime
import json
from faker import Faker
from dataset_generator.dataset_generator_base import DatasetGeneratorBase

fake = Faker()


class DatasetTemplate3(DatasetGeneratorBase):
    def __init__(self):
        super().__init__()

    def create_dataset(self, length: int):

        rows = []

        for i in range(length):

            product_rows = random.randint(1, 5)
            product_data = []
            subtotal = 0
            for _ in range(product_rows):
                description = fake.bs()
                rate = round(random.uniform(10, 500), 2)
                qty = random.randint(1, 10)
                total = round(rate * qty, 2)
                subtotal += total
                product_data.append([description, rate, qty, total])

            tax_rate = random.uniform(0.05, 0.2)
            tax = round(subtotal * tax_rate, 2)
            total = round(subtotal + tax, 2)

            row = {
                "issuer": fake.company(),
                "issuer_address": fake.address(),
                "issuer_number": fake.phone_number(),
                "business_code": str(random.randint(1111111, 9999999)),
                "invoice_n": random.randint(1, 99999),
                "date": fake.date_between(start_date='-5y', end_date='today'),
                "billed_to": fake.name(),
                "email": fake.email(),
                "website": fake.url(),
                "deadline": random.randint(1, 60),
                "data": json.dumps(product_data),
                "subtotal": subtotal,
                "tax": tax,
                "total": total,
            }
            rows.append(row)

        return rows


if __name__ == '__main__':
    dataset_gen = DatasetTemplate3()
    rows = dataset_gen.create_dataset(200)
    dataset_gen.write_csv(input('File output filename without csv extension: ') + '.csv', rows[0].keys(), rows, 'w')
