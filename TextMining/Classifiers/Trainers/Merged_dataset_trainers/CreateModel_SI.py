import MySQLdb
from os import listdir
from os.path import isfile, join

import nltk
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.svm import SVC
from sklearn.utils import resample
from database_access import *
import pickle
import os

#this code prepares the SI model, to fit the SI data. It is very similar to the Basic_experiments code, except
#that it only trains the SI models, and not all the other criteria, like actors, objectives, outputs and innova-
#tiveness

#this read_files function works the same as in the other code
def read_files(path):
    ann1files = [f for f in listdir(path) if isfile(join(path, f))]

    annotations = []

    for ann in ann1files:
        content = ""
        if ".txt" in ann:
            objective = -1
            actors = -1
            outputs = -1
            innovativeness = -1
            f = open(path +'/'+ann,'r')
            lines = f.readlines()
            for line in lines:
                content = content + line
            f = open(path + "/" + ann.replace('.txt','.ann'), "r")
            lines = f.readlines()
            for line in lines:
                if "Objectives:" in line:
                    objective = int(line.split(':')[1].replace('\r\n',''))
                if "Actors:" in line:
                    actors = int(line.split(':')[1].replace('\r\n',''))
                if "Outputs:" in line:
                    outputs = int(line.split(':')[1].replace('\r\n',''))
                if "Innovativenss:" in line:
                    innovativeness = int(line.split(':')[1].replace('\r\n',''))
                if "SI:" in line:
                    si = int(line.split(':')[1].replace('\r\n',''))
            annotations.append([ann,content,objective,actors,outputs,innovativeness,si])
    return annotations

#this function is also the same as that in Basic_experiments.py
def transfer_to_database(annotations):
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    for ann in annotations:
        project = ann[0].replace('p_','').replace('.txt','')
        project = unicode(project,'utf-8')
        project_id = 0
        if project.isnumeric():
            sql = "SELECT * FROM EDSI.Projects where idProjects="+project
            cursor.execute(sql)
            results = cursor.fetchall()
            for res in results:
                project_id = res[0]
        else:
            sql = "SELECT * FROM EDSI.Projects where ProjectWebpage like '%{0}%'".format(project)
            cursor.execute(sql)
            results = cursor.fetchall()
            for res in results:
                project_id = res[0]
        if project_id == 0:
            continue
        sql = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,Social_innovation_overall,SourceModel)" \
              "Values ({0},{1},{2},{3},{4},{5},'{6}')".format(ann[4],ann[2],ann[3],ann[5],project_id,ann[6],"ManualAnnotation")
        cursor.execute(sql)
        db.commit()
    db.close()

#this function also works the same as it does in the other code - Basic_experiments.py
def load_database_description_dataset():
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    sql = "Select * FROM TypeOfSocialInnotation"
    cursor.execute(sql)
    results = cursor.fetchall()
    annotations = []
    for res in results:
        output = res[1]
        objectives = res[2]
        actors = res[3]
        innovativeness = res[4]
        si = res[6]
        project_id = res[5]
        new_sql = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%Desc%' and Projects_idProjects="+str(project_id)
        cursor.execute(new_sql)
        results2 = cursor.fetchall()
        description = ""
        for res2 in results2:
            description = description + " " +res2[2]
        if len(description)<20:
            continue
        annotations.append([project_id,description,objectives,actors,output,innovativeness,si])
    return annotations

