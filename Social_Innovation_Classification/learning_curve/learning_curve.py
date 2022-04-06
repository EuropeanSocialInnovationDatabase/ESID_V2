import math
import os
import shutil
from argparse import ArgumentParser
from datetime import datetime

import torch
from simpletransformers.classification import ClassificationModel
from sklearn.model_selection import train_test_split

from data_collector.data_collector import DataCollector
from model_training.training_utils import print_result

os.environ["TOKENIZERS_PARALLELISM"] = "false"

si_criteria = ['CriterionActors', 'CriterionInnovativeness', 'CriterionObjectives', 'CriterionOutputs']
timeStamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
# model to use
MODEL_NAME = "bert-base-cased"

# model family
MODEL_TYPE = "bert"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-s", "--step_size", dest="step_size", default=50, help="Training dataset step size")

    parser.add_argument("-r", "--dataset_ids", dest="dataset_ids_path",
                        help="Path to a text/CSV file contains training project IDs", default='')

    args = parser.parse_args()
    step_size = int(args.step_size)
    dataset_ids_path = args.dataset_ids_path

    data_collector = DataCollector()

    if os.path.exists(dataset_ids_path):
        with open(dataset_ids_path) as rdr:
            dataset_ids = [x.strip() for x in rdr.readlines()]
    else:
        dataset_ids = None

    #import pandas as pd
    # dataset = pd.read_csv('dataset/trainingset.csv')
    dataset = data_collector.load_training_set(project_ids=dataset_ids)
    dataset = dataset.sample(n=len(dataset), random_state=42)

    if len(dataset) < 1:
        raise ValueError('The training set project IDs are invalid.')

    training_set, testing_set = train_test_split(dataset, test_size=0.2)

    for CRITERION in si_criteria:
        print(f'Start building the LR for {CRITERION}')

        lc_tmp_path = f'learning_curve/lc_tmp_path/{CRITERION}/'
        if not os.path.exists(lc_tmp_path):
            os.makedirs(lc_tmp_path)

        # use GPU for training or not
        USE_CUDA = False
        if torch.cuda.is_available():
            USE_CUDA = True

        train_args = {
            # path where to save the model
            "output_dir": lc_tmp_path,
            # path where to save the best model
            "best_model_dir": lc_tmp_path,
            # longest text processed (max bert)
            'max_seq_length': 512,  # 512
            'num_train_epochs': 5,  # 5
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

        training_set_ctr = training_set[['Project_id', 'text', CRITERION]]
        testing_set_ctr = testing_set[['Project_id', 'text', CRITERION]]

        training_set_ctr.columns = ['Project_id', "text", "labels"]
        testing_set_ctr.columns = ['Project_id', "text", "labels"]

        training_set_ctr['text'] = training_set_ctr['text'].replace(r"\n", " ", regex=True)
        testing_set_ctr['text'] = testing_set_ctr['text'].replace(r"\n", " ", regex=True)

        training_set_ctr['labels'] = training_set_ctr['labels'].astype(int)
        testing_set_ctr['labels'] = testing_set_ctr['labels'].astype(int)

        learning_curve_data = {}
        # Iterate over the dataset
        for subset_size in range(1, int(math.ceil(len(training_set_ctr) / step_size) + 1)):
            training_subset = training_set_ctr.iloc[0:subset_size * step_size]
            print('training_subset: ', len(training_subset))
            if len(set(training_subset.labels.values.tolist())) < 3:
                print('Escape, the subset has to have samples from all the classes')
                continue

            # Create a ClassificationModel
            clf_model = ClassificationModel(MODEL_TYPE,
                                            MODEL_NAME,
                                            num_labels=len(set(training_subset.labels.values.tolist())),
                                            args=train_args,
                                            use_cuda=USE_CUDA
                                            )

            clf_model.train_model(training_subset, show_running_loss=False, verbose=False)

            # Evaluate the model
            predictions, _ = clf_model.predict(testing_set_ctr.text.tolist())

            metric_result = print_result(predictions, testing_set_ctr.labels.values.tolist())
            learning_curve_data[str(len(training_subset))] = metric_result

        # Saving the result
        with open(f'learning_curve/lr_{CRITERION}_{timeStamp}.csv', 'w')as wrt:
            line = f"Training Size\tMacro F1\tMacro Recall\tMacro Precision\n"
            wrt.write(line)
            for size, res in learning_curve_data.items():
                line = f"{size}\t{res['macro F1']}\t{res['macro recall']}\t{res['macro precision']}\n"
                wrt.write(line)

        if os.path.exists(lc_tmp_path):
            shutil.rmtree(lc_tmp_path)

        print(f'Finish building the LR for {CRITERION}')
