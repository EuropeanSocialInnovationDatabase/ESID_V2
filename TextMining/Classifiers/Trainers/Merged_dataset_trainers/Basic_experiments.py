# -*- coding: utf-8 -*-

import MySQLdb
from os import listdir
from os.path import isfile, join
import io

import nltk
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.multiclass import OutputCodeClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.utils import resample
from database_access import *
import pickle
import os
from sklearn.model_selection import train_test_split
import numpy as np

#this function reads the file path. It takes an input parameter - path
def read_files(path):
    # this extracts the files from the path in path and joins path with f
    #listdir prints all the files and directories in path, and for each output, if the output (printed out by listdir) is
    #a file, then the os.join joins the path with the file name
    ann1files = [f for f in listdir(path) if isfile(join(path, f))]

    #create an empty list 'annotations'
    annotations = []

    #this is quite similar to the ANN_Experiments file, at this top section
    #iterate through the files in ann1files
    for ann in ann1files:
        #declare an empty string -content
        content = ""
        #if the string '.txt' exists in the iterable file - ann
        if ".txt" in ann:
            #set objective and the other criteria to -1
            objective = -1
            actors = -1
            outputs = -1
            innovativeness = -1
            si = -1
            #open the file at path concatenated with the filename at the iterable - ann, for reading
            f = open(path +'/'+ann,'r')
            # read the lines in the file using readlines and assign it to a list variable - lines
            lines = f.readlines()
            #iterate through the lines and concatenate each line to the string - content, which was declare above
            for line in lines:
                content = content + line
            #if ".txt.ann1" exists among the iterable files - ann, then jump back to outer loop; basically, ignore these
            #ones. There are some of those files in the folder, they seem to have a topic criteria as well, making them
            #different from the .ann files
            if ".txt.ann1" in ann:
                continue
            #open the file at path, concatenated with ann, where .txt is replaced with .ann, for reading. This seems
            #basically like reading the files of extension - .ann
            f = open(path + "/" + ann.replace('.txt','.ann'), "r")
            #read the lines in the file using readlines and assign it to a list variable - lines
            lines = f.readlines()
            #iterate through lines
            for line in lines:
                #if the string "Objectives" is found in the iterable - line
                if "Objectives:" in line:
                    #assign the value at index 1 on the line, splitting on ':', to have a list which allows this assignment
                    #cast into an int from string, and the end of line replaced with an empty string...maybe so as not to
                    #interfere
                    objective = int(line.split(':')[1].replace('\r\n',''))
                #the same is done for Actors and all the other criteria, if cound in the iterable -line
                if "Actors:" in line:
                    actors = int(line.split(':')[1].replace('\r\n',''))
                if "Outputs:" in line:
                    outputs = int(line.split(':')[1].replace('\r\n',''))
                if "Innovativenss:" in line:
                    innovativeness = int(line.split(':')[1].replace('\r\n',''))
                if "SI:" in line:
                    si = int(line.split(':')[1].replace('\r\n',''))
            #the following are appended to annotations - which was the empty list declared
            annotations.append([ann,content,objective,actors,outputs,innovativeness,si])
    #return the list annotations
    print (annotations[1]) #added by me to check the output of this function. RA- May 2021
    #print(annotations)
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
        #print (annotations2)

    annotations_kick = []


    new_sql = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like 'Manual_Kick%' LIMIT 2500"
    cursor.execute(new_sql)
    results3 = cursor.fetchall()

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
            #print (project_id,description,objectives,actors,output, innovativeness,si)
        if len(description) < 20:
            continue

        #while len(annotations_kick) < 2500:
        annotations_kick.append([project_id, description, objectives, actors, output, innovativeness, si])
        #print (annotations_kick)
        print("the length of annotations_kick is:" ,len(annotations_kick))

    #print (annotations2[-1])
    #while (len(annotations2)) < 5000:
    annotations2.extend(annotations_kick)
    #print (annotations2[-1])
    print ("length of annotations2 is: ", len(annotations2))

    print ("This code is running the current version")
    return annotations2

