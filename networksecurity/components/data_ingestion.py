from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import pandas as pd
import numpy as np
import pymongo
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv


# Load MongoDB connection string from .env
load_dotenv()
MONGO_DB_URL = os.getenv("MONGODB_URI")


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def export_collection_as_dataframe(self):
        """Load data from MongoDB into a DataFrame."""
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            # Connect to MongoDB and access the collection
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            # Convert MongoDB collection into DataFrame
            df = pd.DataFrame(list(collection.find()))

            # Remove MongoDB's default ID column
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            # Replace missing values
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        """Save the complete dataset into the feature store."""
        try:
            feature_store_file_path = (
                self.data_ingestion_config.feature_store_file_path
            )

            # Create the directory if it does not exist
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # Save dataset as CSV
            dataframe.to_csv(
                feature_store_file_path,
                index=False,
                header=True
            )

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """Split and save the dataset into train and test sets."""
        try:
            # Split the dataset
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Performed train test split on the dataframe")

            # Create directory for train/test files
            dir_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )
            os.makedirs(dir_path, exist_ok=True)

            # Save training data
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True
            )

            # Save testing data
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True
            )

            logging.info("Exported train and test file path")

        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def initiate_data_ingestion(self):
        """Run the complete data ingestion process."""
        try:
            # Load data from MongoDB
            dataframe = self.export_collection_as_dataframe()

            # Save data to feature store
            dataframe = self.export_data_into_feature_store(
                dataframe=dataframe
            )

            # Split data into train and test sets
            self.split_data_as_train_test(dataframe=dataframe)

            # Store the output file paths
            data_ingestion_artifact = DataIngestionArtifact(
                training_file_path=
                    self.data_ingestion_config.training_file_path,
                test_file_path=
                    self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
