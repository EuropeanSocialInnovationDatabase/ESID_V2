import MySQLdb
from os import listdir
from os.path import isfile, join
import pandas as pd
import sklearn
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.layers import Embedding, Conv1D, MaxPooling1D, Dropout, Flatten, Dense, Activation, LSTM
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from sklearn.utils import resample

from database_access import *
from keras.models import model_from_json
from sklearn.model_selection import KFold
from keras import metrics
from sklearn.model_selection import train_test_split
import numpy as np
import os
import pickle


#this function reads the file path. It takes an input parameter - path
def read_files(path):
    #this extracts the files from the path in path and joins path with f
    ann1files = [f for f in listdir(path) if isfile(join(path, f))]
    #create an empty list called annotations
    annotations = []

    #iterate through ann1files
    for ann in ann1files:
        #create an empty string -content
        content = ""
        #if the iterable is a text file, as it has the extension - .txt
        if ".txt" in ann:
            #set these variables to the value of -1
            objective = -1
            actors = -1
            outputs = -1
            innovativeness = -1
            si = -1 #this was added by me to ensure this runs. - RA 10/05/21
            #open the file, for reading, at the location path/ann - this ann is also part of the path.It's a path too.
            # Assign it to #a variable - f
            f = open(path +'/'+ann,'r')
            #read the lines in the file using readlines and assigns it to a list variable - lines
            lines = f.readlines()
            #iterate through lines - which is basically a list of each line from the text file - ann
            for line in lines:
                #concatenate the line to the empty string - content. So, content will now contain all the lines from the
                #text file.
                content = content + line
            #open again the file at location path concatenated with ann, as above, but this time, replace 'txt' with 'ann'
            #open the file for reading. ann files maybe come as .txt.
            f = open(path + "/" + ann.replace('.txt','.ann'), "r")
            #read the lines of the file in f using readlines, and assign it to the variable -lines.
            lines = f.readlines()
            #iterate through lines
            for line in lines:
                #if the string "Objectives:" is in line
                if "Objectives:" in line:
                    #set the varaible objective's value to the value in index [1] when line has been split on :, and end
                    #line or new line character (\r\n) has been replaced with an empty string, hence, -maybe rather than
                    #the line ending, it's a space and another line continues it, so it's one long string.Typecast into an
                    #integer
                    #line.split splits the line by the stated seperator, into a list with elements seperated by the seperator
                    objective = int(line.split(':')[1].replace('\r\n',''))
                #if the string Actors: is in the line, then
                if "Actors:" in line:
                    #set variable actors as with objectives above. Do same for Outputs, innovativeness and si
                    actors = int(line.split(':')[1].replace('\r\n',''))
                if "Outputs:" in line:
                    outputs = int(line.split(':')[1].replace('\r\n',''))
                if "Innovativenss:" in line:
                    innovativeness = int(line.split(':')[1].replace('\r\n',''))
                if "SI:" in line:
                    si = int(line.split(':')[1].replace('\r\n',''))
            #append ann-which was the file's path, I guess, the content, and the scores of all the criteria to the
            # empty list- annotations which was created above
            annotations.append([ann,content,objective,actors,outputs,innovativeness,si])
    #return the list annotations
    return annotations

def create_new_trainingset1():
    annotations2 = []

    db = MySQLdb.connect(host, username, password, database, charset = 'utf8')
    cursor = db.cursor()

    sql = "SELECT *  FROM EDSI.TypeOfSocialInnotation where (SourceModel like '%Manual%' AND \
          (Projects_idProjects not in (Select distinct(Projects_idProjects) from EDSI.TypeOfSocialInnotation where \
          SourceModel like '%v14%')) or SourceModel like '%v14%') and Projects_idProjects in \
          (SELECT Projects_idProjects FROM EDSI.Projects, EDSI.TypeOfSocialInnotation where KNOWMAK_ready = 1 AND \
          idProjects = Projects_idProjects)"
    cursor.execute(sql)
    results = cursor.fetchall()
    for res in results:
        output = res[1]
        objectives = res[2]
        actors = res[3]
        innovativeness =res[4]
        si = res[6]
        project_id = res[5]

        sql2 = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(project_id)
                #(SELECT Projects_idProjects FROM EDSI.Projects, EDSI.TypeOfSocialInnotation where KNOWMAK_ready = 1
                #AND idProjects = Projects_idProjects)"
        cursor.execute(sql2)
        description = ""
        results2 = cursor.fetchall()
        for res2 in results2:
            description = description + " " + res2[2]
        if len(description)<20:
            continue
        annotations2.append([project_id, description, objectives, actors, output, innovativeness, si])
        print("length of annotations2 is: " + str(len(annotations2)))

    new_sql = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like 'Manual_Kick%'"
    cursor.execute(new_sql)
    results3 = cursor.fetchall()
    annotations_kick =[]
    for res3 in results3:
        output = res3[1]
        objectives = res3[2]
        actors = res3[3]
        innovativeness = res3[4]
        si = res3[6]
        project_id = res3[5]

        new_sql2 = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and \
        Projects_idProjects="+str(project_id)
        cursor.execute(new_sql2)
        description = ""
        results4 = cursor.fetchall()
        for res4 in results4:
            description = description + " " + res4[2]
        if len(description) < 20:
            continue
        i = 0
        while len(annotations_kick) < 2500:
            annotations_kick.append([project_id, description, objectives, actors, output, innovativeness, si])
            i += 1
            annotations2.append(annotations_kick[0])
            print("length of annotations_kick is:" + str(len(annotations_kick)))

    print("length of annotations2 after annotations_kick:" + str(len(annotations2)))
    #print (annotations2)
    #print (annotations2[4162])
    return annotations2