def dataframe_create(annotations,path):
    df = pd.DataFrame(annotations)
    df.columns = ["Project_id","Description","Objectives","Actors","Output","Innovativeness","SI"]
    print(df)
    df.to_csv(os.path.join(path, r'SIdataframe.csv'))

    #df.to_csv(r'../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2\pandas.txt', header=None, index=None, sep='\t', mode='a')


#This function transfers to database,and takes as a parameter - annotations
def transfer_to_database(annotations):
    #the database connection object is declared and the cursor as well
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    #iterate through annotations
    for ann in annotations:
        #take the value at index 0 of annotations, which seems to be the filename, replace the 'p_' with an empty string
        #and also replace the '.txt' with an empty string. Assign this to a variable - project. Having seen the files with
        #these names, this leaves the project number
        project = ann[0].replace('p_','').replace('.txt','')
        #encode this variable - project, in preparation for the database
        project = unicode(project,'utf-8')
        #declare a variable - project_id, and assign it the value - 0
        project_id = 0
        #if the value in the project variable is numeric, then,
        if project.isnumeric():
            #declare an sql select variable, to select all from the Projects table where the idProjects matches this
            #number - project
            sql = "SELECT * FROM EDSI.Projects where idProjects="+project
            #execute the query and assign the fetched results to variable - results
            cursor.execute(sql)
            results = cursor.fetchall()
            #iterate through results
            for res in results:
                #assign the value at index 0 of the fetched results to variable - project_id. This is the idProjects in the
                #ESID projects table
                project_id = res[0]
        #if project is not numeric,
        else:
            #declare an sql select variable which selects all from the ESID Projects table where the ProjectWebpage field
            #like the value in the project variable
            sql = "SELECT * FROM EDSI.Projects where ProjectWebpage like '%{0}%'".format(project)
            #execute the query and assign the fetched results to the variable - results
            cursor.execute(sql)
            results = cursor.fetchall()
            #iterate through results
            for res in results:
                #assign the value at index 0 in results to the variable project_id
                project_id = res[0]
        #if at the end the project_id is zero, meaning there was no matching one from the database, then jump to outer loop
        if project_id == 0:
            continue
        #Next, delcare an sql insert query and insert the following into the TypeOfSocialInnovation table, with the
        #SourceModel entered as "Manual Annotation"
        sql = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,Social_innovation_overall,SourceModel)" \
              "Values ({0},{1},{2},{3},{4},{5},'{6}')".format(ann[4],ann[2],ann[3],ann[5],project_id,ann[6],"ManualAnnotation")
        #execute the query and commit to the database and close the database
        cursor.execute(sql)
        db.commit()
    db.close()

#this function loads the description from the database
def load_database_description_dataset():
    #declare the database connection variable and the cursor
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    #declare an sql select statment to select all from the TypeofSocialInnovation table in the database
    sql = "Select * FROM TypeOfSocialInnotation"
    cursor.execute(sql)
    #execute the query, fetch all results and assign them to the variable - results
    results = cursor.fetchall()
    #declare an empty list 'annotations'
    annotations = []
    #iterate through the results from the sql select query
    for res in results:
        #assign the value at index 1 to output, index 2 to objectives, and for all the others, do the same. This is based
        #on index 1 being CriterionOutputs in the database table, and same for the rest
        output = res[1]
        objectives = res[2]
        actors = res[3]
        innovativeness = res[4]
        si = res[6]
        #at index 5, is the Projects_idProjects, and this is assigned to the project_id variable
        project_id = res[5]
        #declare another sql select query - new_sql, which selects all from the AdditionalProjectData table, where the
        #FieldName is like -%Desc%, and the Projects_idProjects matches the project_id, from the previous query
        new_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(project_id)
        #execute the query and assign the results to the results2 variable
        cursor.execute(new_sql)
        results2 = cursor.fetchall()
        #declare an empty string - description
        description = ""
        #iterate through the results of the query
        for res2 in results2:
            #concatenate the values at index 2 of the results2 variable, which is basically 'Value' in the table in the
            #database, and is the description text. Concatenate all for that particular project_id to one string and assign
            #to description
            description = description + " " +res2[2]
        #if the length of description after this is less than 20, jump back to outer loop
        if len(description)<20:
            continue
        #append a list containing the values below to the annotations list declared earlier
        annotations.append([project_id,description,objectives,actors,output,innovativeness,si])
    #return annotations
    return annotations

