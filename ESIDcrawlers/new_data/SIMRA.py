from database_access import *
from builtins import bytes, int, str
import codecs
import csv
import requests

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import cgi
import MySQLdb
import chardet

# from database_access import *
import MySQLdb
import simplejson

def print_correct(url):
    url = str(url)
    fixed_links2 = []
    # print (url if "://" in url else "http://" + url)

    return url if "://" in url else "http://" + url


if __name__ == '__main__':

    with open("SIMRA.csv",'r', encoding="ISO-8859-1") as file:
        reader = csv.reader(file)
        #reader = csv.reader(text)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_links = []
        all_project_ids = []


        for row in reader:
            if row[7] != " " and row[16] != " ":
                    country = row[2]
                    city = row[8]
                    description = row[11] + '' + row[12]
                    title = row[7].replace("'", "''")
                    link = row[16]
                    #date_start = row[9]
                    correct_link = print_correct(link)
                    #print a check here
                    print(title,description,country, city, link)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor = db.cursor()
                    new_project = True

                    proj_check = "SELECT * from Projects where ProjectName like '%" + title + "%'"
                    #proj_check = "SELECT * from Projects where ProjectName like %s",(title,)
                    #cur.execute("SELECT * FROM records WHERE email LIKE %s", (search,))
                    cursor.execute(proj_check)
                    num_rows = cursor.rowcount
                    if num_rows != 0:
                        new_project = False

                    url_compare = "SELECT * from Projects where ProjectWebpage like '" + link + "'"
                    #url_compare = "SELECT * from Projects where ProjectWebpage like %s",(link,)
                    cursor.execute(url_compare)
                    num_rows = cursor.rowcount
                    if num_rows != 0:
                        new_project = False

                    if new_project:
                        project_insert = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor.execute(project_insert, (title, link,'SIMRA', 5))
                        projectid = cursor.lastrowid
                        print(projectid)



                        #ashoka_projectids.append(projectid)
                        db.commit()

                        ins_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
                        cursor.execute(ins_desc, ("Description", description, str(projectid)))
                        db.commit()

                        ins_location = "Insert into ProjectLocation (Type,Country,City,Projects_idProjects) VALUES (%s,%s,%s,%s)"
                        cursor.execute(ins_location, ("Main", country,city, str(projectid)))
                        db.commit()


                    else:

                        print('Project already exists!')
                        print(title)


                    all_links.append(correct_link)

    #print out SIMRA's links to a file for crawling later
    with open('simra_links', 'w', newline='') as f:
        write = csv.writer(f)
        for row in all_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write.writerow(columns)