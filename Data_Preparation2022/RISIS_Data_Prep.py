from database_access import *
import codecs
import csv
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import cgi
import MySQLdb
import pandas as pd
from os.path import isfile, join
import os
from os import listdir


# from database_access import *
import MySQLdb
import simplejson



def doc_collect(data_collector, path):
    #in this function, the dataframe that will hold the project_id as well as the length of the document crawled
    #for that id will be created and printed out

    #code below still needs work
    df = pd.DataFrame(data_collector)
    df.columns = ["Project_id", "Description"]
    print(df)
    df.to_csv(os.path.join(path, r'Project_and_Description_General.csv'))


if __name__ == '__main__':


    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()

    Datacollector = []

    path = "/ESID_Nikola/ESID-main/Data_Preparation2022"


    #proj_extract ="SELECT idProjects FROM EDSI.Projects, EDSI.ProjectLocation where Country in \
     #       ('Denmark','Norway','Sweden','Finland','Iceland') and idProjects = Projects_idProjects"

    proj_extract = "SELECT distinct(idProjects) FROM EDSI.Projects"

    cursor.execute(proj_extract)
    results = cursor.fetchall()

    for row in results:
        idProject = row[0]
        print("Project ID:" + str(idProject))

        desc_extract = "SELECT * FROM EDSI.AdditionalProjectData where FieldName like '%desc%' and Projects_idProjects="+str(idProject)
        cursor.execute(desc_extract)
        results2 = cursor.fetchall()

        for row2 in results2:
            Description = ""
            desc_text = row2[2]
            Description = Description + " " + desc_text
            print ('Description:' , Description)


        Datacollector.append([idProject , Description])
        print(Datacollector)

    doc_collect(Datacollector,path)
