#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from Basic_experiments import UniversalClassifier
import MySQLdb
from database_access import *
from langdetect import detect

#this code imports from the UniversalClassifier class
#This function takes project_text as a parameter, and checks if in English, and then translates
def checkEngAndTranslate(project_text):
    #signal.signal(signal.SIGALRM, handler)
    #signal.alarm(60)
    #set a global variable -translationTimeout
    global translationTimeout
    #declare a variable -language, and assign it string 'en', which denotes English
    language = 'en'
    #check if project_text is an empty string; and if so, assign it language - 'en'
    if project_text == "":
        language = 'en'
    #else, if it's not empty
    else:
        #call the detect method from langdetect,which is Python's language detection library and pass in the project
        #text. Assign its return value, which would be the detected language to variable - language
        try:
            language = detect(project_text)
        #in case of an exception, then print - 'Error translating'
        except:
            print("Error translating")
    #print out the string langauage, concatenated with the detected language
    print("Language:" + str(language))
    #in this outer loop, if however the langauge is "en", meaning English, then return project_text
    if language == "en":
        return project_text
    #if the langauge is not "en", meaning if it is not English; return an empty string and print - "Start translating"
    if language != "en":
        return ""
        print("Start translating")
        #break the text into tokens by calling the nltk word_tokenize on it and assign these to a variable - tokens
        tokens = nltk.word_tokenize(project_text)
        #declare a variable 'i' and assign it the value - 0
        i = 0
        #declare a varaible - text_to_translate and assign it an empty string
        text_to_translate = ""
        #declare a variable -translated and assign it an empty string
        translated = ""
        #create a while loop to check i. While i is less than the length of the tokens
        while i < len(tokens):
            #for j in range 0-200, as an inner loop,
            for j in range(0, 200):
                #check if i is greater than or equal to the length of tokens, and if so, then go back to outerloop
                if i >= len(tokens):
                    continue
                #concatenate the token at position 'i' to the text_to_translate and assign it to the variable text_
                #to_translate
                text_to_translate = text_to_translate + " " + tokens[i]
                #increment i
                i = i + 1
            #open up an exception and call the translate function to translate the text_to_translate above and assign
            #this to a variable - en_text
            try:
                en_text = translate(text_to_translate.encode('utf-8').strip(), "en", "auto")
            #throw an exception if there is an issue and print out 'Timeout translation'
            except:
                print("Timeout translation")
                #increment the timeout variable, to actually keep track of the translation timeouts
                translationTimeout = translationTimeout + 1
                #assign an empty string to en_text, which is meant to be the english translation of the text
                en_text  = ""
            #concatenate en_text to translated, which was an empty string and assign this to the variable - translated
            #again
            translated = translated + " " + en_text
            #declare text_to_translate as an empty string again
            text_to_translate = ""
        #print the translated text
        print(translated)
        #assign the translated text to project_text
        project_text = translated
        #print "End translating to show the translation has ended, and return project_text
        print("End translating")
        return project_text
    #return project_text for the entire if loop
    return project_text