#this function transfers the annotations to the database. It receives as a parameter the annotations from the read_files
#function
def transfer_to_database(annotations):
    #set a database connector variable - db
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    #set a database cursor variable
    cursor = db.cursor()
    #iterate through the annotations passed into the function
    for ann in annotations:
        #set a variable -project to the element in index 0 of the present iterable, with the string 'p_' of the element
        #replaced with an empty string and the .txt extension also replaced with an empty string
        project = ann[0].replace('p_','').replace('.txt','')
        #implement some unicode encoding or decoding of the variable project, and assign the encoded or decoded value to
        #the variable prject, again.
        project = unicode(project,'utf-8')
        #create a variable -project_id and assign it 0
        project_id = 0
        #check the variable project's value is numeric, and if so,
        if project.isnumeric():
            #set and implement an sql select query to select all from the Projects table in the database, where idProjects
            #matches the value of project above, so basically, select all projects with the project_id equal to project above
            #***confirm this later - why +project?
            sql = "SELECT * FROM EDSI.Projects where idProjects="+project
            #execute the query and fetchall results into a results variable
            cursor.execute(sql)
            results = cursor.fetchall()
            #iterate through results
            for res in results:
                #set the project_id variable to the value at index 0 of the present iterable
                project_id = res[0]
        #if project is numeric returns false,
        else:
            #implement an sql select query to select all from projects the projects table where the ProjectWebpage is like
            #project- the variable from above
            sql = "SELECT * FROM EDSI.Projects where ProjectWebpage like '%{0}%'".format(project)
            #execute the sql query
            cursor.execute(sql)
            #fetchall results from the query into a results variable
            results = cursor.fetchall()
            #iterate through results
            for res in results:
                #set the value at index 0 of the present iterable from results to the project_id variable
                project_id = res[0]
        #if project_id turns out to be equal to 0, then continue to the next iteration. That is, if the project_id is not
        #available, I guess
        if project_id == 0:
            continue
        #implement the sql insert query and insert into the TypeofSocialInnovation table in the database the element at
        #index 4 of ann to CriterionOutputs, index 2 to CriterionObjectives, etc, and project_id under
        #Projects_idProject, and then SourceModel as "ManualAnnotation". Recall ann is from the annotations list passed in
        #from the read files function
        sql = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,Social_innovation_overall,SourceModel)" \
              "Values ({0},{1},{2},{3},{4},{5},'{6}')".format(ann[4],ann[2],ann[3],ann[5],project_id,ann[6],"ManualAnnotation")
        #execute the insert query and commit the results, then close the connection
        cursor.execute(sql)
        db.commit()
    db.close()