#declare class - UniversalClassifier
class UniversalClassifier():
    #declare these variables within the initialisation function for the class. These appear to be the features
    def __init__(self):
        self.confusion_matrix = confusion_matrix([0, 0],[0, 0])
        self.obj = ['aim','objective','goal','vision','strive']
        self.targets = ['poor','refugees','unpriviledged','black','gay','LGBT','trans','aging']
        self.inprove = ['inprove','improve','better','greater','quality','cutting edge']
        self.things = ['language','food','money','health','care','social','insurance','legal']
        self.new = ['new','novel']
        self.things2 = ['method','model','product','service','application','technology','practice']
        self.things3 = ['software','tool','framework','book']
        self.new_tech = ['machine learning','artificial intelligence','3d print','bitcoin','blockchain','cryptocurrency','nano']
        self.actor = ['organisation','university','users','ngo','firm','company','actors','people']

    #declare a function in the class- train_RF_words_only, and pass it the parameters below...the training data
    def train_RF_words_only(self,X_train,y_train):
        #declare the count_vect1 variable
        self.count_vect1 = CountVectorizer(max_features=2000000,ngram_range=(1,3))#ngram_range from 1,4 by Roseline 09/12/20
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        #set number of classifiers
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        self.clf.fit(X_train_tf, y_train)
        # self.clf =SVC()

    #declare a train_cost_sensitive_RF_words_only model that takes X_train and y_train
    def train_cost_sensitive_RF_words_only(self,X_train,y_train):
        #declare a variable -stopWords that takes the english stopwords
        stopWords = set(nltk.corpus.stopwords.words('english'))
        #whas was originally here is four grams...set count_vect1 to this, and pass in the stopwords to be taken out
        #self.count_vect1 = CountVectorizer(max_features=2000000,ngram_range=(1,4),stop_words=stopWords,lowercase=True)
        self.count_vect1 = CountVectorizer(max_features=2000000, ngram_range=(1, 4), stop_words=stopWords,
                                           lowercase=True)#roseline trying trigram 09/12/20
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        #n_jobs is the number of processors that the classifier should use, here set to '3'. Also, random_state is not
        #set here, as is for the RF_words_only that is not cost_sensitive
        self.clf = RandomForestClassifier(n_jobs=3, n_estimators=200)
        #self.clf = MultinomialNB()
        #self.clf = SVC()
        #self.clf = DecisionTreeClassifier(max_depth=6)
        self.clf.fit(X_train_tf, y_train)

    #this function saves the Random Forest model
    def save_RF_words_only(self,path):
        #check if the path does not exist, and creates the directories
        if not os.path.exists(path):
            os.makedirs(path)
        #the pickle is then dumped in that path, with filename as below, which was opened for writing
        #the tf_transformer is also dumped, as well as the classifier itself - clf
        pickle.dump(self.count_vect1, open(path+"/count_vectorizer.pck", 'wb'))
        pickle.dump(self.tf_transformer, open(path + "/tf_transformer.pck", 'wb'))
        pickle.dump(self.clf, open(path + "/classifier.pck", 'wb'))

    #this function loads the model. It takes in path as a parameter. It opens the model files that were saved, for
    # reading and returns self
    def load_RF_words_only(self,path):
        self.count_vect1 = pickle.load(open(path+"/count_vectorizer.pck", 'rb'), encoding='latin1')
        self.tf_transformer = pickle.load(open(path + "/tf_transformer.pck", 'rb'), encoding='latin1')
        self.clf = pickle.load(open(path + "/classifier.pck", 'rb'), encoding='latin1')
        return self

    #declare train_RF_features_only function and pass in X_train and y_train
    def train_RF_features_only(self,X_train,y_train):
        #declare an empty list train_vector
        train_vector = []
        #iterate through X_train which was passed into the function above
        for x in X_train:
            #implement the case lower function on the iterable, and assign the lowered case to variable - xa
            xa = x.lower()
            #initialize these varaibles to 0; they are based on the features declared in the UniversalClassifer above
            has_obj = 0
            has_target = 0
            has_improve = 0
            has_things = 0
            has_new = 0
            has_things2 = 0
            has_things3 = 0
            has_new_tech = 0
            has_actor = 0
            #start a for loop that checks if a feature is in the set of features in the UniversalClassifier feature
            # set. This goes through each feature in each feature set, here, self.obj
            for o in self.obj:
                #check if the feature in question is in xa, the iterable of X_train
                if o in xa:
                    #if it is, then assign 1 to the has_obj variable, which was initilaised above
                    has_obj = 1
            #check here, for every feature in the feature set self.targets
            for o in self.targets:
                #if one of those is in the X_train iterable, then assign 1 to has_target
                if o in xa:
                    has_target =1
            #check here for every feature in the feature set self.inprove
            for o in self.inprove:
                #if one of those is in the X_train iterable, then assign 1 to has_improve
                if o in xa:
                    has_improve = 1
            #do the same for all the other features and feature sets
            for o in self.things:
                if o in xa:
                    has_things = 1
            for o in self.new:
                if o in xa:
                    has_new = 1
            for o in self.things2:
                if o in xa:
                    has_things2 = 1
            for o in self.things3:
                if o in xa:
                    has_things3 = 1
            for o in self.new_tech:
                if o in xa:
                    has_new_tech =1
            for o in self.actor:
                if o in xa:
                    has_actor =1
            train_vector.append([has_obj,has_target,has_improve,has_things,has_things2,has_things3,has_new,has_new_tech,has_actor])
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        self.clf.fit(train_vector, y_train)




    def predict_features_only(self,X_test):
        train_vector = []
        for x in X_test:
            xa = x.lower()
            has_obj = 0
            has_target = 0
            has_improve = 0
            has_things = 0
            has_new = 0
            has_things2 = 0
            has_things3 = 0
            has_new_tech = 0
            for o in self.obj:
                if o in x:
                    has_obj = 1
            for o in self.targets:
                if o in xa:
                    has_target = 1
            for o in self.inprove:
                if o in xa:
                    has_improve = 1
            for o in self.things:
                if o in xa:
                    has_things = 1
            for o in self.new:
                if o in xa:
                    has_new = 1
            for o in self.things2:
                if o in xa:
                    has_things2 = 1
            for o in self.things3:
                if o in xa:
                    has_things3 = 1
            for o in self.new_tech:
                if o in xa:
                    has_new_tech = 1
            for o in self.actor:
                if o in xa:
                    has_actor =1
            #append these scores to the list train_vector, as a list. This builds train_vector as a list
            train_vector.append([has_obj, has_target, has_improve, has_things, has_things2,has_things3, has_new, has_new_tech,has_actor])
        #call the predict function on train_vector, which is a vector of the features, and assign the return value
        #to y_pred
        y_pred = self.clf.predict(train_vector)
        return y_pred

    #declare the train_NB_words_only function and pass in X_train and y_train as parameters. This is the NB model section
    def train_NB_words_only(self, X_train, y_train):
        print("Running NB") #added as a function check - RA- 09/05/21
        #declare the count_vect here, and the X_train_counts, and the rest.
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        #the NB function is called here and assigned to self.clf and the model is fitted below. I need to learn more
        #on how to implement this model
        self.clf = MultinomialNB()
        self.clf.fit(X_train_tf, y_train)

    #declare a function train_SVM_words_only and pass in X_train and y_train as parameters. This function implements
    #the SVM classifier
    def train_SVM_words_only(self, X_train, y_train):
        print("Running SVM")#added as a function run check
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        #the svm model is fitted here
        self.clf = SVC() #original line. Trying something different below - RA 03_06_21
        #self.clf = OutputCodeClassifier(LinearSVC(random_state=0),
                            #code_size=2, random_state=0)
        self.clf.fit(X_train_tf, y_train)
        # self.clf.fit(features2, y)
        #print("Trained")

    #declare the predict_words_only function and pass in X_test as a parameter. This function performs the prediction
    #for words only and returns y_pred, the prediction
    def predict_words_only(self,X_test):
        X_new_counts = self.count_vect1.transform(X_test)
        X_test_tf = self.tf_transformer.transform(X_new_counts)
        y_pred = self.clf.predict(X_test_tf)
        return y_pred


    #declare the print_reports function and pass in the two parameters -y_pred and y_test
    def print_reports(self,y_pred,y_test):
        #this function is used to print your confusion matrix and the classification report as well
        print(sklearn.metrics.classification_report(y_pred, y_test))
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test,labels = [1,0])
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        print(new_confusion_matrix)
        # Accuracy score
        print('accuracy is', accuracy_score(y_pred, y_test))


    #declare a print_final_report function
    def print_final_report(self):
        #print out the confusion matrix
        print("Overall confusion matrix:")
        print(self.confusion_matrix)
        #set the variables for overall true positives, negatives, false positives and negatives and initialise them
        overall_TP = 0.0
        overall_FP = 0.0
        overall_FN = 0.0
        #declare precision, recall and F1score as variables and assign them a two-value list initialised at 0
        precision = [0,0]
        recall = [0,0]
        F1score = [0,0]
        try:  # I added this try here and the if below, and moved the for to correspond - 07/05/21
            if self.confusion_matrix != 0:
        #check for i in range 0,len(precision)
                for i in range(0,len(precision)):
            #set variable true_pos which adds 0.0 to the entry at confusion_matrix[i][i], while false_pos and false_neg
            #are initialised to 0.0
                    true_pos = 0.0+self.confusion_matrix[i][i]
                    false_pos = 0.0
                    false_neg = 0.0
            #for the inner loop, for j in the range 0,len(precision), if j==i, then jump back to outer loop
                    for j in range(0,len(precision)):
                        if j == i:
                            continue
                #calculate false_neg as false_neg, which was initialised to 0.0, plus the confusion_matrix[i][j]
                        false_neg = false_neg + self.confusion_matrix[i][j]

                #calculate false_pos here as well
                    for j in range(0,len(precision)):
                        if j == i:
                            continue
                        false_pos = false_pos + self.confusion_matrix[j][i]
            #add the true_pos to overall_TP and assign it to the overall_TP variable. Do the same for overall_FP and
            #overall_FN
        #I added this exception below - Roseline-07/05/21
        except:  # I also added the except below
            print("Size error")
            overall_TP = overall_TP + true_pos
            overall_FP = overall_FP + false_pos
            overall_FN = overall_FN + false_neg
            #if true_pos + false_pos is not equal to 0,then:
            if (true_pos+false_pos)!=0:
                #precision[i], which is the first element in the precision list is calculated as below
                precision[i] = true_pos/(true_pos+false_pos)
            #but if true_pos == 0 and true_pos+false_pos == 0, then precision [i] = 1.0
            if true_pos ==0 and (true_pos+false_pos)==0:
                precision[i] = 1.0
            #if true_pos + false_neg is not equal to 0, then
            if (true_pos + false_neg) != 0:
                #calculate recall thus:
                recall[i] = true_pos/(true_pos+false_neg)
            #if the true_pos==0 and true_pos+false_neg is also 0, then recall is set to 1.0
            if true_pos ==0 and (true_pos+false_neg)==0:
                recall[i] = 1.0
            #if precision[i] + recall[i] is greater than 0, then F1score[i] is calculated as below
            if precision[i]+recall[i] >0:
                F1score[i] = 2*precision[i]*recall[i]/(precision[i]+recall[i])
            #otherwise, F1score[i] is set to 0
            else:
                F1score[i] = 0.0
            #print out the precision, recall and F1score, round to 2 decimal places
            print(str(i)+"\t\t"+str(round(precision[i],2))+"\t\t\t"+str(round(recall[i],2))+"\t\t"+str(round(F1score[i],2)))
        #print out the overall_precision,overall_recall and overall_F1score as below, round to 2 decimal places
        overall_precision = overall_TP/(overall_FP+overall_TP)
        overall_recall = overall_TP/(overall_TP+overall_FN)
        overall_F1score = 2*overall_precision*overall_recall/(overall_precision+overall_recall)
        #actual statement directly below. Testing with another statement (last one) - RA 07/05/21
        #print("Overall\t"+str(round(overall_precision,2))+"\t\t\t"+str(round(overall_recall,2))+"\t\t"+str(round(overall_F1score,2)))
        print("Overall\t"+str(overall_precision)+"\t\t\t"+str(overall_recall)+"\t\t"+str(overall_F1score))



