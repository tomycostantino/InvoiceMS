import csv
import ast
import os
from pdfjinja import PdfJinja


class TemplateFiller:
    def __init__(self):
        pass

    def read_csv(self, file):
        # Load the CSV data
        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def fill_template(self, file, rows):
        # Loop through the data and generate the invoices
        # Load the template file
        pdfjinja = PdfJinja(file)

        # create the folder if it doesn't already exist
        if not os.path.exists('generated_pdf'):
            os.makedirs('generated_pdf')

        for i, row in enumerate(rows):
            # the data column is the list of items, and usually comes as a str
            if type(row['data']) == str:
                row['data'] = ast.literal_eval(row['data'])

            rendered_pdf = pdfjinja(row)
            with open(f"generated_pdf/{i + 1}.pdf", "wb") as output:
                output.write(rendered_pdf.read())


def main():
    filler = TemplateFiller()

    rows = filler.read_csv(input('Insert csv filename with extension included: '))

    for row in rows:
        if type(row['data']) == str:
            row['data'] = ast.literal_eval(row['data'])
    filler.fill_template('1.pdf', rows)


if __name__ == '__main__':
    main()
