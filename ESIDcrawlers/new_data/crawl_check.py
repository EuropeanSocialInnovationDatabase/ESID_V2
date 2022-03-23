from pymongo import MongoClient
import MySQLdb
import pandas as pd
from database_access import *
from os import listdir
from os.path import isfile, join
import os


def doc_size_count(doc_info, path):
    #in this function, the dataframe that will hold the project_id as well as the length of the document crawled
    #for that id will be created and printed out

    #code below still needs work
    df = pd.DataFrame(doc_info)
    df.columns = ["Project_id", "Document Length","url"]
    print(df)
    df.to_csv(os.path.join(path, r'simra_230322.csv'))
    #df.to_csv(os.path.join(path, r'Documentcount.csv'))


if  __name__ == '__main__':
    #path = "../../../../Helpers/SI_dataset/Output/SI_only"
    path = "/ESID_Nikola/ESID-main/ESIDcrawlers/new_data"
    document_info = []
    db_mysql = MySQLdb.connect(host, username, password, database, charset='utf8')
    #declare the mysql cursor and assign it to variable - mysql_cursor
    mysql_cursor = db_mysql.cursor()
    #declare the MongoClient and assign it to variable mongo_client. This allows us use MongoDB in our code
    mongo_client = MongoClient()
    #set the mongodb database as ESID. Assign this to a variable - mongo_db. This allows us use mongoDB
    mongo_db = mongo_client.ESID

    sql = "Select * from Projects where DataSources_idDataSources = 5"
    mysql_cursor.execute(sql)
    # fetch the results from the query and assign these to the results variable
    results = mysql_cursor.fetchall()

    for res in results:
        print (res[0])
        project_id = res[0]
        project_url = res[11]
        #declare a variable - documents and assign it the results in mongo collection -
        #This will be changed to the new_crawl collections - the ssir ones first
        documents = mongo_db.new_crawl_simra_230322.find({"database_project_id": project_id},
                                                           no_cursor_timeout=True).batch_size(100)
        #documents = mongo_db.new_crawl_310521.find({"database_project_id": project_id},
                                                  # no_cursor_timeout=True).batch_size(100)


        # declare an empty string document_text

        document_text = ""
        #document_url = ""

        for doc in documents:
            #I'll need to change the 'translation' here to whatever the json tag for the contents of the new crawl
            #is. I think it is 'content'. This appends the contents of the documents to the string -document_text
            #for that project

            document_text = document_text + doc['content']
            #document_url = doc ['database_url']
            print (document_text)
            print(project_id, len(document_text))
        document_info.append([project_id,len(document_text),project_url])
        doc_size_count(document_info,path)
        #print (project_id, len (document_text))

