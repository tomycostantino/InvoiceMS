from faker import Faker
import csv


class DatasetGeneratorBase:
    def __init__(self):
        pass

    def write_csv(self, file, fieldnames, rows, mode):
        # write invoices to CSV file
        with open(file, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


if __name__ == '__main__':
    generator = DatasetGeneratorBase()
