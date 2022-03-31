# -*- coding: utf-8 -*-
#import the MongoClient from pymongo; this allows you to use data from MongoDB
from pymongo import MongoClient
#from the ANN_Experiments code, import the UniversalNNClassifier class
from ANN_Experiments import UniversalNNClassifier
#import the mysql database
import MySQLdb
#import the database_access file with the credentials to log into the database
from database_access import *

#use this as we want to implement the present file we are in as the main; and because we imported from another code
if  __name__ == '__main__':
    #set variables wayback_bar and wayback_bar2 as multi-line strings
    wayback_bar = """ <![endif]   BEGIN WAYBACK TOOLBAR INSERT   success  fail   NEXT/PREV MONTH NAV AND MONTH INDICATOR   Oct  MAY  Jun   NEXT/PREV CAPTURE NAV AND DAY OF MONTH INDICATOR   14   NEXT/PREV YEAR NAV AND YEAR INDICATOR"""
    wayback_bar2 = """About this capture  COLLECTED BY  		Organization:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  Collection:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  TIMESTAMPS   END WAYBACK TOOLBAR INSERT   [if lt IE 7]><p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p><![endif]"""

    #set the mysql connection variable to db_mysql
    db_mysql = MySQLdb.connect(host, username, password, database, charset='utf8')
    #declare the mysql cursor and assign it to variable - mysql_cursor
    mysql_cursor = db_mysql.cursor()
    #declare the MongoClient and assign it to variable mongo_client. This allows us use MongoDB in our code
    mongo_client = MongoClient()
    #set the mongodb database as ESID. Assign this to a variable - mongo_db. This allows us use mongoDB
    mongo_db = mongo_client.ESID
    #implement a select query from Projects database where Exclude is equal to False
    sql = "Select * from Projects where Exclude =0"
    #execute the mysql_cursor on the select query result. This allows you iterate through the results
    mysql_cursor.execute(sql)
    #fetch the results from the query and assign these to the results variable
    results = mysql_cursor.fetchall()
    #create an instance of the UniversalNNClassifier class - objective_cls
    objective_cls = UniversalNNClassifier()
    #using this object, call the load_CNN_model and pass Objectives_LSTM to it. This is the folder name. This will the
    #get into the function as a path and be appended with other paths to get to the JSON file within that folder, which
    #seems to be from keras. Will confirm. This is done for the Objectives - LSTM neural networks
    objective_cls.load_CNN_model("Objectives_LSTM")
    #another instance of the UniversalNNClassifier is created for the actors data, actors_cls
    actors_cls = UniversalNNClassifier()
    #using this object, actors_cls, call the load_CNN_model and pass in the path to the Actors_LSTM, which in turn goes
    #leads to the json file
    actors_cls.load_CNN_model("Actors_LSTM")
    #same as actor and objective, is done for outputs
    outputs_cls = UniversalNNClassifier()
    #same as for actor and objective, the load_CNN_model is called and the path passed in
    outputs_cls.load_CNN_model("Outputs_LSTM")
    #same as above, an instance of the UniversalNNClassifier is created for innovativeness
    innovativeness_cls = UniversalNNClassifier()
    #same as those above, the path to the json file is passed in
    innovativeness_cls.load_CNN_model("Innovativeness_LSTM")

    #iterate through results, which contained the results from the select all query from the Projects table
    for res in results:
        #print res[0], which is the idProjects variable
        print (res[0])
        #declare an empty string, variable
        message = ""
        #assign the string below to the 'option' variable, which specifies which neural network classifier version is run
        #together with what it entails - embeddings, unbalanced dataset and the date variable
        option = "v26 CNN+LSTM 200d embeddings unbalanced, 08/05/2019"
        #decalre variables - objective, actors, outputs and innovativeness and assign the value - '0' to them
        objective = 0
        actors = 0
        outputs = 0
        innovativeness = 0
        #assign the present iterable value of idProject to variable - project_id
        project_id = res[0]
        #declare a variable called documents that takes as a value the documents in crawl20190109_translated
        # collection in MongoDB with the mysql_databaseID item/variable being the same as the idProject in question
        #we use the find method of MongoDB, and are able to do this with the mongo_db variable
        #the batch size specifies the number of documents to return per batch
        documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                no_cursor_timeout=True).batch_size(100)
        #declare an empty string document_text
        document_text = ""
        #iterate through the returned documents in the documents variable which are documents associated with
        # the project_id in question
        for doc in documents:
            #concatenate the empty string document_text with the values of the 'translation' item from mongodb,
            # in documents. Hence the translated text only is used. All the documents associated with that project_id
            #are concatenated together into one document_text
            document_text = document_text+doc['translation']
            #added for testing
           # print(document_text)
        #if the length of this concatenated document_text is less than 350, or there is a string "domain sale" in the text
        if len(document_text)<350 or "domain sale" in document_text:
            #declare a variable - documents2 which takes a value the documents in crawl20180801_wayback_translated collection
            #in MongoDB where the idProject -project_id is the same as that in question. It uses the find function
            #of mongo_db to locate the documents, and returns in batch_size of 100.
            #what happens here is that you check the wayback crawls now to get the old data that was there.
            documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)},
                                                    no_cursor_timeout=True).batch_size(100)
            #declare an empty string document_text
            document_text = ""
            #iterate through the documents in documents2
            for doc in documents2:
                #concatenate the entries in the 'translation' variable returned from MongoDB for each document to
                #document_text. At the end, you will have one long document_text with all the documents from that
                #project_id
                document_text = document_text + " "+doc['translation']

        #if '404' is found in document_text or if you encounter "page not found" in document_text, after converting it to
        #lower case, ofcourse. That is, this will show that the page is not available
        if "404" in document_text or "page not found" in document_text.lower():
            #set the string 'message', declared above as empty, to "Page not found"
            message = "Page not found"
            #insert into the TypeOfSocialInnovation table, for the various criteria, zeroes, as this is what was assigned to
            #objective, actors, outputs, innovativeness, above. Insert the project_id, the option, and the message, which
            #saye that the page has not been found
            #option is entered under -SourceModel, and Message - AnnotationComment
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective,actors,outputs,innovativeness,project_id,option,message)
            #execute the sql insert query and commit the results
            mysql_cursor.execute(sql)
            db_mysql.commit()
        #else, if you happen to find any of the strings below,after converting the strings in document_text to lowercase
        #ofcourse, to enable matching.
        elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower()\
                or "abbiamo appena registrato" in document_text.lower() or "neither the service provider nor the domain owner maintain any relationship with the advertisers." in document_text.lower()\
                or "to purchase, call buydomains" in document_text.lower() or "hundreds of thousands of premium domains" in document_text.lower() or "search for a premium domain" in document_text.lower()\
                or "This domain is registered for one" in document_text.lower() or "for your website name!" in document_text.lower():
            #then assign the string below - "Domain for sale" to the message variable.
            message = "Domain for sale"
            #execute an sql insert query to insert the data below into the TypeofSocial Innovation table in the database
            #with the message that the domain is for sale, and also the project_id and the option, and '0' for all the
            #criteria
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            #execute the query and commit the data
            mysql_cursor.execute(sql)
            db_mysql.commit()

        #else, if the length of document_text is below 350, then do what's below. - This appears to me like it should have
        #been placed up there with the domain for sale and less than 350 conditions...as an else for the wayback_crawl data
        elif len(document_text)<350:
            #assign the string "Text smaller than 350 characters" to the string - message
            message = "Text smaller than 350 characters"
            #execute an sql insert query and insert the data below into the TypesofSocialInnovation table in the database
            #the message that the text is smaller than 350 characters, and zeroes for the four criteria, and the project_id
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            #execute the query and commit into the database
            mysql_cursor.execute(sql)
            db_mysql.commit()
        #if document_text is just right
        else:
            #assign the value from calling the predict_CNN function with the objective_cls object, passing in
            # document_text as a list? The score is at the 0th index, of something I'll figure out from the predict_CNN
            #from looking at the predict_CNN function, this appears to return '1' or '0' only. But this is not so. It
            # gives the variation - 0 to 3.
            objective = objective_cls.predict_CNN([document_text])[0]
            #do the same as the above for actors, outputs and innovativeness
            actors = actors_cls.predict_CNN([document_text])[0]
            outputs = outputs_cls.predict_CNN([document_text])[0]
            innovativeness = innovativeness_cls.predict_CNN([document_text])[0]
            #execute an sql insert query to put in the results in the TypesofSocialInnovation table, with the message
            #and the option.
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}')".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message)
            #execute the query and commit the results
            mysql_cursor.execute(sql)
            db_mysql.commit()
            #In summary, this code takes the document_text, which is basically everything that matches a specific
            # project_id from MongoDB and then feeds this to the CNN algorithm which classifies and returns the scores
            #that are then entered into the database TypesofSocialInnovation table

    print("Done!")