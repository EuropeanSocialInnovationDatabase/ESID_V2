import logging
import os
import sys
from argparse import ArgumentParser
from datetime import datetime

import pandas as pd
from simpletransformers.classification import ClassificationModel

from data_collector.data_collector import DataCollector
from utils import clean_text

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# where to save the models
MODEL_ROOT_PATH = 'models'
prediction_path = 'prediction'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')


class ProjectsClassifier:
    """
    Class to load the four classifiers and predict the projects
    """

    def __init__(self, run_name):
        self.MODEL_TYPE = "bert"

        use_cuda = False
        # set the model's path
        actor_model_path = f'{MODEL_ROOT_PATH}/{run_name}/CriterionActors/'
        output_model_path = f'{MODEL_ROOT_PATH}/{run_name}/CriterionOutputs/'
        innov_model_path = f'{MODEL_ROOT_PATH}/{run_name}/CriterionInnovativeness/'
        obj_model_path = f'{MODEL_ROOT_PATH}/{run_name}/CriterionObjectives/'
        if not os.path.exists(actor_model_path) or \
                not os.path.exists(output_model_path) or \
                not os.path.exists(innov_model_path) or \
                not os.path.exists(obj_model_path):
            print(f'Invalid run name "{run_name}"')
            sys.exit()

        n_gpu = 0 if use_cuda else 1
        eval_batch_size = 1
        use_multiprocessing = False

        # Loading BERT classification models. ( we will use ONLY CPU for prediction).
        # GPU is faster but it's not available in your server
        self.actor_clf_model = ClassificationModel(self.MODEL_TYPE, actor_model_path, use_cuda=use_cuda)
        self.actor_clf_model.args.n_gpu = n_gpu
        self.actor_clf_model.args.eval_batch_size = eval_batch_size
        self.actor_clf_model.args.use_multiprocessing = use_multiprocessing
        self.actor_clf_model.args.use_multiprocessing_for_evaluation = False

        self.output_clf_model = ClassificationModel(self.MODEL_TYPE, output_model_path, use_cuda=use_cuda)
        self.output_clf_model.args.n_gpu = n_gpu
        self.output_clf_model.args.eval_batch_size = eval_batch_size
        self.output_clf_model.args.use_multiprocessing = use_multiprocessing
        self.output_clf_model.args.use_multiprocessing_for_evaluation = False

        self.innov_clf_model = ClassificationModel(self.MODEL_TYPE, innov_model_path, use_cuda=use_cuda)
        self.innov_clf_model.args.n_gpu = n_gpu
        self.innov_clf_model.args.eval_batch_size = eval_batch_size
        self.innov_clf_model.args.use_multiprocessing = use_multiprocessing
        self.innov_clf_model.args.use_multiprocessing_for_evaluation = False

        self.obj_clf_model = ClassificationModel(self.MODEL_TYPE, obj_model_path, use_cuda=use_cuda)
        self.obj_clf_model.args.n_gpu = n_gpu
        self.obj_clf_model.args.eval_batch_size = eval_batch_size
        self.obj_clf_model.args.use_multiprocessing = use_multiprocessing
        self.obj_clf_model.args.use_multiprocessing_for_evaluation = False

    def predict_samples(self, df, run_name, model_name):
        """
        function to predict the 4 criteria for each project on the testing dataframe
        """

        # load the testing project's text
        list_of_text = df.text.values.tolist()

        # clean the project's text
        text = [clean_text(x) for x in list_of_text]

        # load the testing project's IDs
        project_ids = df.Project_id.values.tolist()

        print('Start prediction')
        # for each classifier, we call "predict" method given the text of the project.
        # the predict method returns the predicted class and the prediction
        # probability/ confidence score ( we are not using it here)
        all_actor_pred, all_output_pred, all_innov_pred, all_obj_pred = [], [], [], []
        for sample_text in text:
            if sample_text:
                actor_pred, _ = self.actor_clf_model.predict([sample_text])
                actor_pred = actor_pred[0]

                output_pred, _ = self.output_clf_model.predict([sample_text])
                output_pred = output_pred[0]

                innov_pred, _ = self.innov_clf_model.predict([sample_text])
                innov_pred = innov_pred[0]

                obj_pred, _ = self.obj_clf_model.predict([sample_text])
                obj_pred = obj_pred[0]

            else:
                actor_pred = output_pred = innov_pred = obj_pred = -1

            all_actor_pred.append(actor_pred)
            all_output_pred.append(output_pred)
            all_innov_pred.append(innov_pred)
            all_obj_pred.append(obj_pred)

        print('Finish prediction')

        # saving the predictions into a list of dictionaries. Each dict has 5 keys, as shown below.
        result = [{
            "Project_id": i,
            "CriterionActors": x,
            "CriterionInnovativeness": z,
            "CriterionObjectives": w,
            "CriterionOutputs": y,
            'Social_Innovation_overall': '-1',
            'AnnSource': 'MACHINE',
            'ModelName': model_name,
            'expName': run_name
        }
            for i, x, y, z, w in zip(
                project_ids,
                all_actor_pred,
                all_output_pred,
                all_innov_pred,
                all_obj_pred
            )
        ]
        return pd.DataFrame(result)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--run_name", dest="run_name",
                        help="Classification model path")
    parser.add_argument("-p", "--projects", dest="project_ids_path",
                        help="Path to a CSV contains project IDs", default=None)
    parser.add_argument("-d", "--dataset", dest="dataset", default=None,
                        help="A CSV to be used for training and testing")

    args = parser.parse_args()
    RUN_NAME = args.run_name
    project_ids_path = args.project_ids_path
    dataset_path = args.dataset

    if not RUN_NAME:
        raise ValueError("Missing experiment configuration file")

    if project_ids_path:
        with open(project_ids_path) as rdr:
            project_ids = [x.strip() for x in rdr.readlines()]
    else:
        project_ids = []

    # logging dir
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    log_path = f'logs/{RUN_NAME}/exp_{timestamp}'
    os.makedirs(log_path, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_path, 'projects_prediction_log.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f'The RUN NAME is: {RUN_NAME}')

    # Prediction dir
    os.makedirs(prediction_path, exist_ok=True)

    # Class to collect/ push data to the DB
    logger.info('Loading the Data Collector model')
    data_collector = DataCollector()

    # BERT Classifiers class
    logger.info('Loading the Classification model')
    si_classifier = ProjectsClassifier(RUN_NAME)

    if dataset_path and os.path.exists(dataset_path):
        testing_df = pd.read_csv(dataset_path)
    else:
        testing_df = data_collector.load_testing_set(project_ids=project_ids)
        testing_df.to_csv(fr'dataset/prediction_{timestamp}.csv', index=False, encoding='utf-8')

    if len(testing_df) == 0:
        logger.info(f'No new projects were found. Please add the IDs of the new projects to the esid_prediction table.')
    else:
        # Predict the samples
        # sample with empty text will be predicted with -1
        logger.info(f'Start predicting samples')

        df_prediction = si_classifier.predict_samples(testing_df,
                                                      run_name=RUN_NAME,
                                                      model_name=si_classifier.MODEL_TYPE.upper())
        logger.info(f'Finish predicting samples')

        # Save the prediction the the dataset folder with the run name
        logger.info(f'Saving the predictions to a file: ' + f'dataset/{RUN_NAME}/prediction.csv')
        df_prediction.to_csv(os.path.join(prediction_path, f'prediction_{RUN_NAME}.csv'), index=False, encoding='utf-8')

        # Insert the result into the esid_predictions table
        # if a project already predicted, it will updated. Otherwise, inserted.
        logger.info(f'Inserting the predictions into the database')
        p_insert_ctr, p_update_ctr, p_failed = data_collector.insert_predictions(df_prediction)

        logger.info(f'{p_insert_ctr} projects has been inserted')
        logger.info(f'{p_update_ctr} projects has been updated')
        logger.info(f'{p_failed} projects failed')

        logger.info(f'Closing, bye!!')
        sys.exit(0)
