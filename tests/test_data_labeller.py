import unittest
from labeller.document_labeller import DataLabeller
import fitz
import os


class TestDataLabeller(unittest.TestCase):
    def setUp(self):
        self.dl = DataLabeller()
        self.test_pdf_path = "/invoices/invoice_template_1/generated_pdf"

    def test_read_csv(self):
        self.dl._read_csv("/Users/tomasc/PycharmProjects/IMS/InvoiceMS/invoices/invoice_template_1/data.csv")
        self.assertTrue(len(self.dl._rows) > 0, "Rows should not be empty")

    def test_find_subrectangle(self):
        locations = {'invoice': (50, 60, 100, 80), 'total': (150, 60, 200, 80)}
        subrectangle = self.dl._find_rectangle(locations)
        self.assertEqual(subrectangle, (50, 60, 200, 80), "Subrectangle should match the expected values")

    # Test all other methods similarly
    # ...


if __name__ == "__main__":
    unittest.main()