#this UniversalClassifier class is also the same as that in Basic_experiments.py
class UniversalClassifier():
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

    def train_RF_words_only(self,X_train,y_train):
        self.count_vect1 = CountVectorizer(max_features=1000,ngram_range=(1,3))
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = RandomForestClassifier(n_jobs=3, random_state=0, n_estimators=150)
        self.clf.fit(X_train_tf, y_train)
        # self.clf =SVC()
    def train_cost_sensitive_RF_words_only(self,X_train,y_train):
        stopWords = set(nltk.corpus.stopwords.words('english'))
        self.count_vect1 = CountVectorizer(max_features=500000,ngram_range=(1,3),stop_words=stopWords,lowercase=True)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=True).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = RandomForestClassifier(n_jobs=3, n_estimators=200)
        self.clf.fit(X_train_tf, y_train)

    def save_RF_words_only(self,path):
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.count_vect1, open(path+"/count_vectorizer.pck", 'wb'))
        pickle.dump(self.tf_transformer, open(path + "/tf_transformer.pck", 'wb'))
        pickle.dump(self.clf, open(path + "/classifier.pck", 'wb'))

    def load_RF_words_only(self,path):
        self.count_vect1 = pickle.load(open(path+"/count_vectorizer.pck", 'rb'))
        self.tf_transformer = pickle.load(open(path + "/tf_transformer.pck", 'rb'))
        self.clf = pickle.load(open(path + "/classifier.pck", 'rb'))
        return self

    def train_RF_features_only(self,X_train,y_train):
        train_vector = []
        for x in X_train:
            xa = x.lower()
            has_obj = 0
            has_target = 0
            has_improve = 0
            has_things = 0
            has_new = 0
            has_things2 = 0
            has_things3 = 0
            has_new_tech = 0
            has_actor = 0
            for o in self.obj:
                if o in xa:
                    has_obj = 1
            for o in self.targets:
                if o in xa:
                    has_target =1
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
            train_vector.append([has_obj, has_target, has_improve, has_things, has_things2,has_things3, has_new, has_new_tech,has_actor])
        y_pred = self.clf.predict(train_vector)
        return y_pred


    def train_NB_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = MultinomialNB()
        self.clf.fit(X_train_tf, y_train)

    def train_SVM_words_only(self, X_train, y_train):
        self.count_vect1 = CountVectorizer(max_features=1000)
        X_train_counts = self.count_vect1.fit_transform(X_train)
        self.tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
        X_train_tf = self.tf_transformer.transform(X_train_counts)
        #print("Training")
        self.clf = SVC()
        self.clf.fit(X_train_tf, y_train)
        # self.clf.fit(features2, y)
        #print("Trained")
    def predict_words_only(self,X_test):
        X_new_counts = self.count_vect1.transform(X_test)
        X_test_tf = self.tf_transformer.transform(X_new_counts)
        y_pred = self.clf.predict(X_test_tf)
        return y_pred

    def print_reports(self,y_pred,y_test):
        print(sklearn.metrics.classification_report(y_pred, y_test))
        new_confusion_matrix = sklearn.metrics.confusion_matrix(y_pred, y_test)
        #self.confusion_matrix = [[self.confusion_matrix[i][j] + new_confusion_matrix[i][j] for j in range(len(self.confusion_matrix[0]))] for i in range(len(self.confusion_matrix))]
        #self.confusion_matrix = self.confusion_matrix + new_confusion_matrix
        print(new_confusion_matrix)
        print('accuracy is', accuracy_score(y_pred, y_test))


    def print_final_report(self):
        print("Overall confusion matrix:")
        print(self.confusion_matrix)
        overall_TP = 0.0
        overall_FP = 0.0
        overall_FN = 0.0
        precision = [0,0]
        recall = [0,0]
        F1score = [0,0]
        for i in range(0,len(precision)):
            true_pos = 0.0+self.confusion_matrix[i][i]
            false_pos = 0.0
            false_neg = 0.0
            for j in range(0,len(precision)):
                if j == i:
                    continue
                false_neg = false_neg + self.confusion_matrix[i][j]
            for j in range(0,len(precision)):
                if j == i:
                    continue
                false_pos = false_pos + self.confusion_matrix[j][i]
            overall_TP = overall_TP + true_pos
            overall_FP = overall_FP + false_pos
            overall_FN = overall_FN + false_neg
            if (true_pos+false_pos)!=0:
                precision[i] = true_pos/(true_pos+false_pos)
            if true_pos ==0 and (true_pos+false_pos)==0:
                precision[i] = 1.0
            if (true_pos + false_neg) != 0:
                recall[i] = true_pos/(true_pos+false_neg)
            if true_pos ==0 and (true_pos+false_neg)==0:
                recall[i] = 1.0
            if precision[i]+recall[i] >0:
                F1score[i] = 2*precision[i]*recall[i]/(precision[i]+recall[i])
            else:
                F1score[i] = 0.0
            print(str(i)+"\t\t"+str(round(precision[i],2))+"\t\t\t"+str(round(recall[i],2))+"\t\t"+str(round(F1score[i],2)))
        overall_precision = overall_TP/(overall_FP+overall_TP)
        overall_recall = overall_TP/(overall_TP+overall_FN)
        overall_F1score = 2*overall_precision*overall_recall/(overall_precision+overall_recall)
        print("Overall\t"+str(round(overall_precision,2))+"\t\t\t"+str(round(overall_recall,2))+"\t\t"+str(round(overall_F1score,2)))