#this function loads the database description dataset
def load_database_description_dataset():
    #implement the database connection
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    #Implement a select query to select all from the TypesofSocialInnovation table, fetch all the results and store them
    #in the results variable
    sql = "Select * FROM TypeOfSocialInnotation"
    cursor.execute(sql)
    results = cursor.fetchall()
    #create an empty list-annotations
    annotations = []
    #iterate through the results variable, and for each iterable, save the value at index 1 of the fetched results to
    #variable -output, index 2 to objectives and so on. Note these correspond to the CriterionOutputs, CriterionObjectives
    #and so on, in the TypeOfSocialInnovation table
    for res in results:
        output = res[1]
        objectives = res[2]
        actors = res[3]
        innovativeness = res[4]
        si = res[6]
        #also set the value at index 5 to variable -project_id. This is the Projects_idProjects column in TypeOfSocial
        #Innovation
        project_id = res[5]
        #implement another sql select query to select all from the AdditionalProjectData table where the fieldname is like
        #Desc, and the Project_idProjects matches the project_id, converted to string to allow for comparision with the
        #database results. This basically selects the descriptions. Assign these to variable - results2
        new_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(project_id)
        cursor.execute(new_sql)
        results2 = cursor.fetchall()
        #create an empty string variable -description
        description = ""
        #iterate through results2
        for res2 in results2:
            #concatenate the value at res2[2], which is basically the Description text from the database,
            #to the variable description.
            description = description + " " +res2[2]
        #if the length of the description variable is less than 20,continue, meaning, move to the next iteration
        if len(description)<20:
            continue
        #append the project_id, description, objectives, actors, output, innovativeness and si to the annotations list
        #created above
        annotations.append([project_id,description,objectives,actors,output,innovativeness,si])
        #return that annotations list
    return annotations

#create a class here of UniversalNNclassifier
class UniversalNNClassifier():
    #this is the constructor function for this class for neural networks
    #the Glove_dir file looks like a file of vectors
    def __init__(self):
        os.environ['PYTHONHASHSEED'] = '4'
        np.random.seed(523)
        self.max_words = 200000
        self.batch_size = 16
        self.epochs = 100
        self.GLOVE_DIR = "../../../../Helpers/BratDataProcessing/Glove_dir"
        self.MAX_SEQUENCE_LENGTH = 1100
        self.EMBEDDING_DIM = 200
        pass

    #this function is the CNN train function in the UniversalCNN class; takes in X_train and Y_train
    def train_CNN_words_only(self,X_train,y_train):
        embeddings_index = {}
        self.tokenizer = Tokenizer(num_words=self.max_words)
        self.tokenizer.fit_on_texts(X_train)
        sequences = self.tokenizer.texts_to_sequences(X_train)

        word_index = self.tokenizer.word_index
        #it takes the glove.6B.200d.txt file and saves it to variable - f
        f = open(os.path.join(self.GLOVE_DIR, 'glove.6B.200d.txt'))
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        #iterate through the lines in f
        for line in f:
            #values here is assigned line.split, which basically splits the line into a list with each word as an element
            values = line.split()
            #assign the value at index 0 to variable word
            word = values[0]
            #values from index 1 to the end are fed into the np array as coefficients. Recall that the glove file is like
            #a file with vectors per line, first element is a wor, and the rest of the line floats
            coefs = np.asarray(values[1:], dtype='float32')
            #embedding_index of the iterable word is assigned the coefs the line above
            embeddings_index[word] = coefs
        #close the file
        f.close()

        #then print found word vectorsand continue with the rest of the neural nets stuff
        print('Found %s word vectors.' % len(embeddings_index))
        embedding_matrix = np.zeros((len(word_index) + 1, self.EMBEDDING_DIM))
        for word, i in word_index.items():
            embedding_vector = embeddings_index.get(word)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
        embedding_layer = Embedding(len(word_index) + 1,
                                    self.EMBEDDING_DIM,
                                    weights=[embedding_matrix],
                                    input_length=self.MAX_SEQUENCE_LENGTH,
                                    trainable=False)
        Total_TP = 0
        Total_FP = 0
        Total_FN = 0


        early_stopping = EarlyStopping(monitor='val_loss', patience=5)
        y_train = to_categorical(y_train)
        model = None
        model = Sequential()
        model.add(embedding_layer)
        model.add(Conv1D(2048, 5, activation='relu'))
        model.add(MaxPooling1D(20))
        model.add(Dropout(0.2))
        model.add(Conv1D(512, 5, activation='relu'))
        model.add(MaxPooling1D(10))
        model.add(Dropout(0.2))
        model.add(Flatten())
        model.add(Dense(20,activation='relu'))
        model.add(Dense(2))
        model.add(Activation('sigmoid'))

        model.compile(loss='binary_crossentropy',
                          optimizer='nadam',
                          metrics=['accuracy','mean_squared_error', 'mean_absolute_error', 'mean_absolute_percentage_error', 'cosine_proximity'])

        history = model.fit(data, y_train,
                                batch_size=self.batch_size,
                                epochs=self.epochs,
                                verbose=0,
                                validation_split=0.1,
                                callbacks=[early_stopping]
                                )
        #model assigned to self.clf
        self.clf = model

    #this function saves the CNN model. It takes the path variable as a parameter. This function is called below
    #the strings passed in as will be seen are - "Objectives_RF", "Actors_RF", etc.
    def save_CNN_model(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        #dumps the pickle- basically the algorithm stuff in  file along the path, with tokenizr.pck appended. The file
        #is opened for writing the pickle into
        pickle.dump(self.tokenizer, open(path + "/tokenizer.pck", 'wb'))
        #the model is also converted to json here and written into a json file -model_actors.json, opened for writing
        #still along the path
        model_json = self.clf.to_json()
        with open(path+"/model_actors.json", "w") as json_file:
            #after the file is opened, the json_file - model_json is written in
            json_file.write(model_json)
        # serialize weights to HDF5
        #the weights are saved in a file model_actors.h5 along the path
        self.clf.save_weights(path+"/model_actors.h5")

    #the function loads the CNN model, from the json file
    def load_CNN_model(self,path):
        #declare a file read variable json_sign and assign theopen the json file for reading
        json_file = open(path+"/model_actors.json", 'r')
        #read the json file contents into variable- loaded_model_json
        loaded_model_json = json_file.read()
        #load the pickle file from tokenizer.pck into the variable-self.tokenizer
        self.tokenizer = pickle.load(open(path + "/tokenizer.pck", 'rb'))
        #close the json file
        json_file.close()

        #use model_from_json, which is a keras model function which parses a JSON model configuration string and return a
        #model instance. This model instance is assigned to the self.clf variable
        self.clf = model_from_json(loaded_model_json)
        # load weights into new model
        self.clf.load_weights(path+"/model_actors.h5")
        return self


    #this is the CNN predict function, that takes a parameter the X_test variable, basically the test set
    def predict_CNN(self,X_test):
        #it performs the predictions here. I'll have to study this to get it
        #the texts in X_test are converted to sequences here and assigned to the variable - sequences
        sequences = self.tokenizer.texts_to_sequences(X_test)
        data = pad_sequences(sequences, maxlen=self.MAX_SEQUENCE_LENGTH)
        y_pred = self.clf.predict(data)
        #creates an empty list - y_binary
        y_binary = []
        #iterates through the predictions on the data
        for y in y_pred:
            #if the element at index 0 of the predicitons is less than 0.5, it appends 1 to the y_binary list
            if y[0] < 0.5:
                y_binary.append(1)
            #else, it appends 0
            else:
                y_binary.append(0)
        #the y_binary list is returned
        return y_binary

    #call the print_reports function and give it the y_pred and y_test variables as parameters
    def print_reports(self,y_pred,y_test):
        #print out the classification report, an sklearn class fucntion which takes parameters -y_pred and y_test
        print(sklearn.metrics.classification_report(y_pred, y_test))
        #create the confusion matrix here using the sklearn .metrics confusion_matrix function, which takes in y_pred
        #and y_test
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test)
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        #print out the confusion_matrix
        print(new_confusion_matrix)



