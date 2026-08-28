import os
import json
import pandas as pd
import numpy as np
import sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import certifi
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


# Load MongoDB credentials from environment variables
load_dotenv(dotenv_path=Path("atlas-credentials.env"))
uri = os.getenv("MONGODB_URI")

ca = certifi.where()


class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # Convert CSV file into a list of JSON records
    def cv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)

            # Convert DataFrame rows into dictionaries
            records = json.loads(data.to_json(orient="records"))

            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # Insert the records into the specified MongoDB collection
    def insert_data_mongodb(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            # Create MongoDB client
            self.mongo_client = MongoClient(uri)

            # Select the database
            self.database = self.mongo_client[self.database]

            # Select the collection inside that database
            self.collection = self.database[self.collection]

            # Insert all records into MongoDB
            self.collection.insert_many(self.records)

            return len(self.records)

        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == "__main__":

    # Dataset and MongoDB configuration
    FILE_PATH = "Network_Data/phisingData.csv"
    DATABASE = "Swkratis"
    Collection = "NetworkData"

    # Create extractor and convert CSV data
    network_obj = NetworkDataExtract()
    records = network_obj.cv_to_json_convertor(FILE_PATH)

    # Upload records to MongoDB
    no_of_records = network_obj.insert_data_mongodb(
        records=records,
        database=DATABASE,
        collection=Collection
    )

    print(no_of_records)