#this is implemented when in the main program, being this program, as we are importing other code as well
if  __name__ == '__main__':
    #set the path variable equal to the path below. The files in SI_only actually do contain scores for the
    #criteria, other than 0.
    path = "../../../../Helpers/SI_dataset/Output/SI_only"
    #assign the return value from implementing the read_files fucntion with path passed in as a parameter
    #this is what is returned - annotations.append([ann,content,objective,actors,outputs,innovativeness,si])
    annotations = read_files(path)


    #the code below calculates the SI scores
    ### SI Marks
    print("Working on Social innovation")
    #declare two empty lists - texts and classA
    texts = []
    classA = []
    #iterate through the returned list - annotations
    for anns in annotations:
        #append the contents to the empty list- texts
        texts.append(anns[1])
        #assign the si value in annotations at index 6 to the variable - value
        value = anns[6]
        #if value is greater than 2, then assign 1 to it, and if less than 2, then assign 0
        if value>=2:
            value = 1
        else:
            value =0
        #append value to classA
        classA.append(value)
    #create a dataframe with texts and classA as columns and label the columns - 'text' and 'classa'
    df = pd.DataFrame({'text': texts, 'classa': classA})
    #print the count of unique values for the classa column
    print(df.classa.value_counts())
    #create a dataframe - df_majority to hold the classa == 1 entries from df
    df_majority = df[df.classa == 1]
    # create a dataframe - df_minority to hold the classa == 0 entries from df
    df_minority = df[df.classa == 0]
    #upsample df_minority by carrying out resampling with replacement and assign the resulting dataframe to a
    #variable -df_minorty_upsampled
    df_minority_upsampled = resample(df_minority,
                                      replace=True,     # sample with replacement
                                      n_samples=60,    # to match majority class
                                      random_state=83293) # reproducible results

    #create a dataframe -df_upsampled by concatenating df_majority with df_monority_upsampled
    df_upsampled = pd.concat([df_majority, df_minority_upsampled],ignore_index=True)
    #reshuffle df_upsampled as was done with the other dataframes in Basic_experiments
    df_upsampled = df_upsampled.sample(frac=1).reset_index(drop=True)
    #print out the unique values in the classa column of df_upsampled
    print(df_upsampled.classa.value_counts())
    #assign df_upsampled to df, basically for ease, I suspect
    df = df_upsampled
    #create an object of the UniversalClassifier class - cls
    cls = UniversalClassifier()
    #Declare a variable - X_train and assign it the text column in df
    X_train = df['text']
    #Declare a variable y_train and assign it the classa column in df
    y_train = df['classa']

    #pass in X_train and y_train as parameters to the train_cost_sensitive_RF_words_only model
    cls.train_cost_sensitive_RF_words_only(X_train,y_train)

    #call the save_RF_words_only function and pass in the string - "SI_RF" as a parameter, to basically set the
    #directory or folder name for the SI model
    cls.save_RF_words_only("SI_RF")


    #y_pred = cls.predict_words_only(test_df['text'])
    # call the print_reports function of the Universal Classifier and pass in the returned y_pred and the test_df['classa']
    # to print out the confusion matrix and classification report
    #cls.print_reports(y_pred, test_df['classa'])
    print("End of SI")

