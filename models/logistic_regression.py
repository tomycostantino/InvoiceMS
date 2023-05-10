from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

from base_model import BaseModel


class LogisticRegressionModel(BaseModel):
    def __init__(self):
        '''
        Init parent class and create pipeline
        '''
        super().__init__()
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('classifier', LogisticRegression(random_state=42)),
        ])

    def train(self, X_train, y_train):
        '''
        Fit data into model
        :param X_train:
        :param y_train:
        :return:
        '''
        # X_train_preprocessed = self.preprocess_data(X_train)
        self.pipeline.fit(X_train, y_train)

    def predict(self, X_test):
        '''
        Make predictions in data
        :param X_test:
        :return:
        '''
        X_test_preprocessed = self.preprocess_data(X_test)
        return self.pipeline.predict(X_test_preprocessed)


if __name__ == '__main__':
    # Create an instance of the LogisticRegressionModel class
    model = LogisticRegressionModel()

    # Load and merge datasets
    data = model.load_and_merge_datasets('../datasets')

    # Shuffle the data
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)

    data = model.preprocess_data(data)  # Add this line to preprocess the data before creating X and y

    # Split the data into training and testing sets
    X = data[['word', 'coordinates']]
    y = data['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model.train(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate the model
    model.evaluate(y_test, y_pred)