#the main program starts here
if  __name__ == '__main__':
    #the path is set to this folder path. This is the path that is passed into the functions above. This folder however
    #appears to contain zeroes for all the criteria. On the other hand, the folder in the same place
    #Output/Merged_dataset_all_workshops does contain some .ann files where the criteria are not all zero.
    #path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshops"
    #path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2" #original path-RA 26/05/21
    #path = "../../../../Helpers/SI_dataset/Output/Merged_dataset_all_workshop_with_excluded2"
    #path = "../../../../Helpers/SI_dataset/Output/SI_withExcluded3"
    #path = "../../../../Helpers/SI_dataset/Output/SI_only_balanced"
    path = "../../../../Helpers/SI_dataset/Output/SI_only"

    #path is passed in as a parameter to the read_files functions and the return value is assigned to variable - anno-
    #tations. This is what is returned - ([ann,content,objective,actors,outputs,innovativeness,si])
    #annotations = read_files(path)#original code by Nikola - RA_28_05_21
    annotations = create_new_trainingset1()
    print("Working on annot now")
    dataframe_create(annotations,path)
    #annot = create_new_trainingset1()
    #annotations = load_database_description_dataset()
    #transfer_to_database(annotations)
    #exit(1)
    #decalre these two empty lists
    texts = []
    classA = []
    ### Working on Objectives
    print("Working on Objectives")

    #start working on Objectives
    #iterate through the returned list above - annotations
    for anns in annotations:
        #append the value at index 1 of the iterable to the texts list. This is the 'content', as seen above
        texts.append(anns[1])
        #appeand the value at index 2 to value, this is the value for -objective
        value = anns[2]
        #check if the value is larger than 2, and if so, then assign it the value - 1
        if value>=1: #making a change from value >=2 to value >= 1, to see if there's a change. RA 01/06/21
            value = 1
        #else, then assign 0 as its value. This means where 'objective' is 0 or 1, then assign it 0
        else:
            value =0
        #at the end, assign whatever value it is, 0 or 1, to the classA list
        classA.append(value)
    #create a dataframe of texts and classA, with the column - 'text' for texts AND column 'classa' for classA
    df = pd.DataFrame({'text': texts, 'classa': classA})
    #implement the value counts function on the classa column to get the unique counts of the 0s and 1s, and print out
    #the result
    print(df.classa.value_counts())
    #the train_test_split function of sklearn is applied on the dataframe and the test_size is set at 0.2 proportion of
    #the dataset. The splits are assigned back to train_df and test_df accordingly
    train_df, test_df = train_test_split(df, test_size=0.2)
    #print out the unique count of the values in the train_df by applying the value_counts function on the classa column
    #also print out same for the test df. Accompanied by the strings - "Train DF and Test DF
    print("Train DF:\n"+str(train_df.classa.value_counts()))
    print("Test DF:\n" + str(test_df.classa.value_counts()))
    #here, the rows of the dataframe are shuffled and frac=1 shows the proportion to return, in this case, the full
    #dataframes. This is done for both train_df and text_df
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                   replace=True,     # sample with replacement
    #                                   n_samples=420,    # to match majority class
    #                                   random_state=83293) # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled],ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled


    #implement the model_selection function of sklearn with KFold set to 5. This means 5 folds with 4 as training and 1
    #for validation
    folder = sklearn.model_selection.KFold(5)
    scores = [] #added to test the cross validation implementation
    #declare a varaible i
    i = 0
    #use this format, which is the sklearn format, to split the train_df
    for train_index,test_index in folder.split(train_df):
        #increment i and print out the fold number as "FOLD" concatenated with i
        i = i +1
        print("FOLD:"+str(i))
        #declare an instance of the UniversalClassifier class
        cls = UniversalClassifier()
        #declare variable X_train and assign it the value at the train_index position or data subset, of train_df['text']
        X_train = train_df['text'][train_index]
        #declare variable X_train and assign it the value at the train_index position or data subset, of train_df['text']
        y_train = train_df['classa'][train_index]
        #call the train_cost_sensitive_RF_words_only function of the UniversalClassifier class, using the cls object and
        #pass in the X_train and y_train parameters
        #==========================
        cls.train_SVM_words_only(X_train,y_train)
        #cls.train_NB_words_only(X_train,y_train) # test line added -06/05/21
        #cls.train_cost_sensitive_RF_words_only(X_train,y_train) # correct line that was here
        #==============================


        #declare variable X_test and assign it the value at the test_index position or data subset, of train_df['text']
        #do same with variable y_test, but with train_df['classa']
        X_test= train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        #declare variable - y_pred and assign it the return value of implementing the predict_words_only function of the
        #UniversalClassifier class on parameter -X_test
        y_pred = cls.predict_words_only(X_test)
        #call the print_reports function and pass it the y_pred and y_test as parameters
        cls.print_reports(y_pred, y_test)
        #the above happens for the five folds
    #declare an instance o the UniversalClassifier class here again.
    cls = UniversalClassifier()
    #X_train here is set to the value at the train_df['text'], so not the train_index as in the folds above
    X_train = train_df['text']
    #set y_train to the ['classa'] column of train_df
    y_train = train_df['classa']
    #call the train_cost_sensitive_RF_words_only function of the UniversalClassifier, and pass it the X_train and y_train
    #as parameters. That function fits the RandomForest classifier

    #==============Test Section==============
    cls.train_SVM_words_only(X_train,y_train)
    #cls.train_NB_words_only(X_train, y_train) # test line
    #cls.train_cost_sensitive_RF_words_only(X_train, y_train) # actual correct line
    #=======================

    #call the save_RF_words_only function and pass in a string "Objectives_RF" which basically will be a folder/directory
    #name where the fitted model is saved to
    cls.save_RF_words_only("Objectives_RF")
    #call the predict_words_only model and pass in the test_df['text'] for the model to use the fitted model and predict
    #the scores for the text in the test set. Assign the returned value to y_pred...y-predictions
    y_pred = cls.predict_words_only(test_df['text'])
    #call the print_reports function of the Universal Classifier and pass in the returned y_pred and the test_df['classa']
    #to print out the confusion matrix and classification report
    cls.print_reports(y_pred, test_df['classa'])
    #print the below to show the end of the implementation

    print("End of Objectives")

    #repeat the same process as above for the Actors classification, using ofcourse the anns[3] from the annotations list
    #as that was the value for the Actors
    ### Actors
    print("Working on Actors")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[3]
        if value>=1: #making a change from value >=2 to value >= 1, to see if there's a change. RA 01/06/21
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    # print("Train DF:\n" + str(train_df.classa.value_counts()))
    # print("Test DF:\n" + str(test_df.classa.value_counts()))
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=350,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]

        #====added a different model here for testing ============---the original line -06/05/21
        #cls.train_NB_words_only(X_train, y_train)
        cls.train_SVM_words_only(X_train, y_train)
        #cls.train_cost_sensitive_RF_words_only(X_train, y_train) #---the original line -06/05/21
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_words_only(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']

    # ====added a different model here for testing ============---the original line -06/05/21
    #cls.train_NB_words_only(X_train, y_train)
    cls.train_SVM_words_only(X_train, y_train)
    #cls.train_cost_sensitive_RF_words_only(X_train, y_train)#original line - 06/05/21
    cls.save_RF_words_only("Actors_RF")
    y_pred = cls.predict_words_only(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Actors")

    #Carry out the same process for Outputs, and Innovativeness, etc
    ### Outputs
    print("Working on Outputs")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[4]
        if value>=1: #making a change from value >=2 to value >= 1, to see if there's a change. RA 01/06/21
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)



    # print("Train DF:\n" + str(train_df.classa.value_counts()))
    # print("Test DF:\n" + str(test_df.classa.value_counts()))
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=400,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]

        # ====added a different model here for testing ============---the original line -06/05/21
        #cls.train_NB_words_only(X_train, y_train)
        cls.train_SVM_words_only(X_train, y_train)
        #cls.train_cost_sensitive_RF_words_only(X_train, y_train) #- original line - 06/05/21
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_words_only(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']

    # ====added a different model here for testing ============---the original line -06/05/21
    #cls.train_NB_words_only(X_train, y_train)
    cls.train_SVM_words_only(X_train, y_train)
    #cls.train_cost_sensitive_RF_words_only(X_train, y_train)#--original line here 06/05/21
    cls.save_RF_words_only("Outputs_RF")
    y_pred = cls.predict_words_only(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Outputs")

    ### Innovativeness
    print("Working on Innovativness")
    texts = []
    classA = []
    for anns in annotations:
        texts.append(anns[1])
        value = anns[5]
        if value>=1: #making a change from value >=2 to value >= 1, to see if there's a change. RA 01/06/21
            value = 1
        else:
            value =0
        classA.append(value)
    df = pd.DataFrame({'text': texts, 'classa': classA})
    print(df.classa.value_counts())
    train_df, test_df = train_test_split(df, test_size=0.2)
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)


    # print("Train DF:\n" + str(train_df.classa.value_counts()))
    # print("Test DF:\n" + str(test_df.classa.value_counts()))
    #
    # df_majority = train_df[train_df.classa == 1]
    # df_minority = train_df[train_df.classa == 0]
    # df_minority_upsampled = resample(df_minority,
    #                                  replace=True,  # sample with replacement
    #                                  n_samples=400,  # to match majority class
    #                                  random_state=83293)  # reproducible results
    #
    # df_upsampled = pd.concat([df_majority, df_minority_upsampled], ignore_index=True)
    # df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    # print(df_upsampled.classa.value_counts())
    # train_df = df_upsampled



    folder = sklearn.model_selection.KFold(5)
    i = 0
    for train_index, test_index in folder.split(train_df):
        i = i + 1
        print("FOLD:" + str(i))
        cls = UniversalClassifier()
        X_train = train_df['text'][train_index]
        y_train = train_df['classa'][train_index]

        # ====added a different model here for testing ============
        #cls.train_NB_words_only(X_train, y_train)
        cls.train_SVM_words_only(X_train, y_train)
        #cls.train_cost_sensitive_RF_words_only(X_train, y_train) #---original line here - 06/05/21
        X_test = train_df['text'][test_index]
        y_test = train_df['classa'][test_index]
        y_pred = cls.predict_words_only(X_test)
        cls.print_reports(y_pred, y_test)
    cls = UniversalClassifier()
    X_train = train_df['text']
    y_train = train_df['classa']

    # ====added a different model here for testing ============
    #cls.train_NB_words_only(X_train, y_train)
    cls.train_SVM_words_only(X_train, y_train)
    #cls.train_cost_sensitive_RF_words_only(X_train, y_train)#---original line here - 06/05/21
    cls.save_RF_words_only("Innovativeness_RF")
    y_pred = cls.predict_words_only(test_df['text'])
    cls.print_reports(y_pred, test_df['classa'])
    print("End of Innovativeness")


    #Working on SI classifier

    

#cls.print_final_report() #added cls. here to check if it works

##What basically happens in this code is that the annotation files are used with the text to train the models for all
# the criteria. The models are then built and stored. The models built are tested to see their prediction precision,
# recall and F1Score.In the Apply models program, the built models from Basic_experiments are called and the
# description from the AdditionalProjects table and the text on the project from MongoDB is fed to the model and the
# model, which was built and tested is ran on this data and the predicted scores are entered into the
# TypesofSocialInnovation table in the database, as well as the version of the model and the date, as well as the
# accompanying message.
#It also transfers the annotations from the annotation files to the database, and indicates the sourcemodel as
#Manual. It also has a function that loads the database description dataset to annotations. This was not
# called here.

