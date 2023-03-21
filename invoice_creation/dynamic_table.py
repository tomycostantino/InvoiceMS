from docxtpl import DocxTemplate


def dynamic_table():
    # Load the Word template
    template = DocxTemplate('template.docx')

    print('About to render')
    # Define your data
    data = [
        ['Value 1', 'Value 2', 'Value 3', 'Value 4'],
        ['Value 4', 'Value 5', 'Value 6', 'Value 4'],
        ['Value 7', 'Value 8', 'Value 9', 'Value 4'],
        ['Value 7', 'Value 8', 'Value 9', 'Value 4'],
        ['Value 7', 'Value 8', 'Value 9', 'Value 4'],
    ]

    # Fill in the placeholders in the table
    context = {'data': data}
    template.render(context)
    print('Rendered')

    # Save the filled-in document
    template.save('filled-in-document.docx')


if __name__ == '__main__':
    dynamic_table()
