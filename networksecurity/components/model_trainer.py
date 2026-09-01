import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

import mlflow
import mlflow.sklearn

load_dotenv()

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel

from networksecurity.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_models,
)

from networksecurity.utils.ml_utils.metric.classification_metric import (
    get_classification_score,
)
import dagshub
dagshub.init(repo_owner='Swkratis210204', repo_name='NetworkSecurity', mlflow=True)


class ModelTrainer:

    def __init__(
        self,
        model_trainer_config: ModelTrainerConfig,
        data_transformation_artifact: DataTransformationArtifact,
    ):
        try:

            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = (
                data_transformation_artifact
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ================================================================
    # MLflow Tracking
    # ================================================================

    def track_mlflow(
        self,
        model,
        train_metric,
        test_metric,
    ):
        """
        Log the trained model and both train/test metrics
        into a single MLflow run.
        """

        try:

            # Point MLflow at the DagsHub-hosted tracking server
            # (MLFLOW_TRACKING_USERNAME/PASSWORD are read from the
            # environment automatically by mlflow for auth)
            mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

            # Make sure the experiment exists
            mlflow.set_experiment("NetworkSecurity")

            # Start ONE MLflow run
            with mlflow.start_run():

                # ----------------------------------------------------
                # Train Metrics
                # ----------------------------------------------------

                mlflow.log_metric(
                    "train_f1_score",
                    train_metric.f1_score,
                )

                mlflow.log_metric(
                    "train_precision",
                    train_metric.precision_score,
                )

                mlflow.log_metric(
                    "train_recall",
                    train_metric.recall_score,
                )

                # ----------------------------------------------------
                # Test Metrics
                # ----------------------------------------------------

                mlflow.log_metric(
                    "test_f1_score",
                    test_metric.f1_score,
                )

                mlflow.log_metric(
                    "test_precision",
                    test_metric.precision_score,
                )

                mlflow.log_metric(
                    "test_recall",
                    test_metric.recall_score,
                )

                # ----------------------------------------------------
                # Log Model
                # ----------------------------------------------------

                mlflow.sklearn.log_model(
                    model,
                    name="model",
                )

                # ----------------------------------------------------
                # Print MLflow information
                # ----------------------------------------------------

                run_id = mlflow.active_run().info.run_id

                logging.info(
                    f"MLflow Run ID: {run_id}"
                )

                logging.info(
                    "MLflow metrics and model logged successfully"
                )

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ================================================================
    # Train Model
    # ================================================================

    def train_model(
        self,
        x_train,
        y_train,
        x_test,
        y_test,
    ):

        try:

            # ========================================================
            # Models
            # ========================================================

            models = {
                "Random Forest": RandomForestClassifier(),

                "Decision Tree": DecisionTreeClassifier(),

                "Gradient Boosting": GradientBoostingClassifier(),

                "Logistic Regression": LogisticRegression(
                    verbose=1
                ),

                "AdaBoost": AdaBoostClassifier(),
            }

            # ========================================================
            # Hyperparameters
            # ========================================================

            params = {
            "Decision Tree": {
                "criterion": ["gini", "entropy"],
            },

            "Random Forest": {
                "n_estimators": [16, 32],
            },

            "Gradient Boosting": {
                "learning_rate": [0.1, 0.01],
                "n_estimators": [16, 32],
            },

            "Logistic Regression": {},

            "AdaBoost": {
                "learning_rate": [0.1, 0.01],
                "n_estimators": [16, 32],
            }
        }

            # ========================================================
            # Evaluate Models
            # ========================================================

            logging.info("Evaluating models")

            models_report: dict = evaluate_models(
                x_train,
                y_train,
                x_test,
                y_test,
                models,
                params
            )
            logging.info(
                f"Model evaluation report: {models_report}"
            )

            # ========================================================
            # Get Best Model Score
            # ========================================================

            best_score_model = max(
                sorted(models_report.values())
            )

            # ========================================================
            # Get Best Model Name
            # ========================================================

            best_model_name = list(
                models_report.keys()
            )[
                list(models_report.values()).index(
                    best_score_model
                )
            ]

            # ========================================================
            # Get Best Model
            # ========================================================

            best_model = models[best_model_name]

            logging.info(
                f"Best model found: {best_model_name}"
            )

            logging.info(
                f"Best model score: {best_score_model}"
            )

            # ========================================================
            # Training Metrics
            # ========================================================

            y_train_pred = best_model.predict(x_train)

            classification_train_metric = (
                get_classification_score(
                    y_true=y_train,
                    y_pred=y_train_pred,
                )
            )

            logging.info(
                f"Training metrics: "
                f"{classification_train_metric}"
            )

            # ========================================================
            # Testing Metrics
            # ========================================================

            y_test_pred = best_model.predict(x_test)

            classification_test_metric = (
                get_classification_score(
                    y_true=y_test,
                    y_pred=y_test_pred,
                )
            )

            logging.info(
                f"Testing metrics: "
                f"{classification_test_metric}"
            )

            # ========================================================
            # MLflow Tracking
            # ========================================================

            self.track_mlflow(
                model=best_model,
                train_metric=classification_train_metric,
                test_metric=classification_test_metric,
            )

            # ========================================================
            # Load Preprocessor
            # ========================================================

            preprocessor = load_object(
                filepath=(
                    self.data_transformation_artifact
                    .transformed_object_file_path
                )
            )

            # ========================================================
            # Create Model Directory
            # ========================================================

            model_dir_path = os.path.dirname(
                self.model_trainer_config
                .trained_model_file_path
            )

            os.makedirs(
                model_dir_path,
                exist_ok=True,
            )

            # ========================================================
            # Create Network Model
            # ========================================================

            network_model = NetworkModel(
                preprocessor=preprocessor,
                model=best_model,
            )

            # ========================================================
            # Save Model
            # ========================================================

            save_object(
                self.model_trainer_config
                .trained_model_file_path,
                obj=network_model,
            )

            logging.info(
                "Trained model saved successfully"
            )

            # ========================================================
            # Model Trainer Artifact
            # ========================================================

            save_object("final_model.pkl",best_model)
            
            
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=(
                    self.model_trainer_config
                    .trained_model_file_path
                ),

                train_metric_artifact=(
                    classification_train_metric
                ),

                test_metric_artifact=(
                    classification_test_metric
                ),
            )

            logging.info(
                f"Model trainer artifact: "
                f"{model_trainer_artifact}"
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    # ================================================================
    # Initiate Model Trainer
    # ================================================================

    def iniatiate_model_trainer(
        self,
    ) -> ModelTrainerArtifact:

        try:

            # ========================================================
            # Get Transformed File Paths
            # ========================================================

            train_file_path = (
                self.data_transformation_artifact
                .transformed_train_file_path
            )

            test_file_path = (
                self.data_transformation_artifact
                .transformed_test_file_path
            )

            # ========================================================
            # Load Training/Test Arrays
            # ========================================================

            train_arr = load_numpy_array_data(
                train_file_path
            )

            test_arr = load_numpy_array_data(
                test_file_path
            )

            # ========================================================
            # Split Features and Target
            # ========================================================

            x_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            x_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            logging.info(
                f"x_train shape: {x_train.shape}"
            )

            logging.info(
                f"y_train shape: {y_train.shape}"
            )

            logging.info(
                f"x_test shape: {x_test.shape}"
            )

            logging.info(
                f"y_test shape: {y_test.shape}"
            )

            # ========================================================
            # Train Model
            # ========================================================

            model_trainer_artifact = self.train_model(
                x_train=x_train,
                y_train=y_train,
                x_test=x_test,
                y_test=y_test,
            )

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
