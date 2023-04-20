import os
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


class BaseModel:
    def __init__(self):
        self.pipeline = None
        self._data = None

    def load_and_merge_datasets(self, csv_folder):
        # List of CSV files
        csv_files = []

        for dataset in os.listdir(csv_folder):
            if dataset.endswith('.csv'):
                print(f'Retrieving data from {dataset}')
                csv_files.append(f'../datasets/{dataset}')

        data_frames = [pd.read_csv(file) for file in csv_files]
        return pd.concat(data_frames, ignore_index=True)

    def preprocess(self, df):
        df["coordinates"] = df["coordinates"].apply(lambda x: x.strip("()"))
        df["coordinates"] = df["coordinates"].apply(lambda x: x.replace(",", ""))
        df["word_coordinates"] = df["word"] + " " + df["coordinates"]
        return df["word_coordinates"]

    def save_model(self, file_name):
        joblib.dump(self.pipeline, file_name)

    def load_model(self, file_name):
        self.pipeline = joblib.load(file_name)

    def evaluate(self, y_true, y_pred):
        print("Confusion Matrix:")
        print(confusion_matrix(y_true, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred))
        print("\nAccuracy Score:")
        print(accuracy_score(y_true, y_pred))