#execute this when in this main
if  __name__ == '__main__':
    wayback_bar = """ <![endif]   BEGIN WAYBACK TOOLBAR INSERT   success  fail   NEXT/PREV MONTH NAV AND MONTH INDICATOR   Oct  MAY  Jun   NEXT/PREV CAPTURE NAV AND DAY OF MONTH INDICATOR   14   NEXT/PREV YEAR NAV AND YEAR INDICATOR"""
    wayback_bar2 = """About this capture  COLLECTED BY  		Organization:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  Collection:  Alexa Crawls  	  Starting in 1996,  Alexa Internet  has been donating their crawl data to the Internet Archive.  Flowing in every day, these data are added to the  Wayback Machine  after an embargo period.	  TIMESTAMPS   END WAYBACK TOOLBAR INSERT   [if lt IE 7]><p class="chromeframe">You are using an outdated browser. <a href="http://browsehappy.com/">Upgrade your browser today</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to better experience this site.</p><![endif]"""
    #set connection parameter for mysql
    db_mysql = MySQLdb.connect(host, username, password, database, charset='utf8')
    #initialise cursor for mysql
    mysql_cursor = db_mysql.cursor()
    #set a variable for mongoclient and connect to ESID
    mongo_client = MongoClient()
    mongo_db = mongo_client.ESID
    #select all from ESID projects table, where the exclude variable is 0, hence set to False
    sql = "Select * from Projects where Exclude =0"
    #set the cursor to point to, and iterate through the sql statements returned
    mysql_cursor.execute(sql)
    #assign all the results fetched from the sql query to variable 'results'
    results = mysql_cursor.fetchall()
    #create object objective_cls of the Universal Classifier class
    objective_cls = UniversalClassifier()
    #call load_RF_words_only and pass in the parameter "Objectives_RF", which is fed to the function
    objective_cls.load_RF_words_only("Objectives_RF")
    #create object actors_cls of the Universal Classifier class
    actors_cls = UniversalClassifier()
    #call load_RF_words_only and pass in the parameter "Actors_RF"
    actors_cls.load_RF_words_only("Actors_RF")
    #create outputs_cls of the Universal Classifier class
    outputs_cls = UniversalClassifier()
    #call load_RF_words_only and pass in the parameter "Outputs_RF"
    outputs_cls.load_RF_words_only("Outputs_RF")
    #create innovativeness_cls for the Universal Classifier
    innovativeness_cls = UniversalClassifier()
    #call load_RF_words_only and pass in the parameter "Innovativeness_RF"
    innovativeness_cls.load_RF_words_only("Innovativeness_RF")
    #create si_cls as an object of the Universal Classifier class
    si_cls = UniversalClassifier()
    #call load_RF_words_only and pass in the parameter "SI_RF"
    si_cls.load_RF_words_only("SI_RF")
    #iterate through the results, which are the sql projects
    for res in results:
        #print element at index 0; which is the project_id -idProject of the iterated element at that point
        print (res[0])
        #create a variable message, and assign an empty string to it
        message = ""
        #option = "v27 classifier new dataset (naturally balanced) random forests, with 1-4 grams, 08/05/2019"
        #create a variable called option and assign a string which identifies the name of the classifier, as well
        # as the date, to it
        option = "v50 classifier new dataset (naturally balanced) random forests, with 1-3 grams, 15/12/2020"
        #create and initialise variables objective, actors, outputs, innovativeness and si to 0
        objective = 0
        actors = 0
        outputs = 0
        innovativeness = 0
        #create a variale document_text and assign an empty string to it
        document_text = ""
        si = 0
        #assign the element at index 0 of the returned results to variable project_id. This is idProject from the
        #database
        project_id = res[0]
        #create a variable and assign it the sql select statement that selects all entires from AdditionalProjectData table
        #which have descriptions, hence where there is a fieldname description, and SourceURL is not like %v1% or %v2%
        sql_desc = "Select * from AdditionalProjectData where FieldName like '%Desc%' and (SourceURL not like '%v1%' or SourceURL not like '%v2%')"
        #execute that statement with the cursor going through the returned data from the query
        mysql_cursor.execute(sql_desc)
        #assign the results fetched from the sql query to the variable results_desc
        results_desc = mysql_cursor.fetchall()
        #iterate through results_desc
        for desc in results_desc:
            #concatenate the descriptions to document_text, which was an empty string, creating one long string
            #assign these to document_text. The item at index 2 of results_desc is the value, that is, the description text
            document_text = document_text + " "+desc[2]
        #create a variable - documents and assign the mongo crawled texts, find project with the project_id. This is done
        #  with the MongoDB find function. Recall, project_id from above
        documents = mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                no_cursor_timeout=True).batch_size(100)
        #iterate through documents, which were from translated mongo_db crawls above
        for doc in documents:
            #assign the value in the translation element of the document in question to variable txt. documents appears to be
            #a dictionary
            txt = doc['translation']
            print(txt)
            #concatenate the translated texts stored in txt to documents_text, adding to that long document_text string
            document_text = document_text+" "+ txt
        #if the length of the string document_text is less than 350, or it contains string "domain sale"
        if len(document_text)<350 or "domain sale" in document_text:
            #declare a new variable, documents2 and assign the translated strings from the wayback crawls
            documents2 = mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)},
                                                    no_cursor_timeout=True).batch_size(100)
            #declare a new variable document_text and assign it an empty string
            document_text = ""
            #iterate through docuemnts2, which contains the wayback crawls
            for doc in documents2:
                #concatenate the values of the 'text' key or element to document_text, to create on string
                document_text = document_text + " "+doc['text']
        #if you come across the text "page not found" in document_text, (which you have converted to lowercase first),
        if "page not found" in document_text.lower():
            #print out the message, "Page not found"
            message = "Page not found"
            #assign sql insert statement to sql variable. Insert into Table - Types of Social Innovation, the following;
            #the SourceModel is the option set above, which is a string to identify the classifier run
            #the AnnotationComment is the message printed out, which is a string "Page not found". The different Criteria
            #will all be 0.
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                        project_id, option, message, si)
            #execute the sql query and commit the implementation result
            mysql_cursor.execute(sql)
            db_mysql.commit()
        # elif "domain for sale" in document_text.lower() or "buy this domain" in document_text.lower() or "find your perfect domain" in document_text.lower() or "domain expired" in document_text.lower()\
        #         or "abbiamo appena registrato" in document_text.lower() or "neither the service provider nor the domain owner maintain any relationship with the advertisers." in document_text.lower()\
        #         or "to purchase, call buydomains" in document_text.lower() or "hundreds of thousands of premium domains" in document_text.lower() or "search for a premium domain" in document_text.lower()\
        #         or "This domain is registered for one" in document_text.lower() or "for your website name!" in document_text.lower():
        #     message = "Domain for sale"
        #     sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
        #           "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
        #                                                                 project_id, option, message, si)
        #     mysql_cursor.execute(sql)
        #     db_mysql.commit()
        #else if the length of the document_text is less than 350, then print a different message, as shown below
        elif len(document_text)<350:
            message = "Text smaller than 350 characters"
            #declare a variable sql and assign the insert statement to it, to insert into table types of social innovation
            #the criteria will all be 0, based on the original assignment above
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                    project_id, option, message,si)
            #execute and commit the sql query and output
            mysql_cursor.execute(sql)
            db_mysql.commit()
        #the above implemented with objective, actors, outputs, innovativeness all with 0 as the entries
        #when the above conditions don't hold, then this else is executed
        else:
            #this calls the predict_words_only function of UniversalClassifier, using objective_cls and passes the document
            #text to it as a parameter. The value at index 0 is assigned to objective?
            #this implements the prediction on the document_text and on the index 0? Results of that prediction is
            # assigned to objective, same is done for actors, outputs, innovativeness, si
            message = "prediction done"#added by Roseline to denote predcition in dbase#11/01/2021
            objective = objective_cls.predict_words_only([document_text])[0]
            actors = actors_cls.predict_words_only([document_text])[0]
            outputs = outputs_cls.predict_words_only([document_text])[0]
            innovativeness = innovativeness_cls.predict_words_only([document_text])[0]
            si = si_cls.predict_words_only([document_text])[0]
            #the result is entered into the Typesofsocialinnovationtable. With the message and the option. These are ofcourse
            #the predictions for the various criteria, as well as the project_id
            sql = "Insert into TypeOfSocialInnotation (CriterionObjectives,CriterionActors,CriterionOutputs,CriterionInnovativeness,Projects_idProjects,SourceModel,AnnotationComment,Social_Innovation_overall)" \
                  "Values ({0},{1},{2},{3},{4},'{5}','{6}',{7})".format(objective, actors, outputs, innovativeness,
                                                                        project_id, option, message, si)
            #execute the sql query here and commit to the database
            mysql_cursor.execute(sql)
            db_mysql.commit()
    print("Done!")

    #what is basically happening here is that the descriptions of the projects from the AdditionalProjectsData are
    #concatenated with the text on the project from MongoDB crawl_translated and these are used to predict the different
    #criteria. I'm a bit concerned about that approach. Checked MongoDBcawl_translated and it appears to contain the
    #translations of each page, with the project_id to denote what project it is, and also the pages could be the 'about'
    #page, the 'Description' page, the 'home' page, or any other page. Will need to see how which page to use was decided.

