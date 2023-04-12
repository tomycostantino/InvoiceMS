import json
import random
from faker import Faker
from dataset_generator.dataset_generator_base import DatasetGeneratorBase

fake = Faker()


class DatasetTemplate4(DatasetGeneratorBase):
    def __init__(self):
        super().__init__()

    def create_dataset(self, length: int):
        rows = []

        def create_product(item_n):
            item_no = item_n + 1
            description = fake.catch_phrase()
            qty = random.randint(1, 10)
            price = round(random.uniform(10, 100), 2)
            total = round(qty * price, 2)
            return [item_no, description, qty, price, total]

        for i in range(length):
            num_products = random.randint(1, 3)
            products = [create_product(_) for _ in range(num_products)]
            subtotal = round(sum(product[-1] for product in products), 2)
            discount = round(random.uniform(0, subtotal * 0.1), 2)
            total = round(subtotal - discount, 2)

            row = {
                'issuer': fake.company(),
                'invoice_n': f"{random.randint(10000, 99999)}-{random.randint(1, 9)}",
                'billed_to': fake.name().upper(),
                'mobile': fake.phone_number(),
                'address': fake.address().replace('\n', ', '),
                'date': fake.date_between(start_date='-5y', end_date='today').strftime('%d %B %Y'),
                'issuer_phone': fake.phone_number(),
                'email': fake.email(),
                'issuer_address': fake.address().replace('\n', ', '),
                'bank_name': fake.bank_country() + " Bank",
                'account_n': fake.random_int(min=10000000, max=99999999),
                'data': json.dumps(products),
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
            }

            rows.append(row)

        return rows


if __name__ == '__main__':
    dataset_gen = DatasetTemplate4()
    rows = dataset_gen.create_dataset(200)
    dataset_gen.write_csv(input('File output name without csv extension: ') + '.csv', rows[0].keys(), rows, 'w')
