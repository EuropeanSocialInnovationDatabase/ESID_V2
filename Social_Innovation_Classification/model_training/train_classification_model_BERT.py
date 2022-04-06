import json
import logging
import os
from argparse import ArgumentParser
from datetime import datetime

import numpy as np
import pandas as pd
import torch
from simpletransformers.classification import ClassificationModel

from data_collector.data_collector import DataCollector
from model_training.training_utils import return_df, print_result

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# use GPU for training or not
USE_CUDA = False
if torch.cuda.is_available():
    USE_CUDA = True

# model to use
MODEL_NAME = "bert-base-cased"

# model family
MODEL_TYPE = "bert"

# collapse model:
collapse_dict = {0: 0, 1: 1, 2: 2, 3: 3}

# format it to a string
timeStamp = datetime.now().strftime('%Y-%m-%d_%H-%M')

# where to save the models
MODEL_ROOT_PATH = 'models'

RUN_NAME = f'{MODEL_NAME}_{timeStamp}'
RUN_PATH = f'{MODEL_ROOT_PATH}/{RUN_NAME}'
RUN_conf_path = RUN_PATH + '/run_config.json'
os.makedirs(RUN_PATH, exist_ok=True)

# Dictionary to hold the exp information
RUN_DICT = {
    'COLLAPSE_DICT': collapse_dict,
    'MODEL_NAME': MODEL_NAME,
    'MODEL_TYPE': MODEL_TYPE,
    'TRAINING_ARGS': {},
    'TRAINING_PROJECT_IDS': {},
}

CRITERIONS = ['CriterionActors', 'CriterionInnovativeness', 'CriterionObjectives', 'CriterionOutputs']

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--topx", dest="topx", default=None,
                        help="top X files to select from the unlabeled projects")

    parser.add_argument("-d", "--dataset", dest="dataset", default=None,
                        help="A CSV to be used for training and testing")

    args = parser.parse_args()
    dataset_path = args.dataset

    # logging dir
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    log_path = f'logs/{RUN_NAME}/training_{timestamp}'
    os.makedirs(log_path, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_path, 'training_log.log'))
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f'The RUN NAME is: {RUN_NAME}')

    # Load the dataset
    logger.info('Loading the training set from the DB')
    data_collector = DataCollector()
    if dataset_path is None:
        dataset = data_collector.load_training_set(top_x=None)
        dataset.to_csv(fr'dataset/training_{RUN_NAME}_df.csv', index=False, encoding='utf-8')

        # shuffle the samples
        dataset = dataset.sample(n=len(dataset), random_state=42)
    else:
        dataset = pd.read_csv(dataset_path)

    # Start building a classifier for each criterion
    for CRITERION in CRITERIONS:

        logger.info(f'Training a classifier for {CRITERION}')
        # read three columns from the cvs file:
        sub_dataset = dataset[['Project_id', 'text', CRITERION]]

        # split dataframe to train and test 80/20.
        train_df, test_df = return_df(sub_dataset)
        logger.info(f'Split the dataset 80/20. Training length is {len(train_df)} and Testing length is {len(test_df)}')

        OUTPUT_MODEL_PATH = f'{RUN_PATH}/{CRITERION}/'
        BEST_MODEL_PATH = f'{RUN_PATH}/{CRITERION}/best_model/'

        # setup the training params (Do NOT change them)
        train_args = {
            # path where to save the model
            "output_dir": OUTPUT_MODEL_PATH,
            # path where to save the best model
            "best_model_dir": BEST_MODEL_PATH,
            # longest text processed (max bert)
            'max_seq_length': 512,  # 512
            'num_train_epochs': 25,  # 15
            'train_batch_size': 16,
            'eval_batch_size': 32,
            'gradient_accumulation_steps': 1,
            'learning_rate': 5e-5,
            'save_steps': 5000,

            'reprocess_input_data': True,
            "save_model_every_epoch": False,
            'overwrite_output_dir': True,
            'no_cache': True,

            'use_early_stopping': True,
            'early_stopping_patience': 3,
            'manual_seed': 42,
        }

        if USE_CUDA:
            train_args['n_gpu'] = 1
            train_args['use_multiprocessing'] = True
            train_args['fp16'] = True
        else:
            train_args['n_gpu'] = 0
            train_args['use_multiprocessing'] = False
            train_args['fp16'] = False

        RUN_DICT['TRAINING_ARGS'] = train_args
        RUN_DICT['TRAINING_PROJECT_IDS'] = train_df.Project_id.tolist()

        # Create a ClassificationModel
        model = ClassificationModel(MODEL_TYPE,
                                    MODEL_NAME,
                                    args=train_args,
                                    num_labels=len(set(train_df.labels.values.tolist())),
                                    use_cuda=USE_CUDA
                                    )

        logger.info(f'Start training a model for {CRITERION}')
        model.train_model(train_df, test_df)
        logger.info(f'Finish training a model for {CRITERION}')

        # Evaluate the model
        logger.info(f'Start evaluating the {CRITERION} model')
        result, model_outputs, wrong_predictions = model.eval_model(test_df)

        logger.info(f'Writing the result to dist')
        # evaluated the performance on the test set
        predictions = np.argmax(model_outputs, axis=1)
        metric_result = print_result(predictions, test_df.labels.values.tolist())
        RUN_DICT[f'model_metric_result_{CRITERION}'] = metric_result

        logger.info(f'Moving to the next classification model')

    # Saving the exp config to disk (applied only after training 4 classifiers)
    with open(RUN_conf_path, 'w') as outfile:
        json.dump(RUN_DICT, outfile, sort_keys=True, indent=4)

    logger.info('Finish training!!')
