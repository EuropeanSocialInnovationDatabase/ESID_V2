#This code is used to add additional manual annotations to the esid_prediction table

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
import pyodbc

# from database_access import *
import MySQLdb
import simplejson


if __name__ == '__main__':

    data = pd.read_csv(r'/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/Eusic-simra-Annotations.csv')
    df = pd.DataFrame(data)

    print(df)

    #strips out any spaces that might come before or after the column name to ensure it matches
    data.columns = data.columns.str.strip()
    print(df.columns)
    #with open("Eusic-simra-Annotations.csv", 'r') as file:
     #   reader = csv.reader(file)
      #  next(reader, None)
       # print ("project running")
        
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    cursor2 = db.cursor()

    sql_sent = "CREATE TABLE temp2 (Project_id text not null, Name text not null, Objectives text not null, \
    Actors text not null, Outputs text not null, Innovativeness text not null, Annotation text not null);"

    cursor.execute(sql_sent)

    # Insert DataFrame to Table
    for row in df.itertuples():
        sql_insrt = "INSERT INTO temp2 (Project_id, Name, Objectives,Actors, Outputs, Innovativeness, Annotation) \
                    VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor2.execute(sql_insrt,

                        (
                       row.Project_id,
                       row.Name,
                       row.Objectives,
                       row.Actors,
                       row.Outputs,
                       row.Innovativeness,
                       row.Annotation
                        ))
        db.commit()




        #sql_query = sqlalchemy.text(
         #   "CREATE TABLE temp (id int primary key, name varchar(30) not null, author varchar(30) not null)")
        #result = db_connection.execute(sql_query)
        #csv_df.to_sql('temp', con=db_connection, index=False, if_exists='append')