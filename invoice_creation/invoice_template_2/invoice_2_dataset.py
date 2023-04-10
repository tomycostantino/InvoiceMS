import csv
import json
from faker import Faker

fake = Faker()


# Function to generate a random row with the specified fields and the data column
def generate_random_row():
    data = [
        [
            fake.date_between(start_date='-30y', end_date='today').strftime('%d/%m/%Y'), # Change the date format to "dd/mm/yyyy"
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
        "issuer": f"{fake.company()} Pty Ltd",
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

    return row


# Generate 100 rows of random data
rows = [generate_random_row() for _ in range(200)]

# Write the random data to a CSV file
with open('data.csv', 'w', newline='') as csvfile:
    fieldnames = [
        "ABN", "issuer", "issuer_address", "billing_address", "invoice_n",
        "date", "date_period", "reference_n", "billed_to",
        "total_without_GST", "GST", "total_with_GST", "data"
    ]
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csv_writer.writeheader()
    for row in rows:
        csv_writer.writerow(row)
