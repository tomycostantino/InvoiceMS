import random
import csv
from faker import Faker
from invoice_creation.dataset_generator_base import DatasetGeneratorBase

fake = Faker()


class DatasetGeneratorTemplate1(DatasetGeneratorBase):
    def __init__(self):
        super().__init__()

    def create_dataset(self, length: int):

        rows = []

        for i in range(length):
            # create random data
            issuer = fake.company()
            issuer_address = fake.address()
            phone = fake.phone_number()
            invoice_n = str(random.randint(10000000, 99999999))
            date = fake.date_between(start_date='-5y', end_date='today').strftime("%d %B, %Y")
            billed_to = fake.company()
            billing_address = fake.address()

            # this is the product description
            data = [
                [i + 1, fake.catch_phrase(), random.randint(100, 1000), ""]
                for i in range(random.randint(1, 5))
            ]
            for row in data:
                row[3] = row[2] * random.randint(1, 2)  # calculate amount
                row[2] = "${:.2f}".format(row[2])  # format price as currency
                row[3] = "${:.2f}".format(row[3])  # format amount as currency

            total = sum([float(row[3][1:]) for row in data])  # convert amount string to float and sum

            # create invoice dictionary
            invoice = {
                "issuer": issuer,
                "issuer_address": issuer_address,
                "phone": phone,
                "invoice_n": invoice_n,
                "date": date,
                "billed_to": billed_to,
                "billing_address": billing_address,
                "data": data,
                "total": total,
                "bank_name": "Bank of America",
                "account_n": "0123 4567 8901",
                "support_email": f"support@reallygreatsite.com"
            }

            rows.append(invoice)

        return rows


if __name__ == '__main__':
    # generate invoices
    gen = DatasetGeneratorTemplate1()
    rows = gen.create_dataset(200)
    print(type(list(rows[0].keys())))
    gen.write_csv(input('File output name without csv: ') + '.csv', rows[0].keys(), rows)
