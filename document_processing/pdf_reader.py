import fitz
import re


class PDFDataReader:
    def __init__(self):
        pass

    def retrieve_data(self, filename):
        '''
        Read data for when model is used in production
        :param filename:
        :return:
        '''

        pdf = fitz.open(filename)
        words_in_file = []
        for page in pdf.pages():
            for word in page.get_text('words'):
                words_in_file.append(
                    {
                        'word': word[4],
                        'coordinates': self._round_coordinates(word[:4]),
                    }
                )
        return words_in_file

    def retrieve_text_blocks(self, filename):
        """
        Retrieve blocks of text to perform NER
        :param filename:
        :return:
        """
        pdf = fitz.open(filename)
        blocks = []

        for page in pdf.pages():
            for block in page.get_text("blocks"):
                blocks.append(block[4])
        return self._clean_blocks_str(blocks)

    def _clean_blocks_str(self, blocks):
        """
        Remove \n from block strings
        :param blocks:
        :return:
        """
        # Step 1: Remove leading and trailing spaces
        blocks = [s.strip() for s in blocks]

        # Step 2: Filter out empty strings
        blocks = [s for s in blocks if s]

        # Step 3: Replace multiple spaces with a single space
        blocks = [re.sub(' +', ' ', s) for s in blocks]

        blocks = [s.replace('\n', '') for s in blocks]

        return blocks

    def _round_coordinates(self, coordinates):
        '''
        Round coordinates to 4 decimal points and return as tuple
        :param coordinates:
        :return:
        '''
        rounded_coordinates = []
        for coordinate in coordinates:
            rounded_coordinates.append(round(coordinate, 4))

        return tuple(rounded_coordinates)


if __name__ == '__main__':
    reader = PDFDataReader()
    text = reader.retrieve_text_blocks('/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoices/invoice_template_5/generated_pdf/10.pdf')
    text = [s.replace('\n', '') for s in text]
    for t in text:
        print(t)
