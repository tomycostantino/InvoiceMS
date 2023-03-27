import ast
from invoice_creation.template_filler import TemplateFiller


def main():
    filler = TemplateFiller()

    rows = filler.read_csv(input('Insert csv filename with extension included: '))

    filler.fill_template('1.docx', rows)


if __name__ == '__main__':
    main()
