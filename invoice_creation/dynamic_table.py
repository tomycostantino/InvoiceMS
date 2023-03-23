from docxtpl import DocxTemplate


def dynamic_table(filename: str, file_output: str, data):
    # Load the Word template
    template = DocxTemplate(filename)

    # Fill in the placeholders in the table
    context = {'data': data}
    template.render(context)

    # Save the filled-in document
    template.save(file_output)


if __name__ == '__main__':
    dynamic_table('template.docx', 'filled-in-document.docx', [[j for j in range(5)] for i in range(5)])
