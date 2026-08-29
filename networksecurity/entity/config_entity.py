"""
This file defines the configuration used by the training pipeline.
It centralizes the paths, folders, and settings needed by each pipeline component.
"""
from datetime import datetime
import os
from networksecurity.constant import training_pipeline

"""
Stores the main configuration for a pipeline run, including the timestamp,
artifact directory, and final model directory.
"""
class TrainingPipelineConfig:
    def __init__(self, timestamp=datetime.now()):
        # Format execution start time for folder naming
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training_pipeline.PIPELINE_NAME
        self.artifact_name = training_pipeline.ARTIFACT_DIR
        # Root output directory for this specific run: e.g., "Artifacts/08_29_2026_09_46_22"
        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        # Directory where the finalized serialized model will be exported
        self.model_dir = os.path.join("final_model")
        self.timestamp: str = timestamp

"""
Stores the configuration for data ingestion, including the locations of
raw, training, and testing data and the MongoDB source information.
"""
class DataIngestionConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        # Component-level root: "Artifacts/<timestamp>/data_ingestion"
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir, training_pipeline.DATA_INGESTION_DIR_NAME
        )
        # Raw extracted dataset destination: ".../feature_store/<FILE_NAME>"
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir, training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR, training_pipeline.FILE_NAME
        )
        # Processed train split: ".../ingested/<TRAIN_FILE_NAME>"
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir, training_pipeline.DATA_INGESTION_INGESTED_DIR, training_pipeline.TRAIN_FILE_NAME
        )
        # Processed test split: ".../ingested/<TEST_FILE_NAME>"
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir, training_pipeline.DATA_INGESTION_INGESTED_DIR, training_pipeline.TEST_FILE_NAME
        )
        # Train/test split ratio (e.g., 0.2)
        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATION
        # Source MongoDB / database target metadata
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME