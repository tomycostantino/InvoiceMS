from faker import Faker
import csv


class DatasetGeneratorBase:
    def __init__(self):
        self.fake = Faker()

    def write_csv(self, file, fieldnames, rows):
        # write invoices to CSV file
        with open(file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


if __name__ == '__main__':
    generator = DatasetGeneratorBase()
