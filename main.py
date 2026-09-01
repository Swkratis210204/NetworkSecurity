import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    TrainingPipelineConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)


if __name__ == "__main__":
    try:

        # ============================================================
        # Initialize Training Pipeline Configuration
        # ============================================================

        training_pipeline_config = TrainingPipelineConfig()

        # ============================================================
        # Data Ingestion
        # ============================================================

        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline_config
        )

        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config
        )

        logging.info("Initiate the data ingestion")

        data_ingestion_artifact = (
            data_ingestion.initiate_data_ingestion()
        )

        logging.info("Data Ingestion completed\n")

        print(data_ingestion_artifact)

        # ============================================================
        # Data Validation
        # ============================================================

        data_validation_config = DataValidationConfig(
            training_pipeline_config=training_pipeline_config
        )

        data_validation = DataValidation(
            data_ingestion_artifact,
            data_validation_config,
        )

        logging.info("Initiate Data Validation")

        data_validation_artifact = (
            data_validation.initiate_data_validation()
        )

        logging.info("Data Validation Completed\n")

        print(data_validation_artifact)

        # ============================================================
        # Data Transformation
        # ============================================================

        logging.info("Data Transformation Started")

        data_transformation_config = DataTransformationConfig(
            training_pipeline_config=training_pipeline_config
        )

        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            data_transformation_config=data_transformation_config,
        )

        data_transformation_artifact = (
            data_transformation.initiate_data_transformation()
        )

        print(data_transformation_artifact)

        logging.info("Data Transformation Completed\n")

        # ============================================================
        # Model Training
        # ============================================================

        logging.info("Model Training Started")

        model_trainer_config = ModelTrainerConfig(
            training_pipeline_config=training_pipeline_config
        )

        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact,
        )

        model_trainer_artifact = (
            model_trainer.iniatiate_model_trainer()
        )

        print(model_trainer_artifact)

        logging.info("Model Training Completed\n")

        # ============================================================
        # Pipeline Completed
        # ============================================================

        logging.info("Training Pipeline Completed Successfully")

    except Exception as e:
        raise NetworkSecurityException(e, sys)
