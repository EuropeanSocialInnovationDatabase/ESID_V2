import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score, recall_score, precision_score


def collapse_me(collapse_dict, x):
    """
    collapse classes of the dataset
    """
    return collapse_dict[x]


def print_result(y, y_pred, fn=None):
    """
    function to print results
    """

    result = {
        'macro F1': f1_score(y, y_pred, average='macro'),
        'macro recall': recall_score(y, y_pred, average='macro'),
        'macro precision': precision_score(y, y_pred, average='macro'),
        'micro F1': f1_score(y, y_pred, average='micro'),
        'micro recall': recall_score(y, y_pred, average='micro'),
        'micro precision': precision_score(y, y_pred, average='micro'),
        'accuracy': metrics.accuracy_score(y, y_pred)
    }

    print(confusion_matrix(y, y_pred))
    print(classification_report(y, y_pred))
    return result
    #
    # if fn is not None:
    #     with open(fn, 'w') as wrt:
    #         wrt.write('macro F1 is:' + str(f1_score(y, y_pred, average='macro')))
    #         wrt.write('\n')
    #         wrt.write('macro recall is:' + str(recall_score(y, y_pred, average='macro')))
    #         wrt.write('\n')
    #         wrt.write('macro precision is:' + str(precision_score(y, y_pred, average='macro')))
    #         wrt.write('\n')
    #         wrt.write(str(confusion_matrix(y, y_pred)))
    #         wrt.write('\n')
    #         wrt.write('accuracy' + str(metrics.accuracy_score(y, y_pred)))


def return_df(df):
    """
    function to split dataframe into training/testing (80/20)
    :param df: dataframe to split
    :return: training and testing dataframes. Each has two columns: text/ labels
    """
    np.random.seed(42)
    msk = np.random.rand(len(df)) < 0.8
    train_df = df[msk]
    train_df = train_df.sample(frac=1)
    train_df.columns = ['Project_id', "text", "labels"]
    eval_df = df[~msk]
    eval_df.columns = ['Project_id', "text", "labels"]
    train_df = pd.DataFrame(
        {
            "Project_id": train_df['Project_id'],
            "text": train_df['text'].replace(r"\n", " ", regex=True),
            "labels": train_df['labels'].astype(int)
        }
    )

    eval_df = pd.DataFrame(
        {
            "Project_id": eval_df['Project_id'],
            "text": eval_df['text'].replace(r"\n", " ", regex=True),
            "labels": eval_df['labels'].astype(int)
        }
    )

    train_df = train_df[train_df['text'].notna()]
    eval_df = eval_df[eval_df['text'].notna()]

    return train_df, eval_df
