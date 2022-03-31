from ANN_Experiments import UniversalNNClassifier,read_files
import pandas as pd
from sklearn.utils import resample


#this ANN_training code imports the UniversalNNClassifier class from ANN_Experiments.py, and also the
# read_files function
#Line below necessary as we are importing from another file.
if  __name__ == '__main__':
    #the path where the files are is declared as below. This folder contains. The files contained are the ann files
    #and the txt files. The ann files just contain the annotation scores, and have the same name as the file, but different
    #extensions
    #..the files in this folder appear to all have 0s for the criteria. I'll have to confirm which are the actual
    #annotations Nikol used - RA -26/04/21
    #Merged_dataset_all_workshop does have different entries for the categories, than 0s.
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded"
    # path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2"
    # path = "../../../../Helpers/SI_dataset/Output/SI_withExcluded3"
    # path = "../../../../Helpers/SI_dataset/Output/SI_only_balanced"
    # path = "../../../../Helpers/SI_dataset/Output/SI_only"

    #Call the read_files function and pass in the path above. Assign the return to the variable - annotations
    #What is returned is - [ann,content,objective,actors,outputs,innovativeness,si]
    annotations = read_files(path)
    # annotations = load_database_description_dataset()
    # transfer_to_database(annotations)
    # exit(1)

    #declare these empty lists- texts and classA
    texts = []
    classA = []
    ### Working on Objectives
    print("Working on Objectives")

    #iterate through annotations
    for anns in annotations:
        #append the contents to texts
        #assign the objective to value and if >=2, assign 1, and 0 for less than 2.
        texts.append(anns[1])
        value = anns[2]
        if value >= 2:
            value = 1
        else:
            value = 0
        #append value, which is 1 or 0 to the classA list
        classA.append(value)
    #convert these two lists to a dataframe with two columns, text and classa
    df = pd.DataFrame({'text': texts, 'classa': classA})
    #print out the count of the unique entries of classa...that is, how many 1s and 0s
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=530,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled

    #declare an object of the UniversalNNClassifier class
    cls = UniversalNNClassifier()
    #set varaible X_train to a dataframe containing text only
    X_train = df['text']
    #set a variable y_train to a dataframe containing classa only
    y_train = df['classa']

    #call the train_CNN_words_only function of the UniversalNNClassifier class, and pass in X_train and y_train
    #this trains the model
    cls.train_CNN_words_only(X_train, y_train)
    #save the trained model by calling the save_CNN_model and passing in the string "Objectives_NN"
    #This creates a directory -Objectives_NN and saves the tokenizer-pickle dump, json and the weights
    cls.save_CNN_model("Objectives_NN")

    #the same as the above is also done for the actors, using the actors score and the model saved in Actors_NN
    ### Actors
    print("Working on Actors")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[3]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=440,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Actors_NN")

   #the same is done for Outputs and the model saved in Outputs_NN
    ### Outputs
    print("Working on Outputs")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[4]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=510,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Outputs_NN")

    #the same is done for innovativeness, and the model saved in Innovativeness_NN
    ### Innovativeness
    print("Working on Innovativness")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[5]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    # df_majority = df[df.classa == 1]
    # df_minority = df[df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=510,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Innovativeness_NN")

    #I added this for the SI calssification, which is not here. RA - 28/05/21.
    #To run this, I will have to set the path to : - path = "../../../../Helpers/SI_dataset/Output/SI_only"

    print("Working on SI")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[6]
        if value >= 2:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    df_majority = df[df.classa == 1]
    df_minority = df[df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                      replace=True,  # sample with replacement
                                      n_samples=80,  # to match majority class
                                      random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    df = df_upsampled
    cls = UniversalNNClassifier()
    X_train = df['text']
    y_train = df['classa']

    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("SI_NN")

    ##this training looks a lot similar to ANN_Experiments, except for the non upsampling and no predictions and
    #a few other things. It seems like a subset of that code