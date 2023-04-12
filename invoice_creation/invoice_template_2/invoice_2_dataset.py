import csv
import json
from faker import Faker
from dataset_generator.dataset_generator_base import DatasetGeneratorBase

fake = Faker()


class DatasetTemplate2(DatasetGeneratorBase):
    def __init__(self):
        super().__init__()

    def create_dataset(self, length: int):
        rows = []

        for i in range(length):
            data = [
                [
                    fake.date_between(start_date='-3y', end_date='today').strftime('%d/%m/%Y'),
                    # Change the date format to "dd/mm/yyyy"
                    fake.bs(),
                    round(fake.random.uniform(1, 500), 2),
                ]
                for _ in range(fake.random.randint(1, 5))
            ]

            total_without_GST = round(sum(item[2] for item in data), 2)
            GST = round(total_without_GST * 0.1, 2)
            total_with_GST = round(total_without_GST + GST, 2)

            row = {
                "ABN": f"{fake.random_number(digits=11)}",
                "issuer": f"{fake.company()}",
                "issuer_address": fake.address().replace("\n", ", "),
                "billing_address": fake.address().replace("\n", ", "),
                "invoice_n": fake.uuid4(),
                "date": fake.date_between(start_date='-30y', end_date='today').strftime('%d/%m/%Y'),
                "date_period": fake.date_between(start_date='-30y', end_date='today').strftime('%d/%m/%Y'),
                "reference_n": fake.random_number(digits=7),
                "billed_to": fake.name(),
                "total_without_GST": total_without_GST,
                "GST": GST,
                "total_with_GST": total_with_GST,
                "data": json.dumps(data)  # Convert the data list to a JSON string
            }

            rows.append(row)

        return rows


if __name__ == '__main__':
    dataset_gen = DatasetTemplate2()
    rows = dataset_gen.create_dataset(200)
    dataset_gen.write_csv(input('File output name without csv extension: ') + '.csv', rows[0].keys(), rows, 'w')
