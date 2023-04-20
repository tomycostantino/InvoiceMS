import os
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


class BaseModel:
    def __init__(self):
        '''
        Start the dataset and pipeline
        '''
        self.pipeline = None
        self._data = None

    def load_and_merge_datasets(self, csv_folder):
        '''
        Load multiple csv files merge and shuffle
        :param csv_folder:
        :return:
        '''

        # List of CSV file names
        csv_files = []

        # get all the dataset names in a folder
        for dataset in os.listdir(csv_folder):
            if dataset.endswith('.csv'):
                print(f'Retrieving data from {dataset}')
                csv_files.append(f'{csv_folder}/{dataset}')

        # open datasets and concatenate into one
        data_frames = [pd.read_csv(file) for file in csv_files]
        data = pd.concat(data_frames, ignore_index=True)

        # Shuffle the data and return
        return data.sample(frac=1, random_state=42).reset_index(drop=True)

    def preprocess_data(self, df):
        '''
        prepare data for model to be trained or to predict
        :param df:
        :return:
        '''
        df["coordinates"] = df["coordinates"].apply(lambda x: x.strip("()"))
        df["coordinates"] = df["coordinates"].apply(lambda x: x.replace(",", ""))
        df["word_coordinates"] = df["word"] + " " + df["coordinates"]
        return df["word_coordinates"]

    def save_model(self, file_name):
        '''
        Save model to be loaded later
        :param file_name:
        :return:
        '''
        joblib.dump(self.pipeline, file_name)

    def load_model(self, file_name):
        '''
        Load already trained model
        :param file_name:
        :return:
        '''
        self.pipeline = joblib.load(file_name)

    def predict_production(self, X):
        '''
        Will be called when using a model to predict in real scenarios
        :param X:
        :return:
        '''
        if self.pipeline is not None:
            X_preprocessed = self.preprocess_data(X)
            return self.pipeline.predict(X_preprocessed)
        else:
            raise ValueError("No model has been loaded. Please load a model before making predictions.")

    def evaluate(self, y_true, y_pred):
        '''
        Model evaluation after it has been trained
        :param y_true:
        :param y_pred:
        :return:
        '''

        print("Confusion Matrix:")
        print(confusion_matrix(y_true, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred))
        print("\nAccuracy Score:")
        print(accuracy_score(y_true, y_pred))
