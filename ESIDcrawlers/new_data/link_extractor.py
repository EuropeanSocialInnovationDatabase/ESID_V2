#!/usr/bin/env python
# -*- coding: utf-8 -*-

from database_access import *
import codecs
import csv
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import cgi
import MySQLdb

#from database_access import *
import MySQLdb
import simplejson


def print_correct(url):
    url = str(url)
    fixed_links2 =[]
    #print (url if "://" in url else "http://" + url)

    return url if "://" in url else "http://" + url


def url_check(url):

    min_attr = ('scheme' , 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            print ('correct')
        else:
            print('wrong')
    except:
        print ('wrong')

#def get_netloc(u):
 #   if not u.startswith('http'):
  #      u = '//' + u
   # return urlparse(u).netloc

if __name__ == '__main__':
    print('starting link extraction')
    fname = "aifors.json"
    with codecs.open(fname, "rb", encoding='utf-8') as f:
        links_data = f.read()
    json_data = simplejson.loads(links_data)

    all_links =[]

    for item in json_data:
        try:
            website = item['link'][0]
        except:
            website = ""
        #website = str(website)
        #in order to allow for the url to be correct, I have added these

        print_correct(website)
        all_links.append(website)#not working yet
        #url_check(website)
        corrected_url = print_correct(website)
        print (corrected_url)


        #get_netloc(website)
        #get_all_website_link(website)


    with open('aiforsdg_links','w') as f:
        write = csv.writer(f)
        write.writerows(all_links)


    print(all_links) #not working yet
    print (len(all_links))#not working yet

    #db = MySQLdb.connect(host, username, password, database, charset='utf8')
    #cursor = db.cursor()
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    for item in json_data:
        title = item['title'][0]
        country = item['country'][0]
        try:
            link = print_correct(item['link'][0])
        except:
            link = ""
        short_description = tag_re.sub('',item['short_description'][0])
        long_description = tag_re.sub('',item['long_description'][0])
        description = short_description + ' ' + long_description

        print (title,country,link,description)#- just used as a check of the data

        db = MySQLdb.connect(host, username, password, database, charset='utf8')
        cursor = db.cursor()
        new_project = True
    
        proj_check = "SELECT * from Projects where ProjectName like '%"+title+"%'"
        cursor.execute(proj_check)
        num_rows = cursor.rowcount
        if num_rows != 0:
            new_project = False
    
        url_compare = "SELECT * from Projects where ProjectWebpage like '" + link + "'"
        cursor.execute(url_compare)
        num_rows = cursor.rowcount
        if num_rows != 0:
            new_project = False

        if new_project:
            project_insert = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
            cursor.execute(project_insert,(title,link,'https://www.aiforsdgs.org/all-projects',9))
            projectid = cursor.lastrowid
            print(projectid)
            db.commit()

            ins_desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
            cursor.execute(ins_desc,("Description",description,str(projectid)))
            db.commit()

            ins_location = "Insert into ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)"
            cursor.execute(ins_location,("Main",country,str(projectid)))
            db.commit()

        else:
            print('Project already exists!')
            print (title)
