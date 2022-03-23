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


def url_check(url):
    min_attr = ('scheme', 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            print('correct')
        else:
            print('wrong')
    except:
        print('wrong')


if __name__ == '__main__':

    with open("Eusic.csv", 'r',encoding = "ISO-8859-1") as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")

        all_links = []
        all_project_ids = []

        for row in reader:
            if row[1] != "" and row[4] != "":
                    link = row[4]
                    corrected_url = print_correct(link)
                    print (corrected_url)
                    right_link = corrected_url
                    country = row[3]
                    description = row[5]
                    title = row[1].replace("'", "''")
                    facebook_page = row[6]
                    twitter_handle = row[7]

                    #print a check here
                    print(title,description,country, right_link)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor = db.cursor()
                    new_project = True

                    proj_check = "SELECT * from Projects where ProjectName like '%" + title + "%'"
                    cursor.execute(proj_check)
                    num_rows = cursor.rowcount
                    if num_rows != 0:
                        new_project = False

                    url_compare = "SELECT * from Projects where ProjectWebpage like '" + right_link + "'"
                    cursor.execute(url_compare)
                    num_rows = cursor.rowcount
                    if num_rows != 0:
                        new_project = False

                    if new_project:
                        project_insert = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources,FacebookPage,ProjectTwitter) VALUES (%s,%s,%s,%s,%s,%s)"
                        cursor.execute(project_insert, (title, right_link, 'EUSIC', 12,facebook_page,twitter_handle))
                        projectid = cursor.lastrowid
                        print(projectid)



                        #ashoka_projectids.append(projectid)
                        db.commit()

                        ins_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
                        cursor.execute(ins_desc, ("Description", description, str(projectid)))
                        db.commit()

                        ins_location = "Insert into ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)"
                        cursor.execute(ins_location, ("Main", country, str(projectid)))
                        db.commit()

                        all_links.append(corrected_url)
                        url_check(corrected_url)

                    else:

                        print('Project already exists!')
                        print(title)


                    #all_links.append(corrected_url)
                    #url_check(corrected_url)
        #location_update()

#print out EUSIC's links to a file for crawling later
    with open('eusic_links', 'w', newline='') as f:
        write = csv.writer(f)
        for row in all_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write.writerow(columns)