#this is ofcourse the main fuction here, that is implemented by this code. if __name__ == '__main__' required because
#we are calling a number of other classes into this code
if  __name__ == '__main__':
    #this is where the path variable which has been called into functions above, is declared and assigned.
    #need to check out this data at the Merged_dataset_all_workshop_with_excluded
    path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded"# the correct path -RA_28_05_21
    #path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2"
    #path = "../../../../Helpers/SI_dataset/Output/SI_withExcluded3"
    #path = "../../../../Helpers/SI_dataset/Output/SI_only_balanced"
    #path = "../../../../Helpers/SI_dataset/Output/SI_only"

    #annotations variable here takes the output from the read_files function which takes path as a parameter
    #annotations = read_files(path) #original line in code. RA 01_06_21
    annotations = create_new_trainingset1()
    print("Working on annot now")
    #annotations = load_database_description_dataset()
    #transfer_to_database(annotations)
    #exit(1)
    #declare two empty lists here -texts and classA
    texts = []
    classA = []
    #print out working on Objectives here to show the objectives are being worked on now
    ### Working on Objectives
    print("Working on Objectives")

    #iterate through annotations. Recall, the read_files function returns -
    # annotations.append([ann,content,objective,actors,outputs,innovativeness,si]) the list annotations with these
    for anns in annotations:
        #content, which is at index 1 is appended to the texts list created above
        texts.append(anns[1])
        #objective, which is at index 2 is appended to the value variable. Recall, we are working on objectives here
        value = anns[2]
        #if the value, that is the score of objectives is greater than 2, then assign as value - '1'
        if value>=1:
            value = 1
        #else, meaning, if it's 0 or 1, then assign as value - '0'
        else:
            value =0
        #append the value to the list - classA
        classA.append(value)
    #write out a dataframe, using Panda with the texts under the text column, and classA under the classa column
    df = pd.DataFrame({'text': texts, 'classa': classA})
    #calll the value_counts fucntion of dataframes, which counts the unique values, on df and print out the result of
    #that count. This willcount how many 1s are there and how many 0s. Recall it is called on the classa column
    print(df.classa.value_counts())
    #pass the df into the train_test_split fucntion of sklearn, which splits arrays and matrices into random train and
    #test subsets, here the test_size, which is the proportion to be used as the test set is 0.2. The output  of this
    # call is assigned to train_df and test_df, two dataframe
    train_df, test_df = train_test_split(df, test_size=0.2)
    #then call the value_counts function of dataframes on the train_df classa column, to print the count of unique values
    #basically the counts of 0s and 1s. Do the same for the test dataframe
    print("Train DF:\n"+str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    #then sample the train_df to return a random sample of items from an axis of object, set fraction of axis items to
    #return as 1, and also reset the index and Do not try to insert index into dataframe columns.
    # This resets the index to the default integer index.Note, if frac was set to 0.5, that would be a random 50% of the
    #sample that would be used. I guess this just randomly samples train_df and same is done for test_df. Uses the full
    #sample as is, that's why frac = 1. Frac =0.5 would be half of sample, and frac = 2 would upsample
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)

    #....I will have to investigate this upsampling more closely...
    #create a dataframe - df_majority, which takes the entries of train_df where classa = 1
    df_majority = train_df[train_df.classa == 1]
    #create a dataframe df_minority, whose entries are those of train_df where classa = 0
    df_minority = train_df[train_df.classa == 0]
    #create a df_minority_upsampled dataframe which basically holds the resampled df_minority, which has been sampled
    #with replacement (replace=True), samples set to 420 (as stated below, its to match the majority class), n (here
    #n_samples) is the number of random elements to extract. random_state is set to ensure reproducibility. This
    #creates an upsample of df_minority, ofcourse
    df_minority_upsampled = resample(df_minority,
                                      replace=True,     # sample with replacement
                                      n_samples=420,    # to match majority class
                                      random_state=83293) # reproducible results

    #create a dataframe -df_upsampled, by concatenating df_majority with df_minority_upsampled, ignore index
    df_upsampled = pd.concat([df_majority, df_minority_upsampled],ignore_index=True)
    #then sample df_upsampled as explained previously, and assign the result to df_upsampled
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    #call value_counts() on df_upsampled to get the count of its unique values and print out the result
    print(df_upsampled.classa.value_counts())
    #assign df_upsampled to train_df.
    #I guess what was done here was to balance out the number of 0s and 1s in the dataframe, to create a balanced dataset?
    train_df = df_upsampled


    #start calculation of the cross validation of the model. KFold is used here to obtain a leave one out CV
    #here, the data is split into 5 folds,and these are assigned to a variable-folder. Four folds will be used for
    #training and one fold for testing
    folder = sklearn.model_selection.KFold(5)
    #set a variable i to 0
    i = 0
    #carry out the split of the training dataframe - train_df, iterate through the splits of the train_df. For
    #test_index and train_index in train_df,
    for test_index,train_index in folder.split(train_df):
        #increment i here
        i = i +1
        #print out what fold it is, preceeded by the word- 'fold' and concatenate the fold number - i
        print("FOLD:"+str(i))
        #declare an instance of the Universalclassifier class here - cls
        cls = UniversalNNClassifier()
        #declare variable X_train and assign it the entry at index ['text'][train_index] of the train_df. So it seems
        #the text at that train_index, which is basically a location... same for below
        X_train = train_df['text'][train_index]
        #declare varaible y_train and assign it the entry at index ['classa'][train_index]
        y_train = train_df['classa'][train_index]
        #call the function train_CNN_words_only with the UniversalNNClassifier object and pass in X_train and
        #y_train as parameters to the function. This does the training of that fold, and builds the model
        cls.train_CNN_words_only(X_train,y_train)
        #set variable X_test and y_test, and assign to X_test the entry at train_df['text'][test_index], so basically
        #the text at that position. Do same for y_test, but for the classa column
        X_test= train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        #declare variable - y_pred and assign it the returned value from calling the predict_CNN function on X_test
        y_pred = cls.predict_CNN(X_test)
        #call the print_reports function and give it the parameters - y_pred (the returned prediction) and y_test
        #this function, which is above in this code, prints out the confusion matrix for the fold
        cls.print_reports(y_pred, y_test)
    # declare an instance of the Universalclassifier class here - cls. Outside the for loop of the folds
    cls = UniversalNNClassifier()
    #set variable X_train to the value at train_df['text'], basically, the contents of the annotation file
    X_train = train_df['text']
    #set y_train to train_df['classa'], which is the score values we had above, 0 or 1.
    #a bit confusing here...as it seems this is done without the folds, but taking the full sample
    y_train = train_df['classa']
    #call the train_CNN_words_only function here, and pass it X_train and y_train. This basically builds the model on
    #the training data
    cls.train_CNN_words_only(X_train, y_train)
    #call the save_CNN_model function and pass it a string - "Objectives_RF", to show the objectives were considered
    #here. This string is passed in as the path for that function, and that function dumps the pickles, and weights
    #etc for the model. Hence to find the objectives model, it'll be with "Objectives_RF" in its path
    cls.save_CNN_model("Objectives_RF")
    #declare a variable - y_pred here and assign it the return value from calling the predict_CNN function on the text
    #in the test_df. Recall test_df up there which is 0.2 of the full sample
    y_pred = cls.predict_CNN(test_df['text'])
    #call the print_reports function here, and pass it the two parameters - y_pred and test_df['classa']. This function
    #takes the prediction and the test set and prints out the confusion matrix
    cls.print_reports(y_pred, test_df['classa'])
    #complete the objectives classification
    print("End of Objectives")
    #in summary, the classification and models are built on the training set which is 0.8 of the sample, but also, a
    #K-folds validation is done on the training set only. But it seems the training and test is done again on the
    #full set. Not clear why the cross validation was not done on the full data and if the model benefitted from it.
    #Might be something to improve in the model


    #repeat the same process above for the Actors classification
    ### Actors
    print("Working on Actors")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[3]
        if value>=1:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))

    df_majority = train_df[train_df.classa == 1]
    df_minority = train_df[train_df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                     replace=True,  # sample with replacement
                                     n_samples=350,  # to match majority class
                                     random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalNNClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_CNN_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_CNN(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalNNClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Actors_RF")
    y_pred = cls.predict_CNN(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Actors")

    #Repeat the same as above for the Outputs
    ### Outputs
    print("Working on Outputs")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[4]
        if value>=1:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))

    df_majority = train_df[train_df.classa == 1]
    df_minority = train_df[train_df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                     replace=True,  # sample with replacement
                                     n_samples=400,  # to match majority class
                                     random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalNNClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_CNN_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_CNN(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalNNClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Outputs_RF")
    y_pred = cls.predict_CNN(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Outputs")

    #Repeat the same above for Innovativeness
    ### Innovativeness
    print("Working on Innovativness")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[5]
        if value>=1:
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)


    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))

    df_majority = train_df[train_df.classa == 1]
    df_minority = train_df[train_df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                     replace=True,  # sample with replacement
                                     n_samples=400,  # to match majority class
                                     random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalNNClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_CNN_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_CNN(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalNNClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("Innovativeness_RF")
    y_pred = cls.predict_CNN(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Innovativeness")

##Adding this here for the SI classification.
#When running it, I will have to change the path to : path = "../../../../Helpers/SI_dataset/Output/SI_only"

    print("Working on SI")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[6]
        if value is not None and value >= 1:
            value = 1
        else:
            value = 0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)

    print("Train DF:\n" + str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))

    df_majority = train_df[train_df.classa == 1]
    df_minority = train_df[train_df.classa == 0]
    df_minority_upsampled = resample(df_minority,
                                     replace=True,  # sample with replacement
                                     n_samples=80,  # to match majority class
                                     random_state=83293)  # reproducible results

    df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    print(df_upsampled.classa.value_counts())
    train_df = df_upsampled

    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalNNClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]
        cls.train_CNN_words_only(X_train, y_train)
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_CNN(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalNNClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']
    cls.train_CNN_words_only(X_train, y_train)
    cls.save_CNN_model("SI_RF")
    y_pred = cls.predict_CNN(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of SI")


