import pandas as pd
from document_processing.pdf_reader import PDFDataReader
from base_model import BaseModel


class RunModel:
    '''
    This class will load a model, and read a pdf and return all predictions and words
    '''

    def __init__(self, model_name):
        '''
        Load model and create pdf reader
        '''
        self.model = BaseModel()
        self.model.load_model(model_name)
        self.pdf_reader = PDFDataReader()

    def classify_pdf(self, pdf_name):
        '''
        Open the pdf with the reader and make predictions for every word
        :param pdf_name:
        :return:
        '''

        pdf_data = self.pdf_reader.retrieve_data(pdf_name)

        # Convert the list of dictionaries to a DataFrame
        data_df = pd.DataFrame(pdf_data, columns=['word', 'coordinates'])

        # Convert the 'coordinates' tuples to strings
        data_df['coordinates'] = data_df['coordinates'].apply(lambda x: str(x))

        # Make predictions using the loaded model in production
        predictions = self.model.predict_production(data_df)

        # Create a DataFrame with the predictions
        predictions_df = pd.DataFrame(predictions, columns=['prediction'])

        # Concatenate the input DataFrame and predictions DataFrame
        result = pd.concat([data_df, predictions_df], axis=1)

        return result


if __name__ == '__main__':
    lr = RunModel('random_forest')
    results = lr.classify_pdf('/Users/tomasc/PycharmProjects/IMS/invoices_templates/PDF/12.pdf')
    print(results.to_string())
