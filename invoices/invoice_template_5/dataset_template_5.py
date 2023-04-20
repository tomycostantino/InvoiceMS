import json
import random
from faker import Faker
from dataset_generator.dataset_generator_base import DatasetGeneratorBase

fake = Faker()


class DatasetTemplate5(DatasetGeneratorBase):
    def __init__(self):
        super().__init__()

    def create_dataset(self, length: int):
        rows = []

        def create_product():
            description = fake.catch_phrase()
            qty = random.randint(1, 5)
            price = round(random.uniform(10, 100), 2)
            total = round(qty * price, 2)
            return [description, qty, price, total]

        for i in range(length):
            num_products = random.randint(1, 5)
            products = [create_product() for _ in range(num_products)]
            subtotal = round(sum(product[-1] for product in products), 2)
            tax = round(subtotal * 0.1, 2)
            total = round(subtotal + tax, 2)

            row = {
                'issuer': fake.company(),
                'invoice_n': f"{random.randint(10000, 99999)}",
                'billed_to': fake.name().upper(),
                'mobile': fake.phone_number(),
                'address': fake.address().replace('\n', ', '),
                'date': fake.date_between(start_date='-5y', end_date='today').strftime('%d/%m/%Y'),
                'email': fake.email(),
                'data': json.dumps(products),
                'subtotal': subtotal,
                'tax': tax,
                'total': total,
            }

            rows.append(row)

        return rows


if __name__ == '__main__':
    dataset_gen = DatasetTemplate5()
    rows = dataset_gen.create_dataset(200)
    dataset_gen.write_csv(input('File output filename without csv extension: ') + '.csv', rows[0].keys(), rows, 'w')
