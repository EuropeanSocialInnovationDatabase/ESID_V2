import pandas as pd
import pysolr
import json
import pprint
from pymongo import MongoClient
from database_access import *
import MySQLdb
from urllib.parse import unquote, urlparse
import tldextract
from os import listdir
from os.path import isfile, join
import os



def url_break_match(url):
    #url_piece = urlparse(url).path
    #url_piece = url_piece.split("/")[-2]
    #print(url_piece)

    parsed_uri = urlparse(url)
    # result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    result = '{uri.netloc}/'.format(uri=parsed_uri)
    # url_end = url.split("/")[-3:]
    return result

def url_trailing(url):
    url_end = url.split("/")[3:]
    #return url_end
    return len(url_end)
    print(url_end)
    print('The length of the URL is:', len(url_end))

def url_trailing_end (url):
    url_ending = url.split("/")[3:]
    return url_ending

def replace_url_scheme(url):
    result2 = url.replace("https://", "").replace("http://", "").replace("www.", "")
    result2 = result2.strip()
    return result2

def domain_extract(url):
    ext = tldextract.extract(url)
    domain_name = ext.domain
    domain_name = domain_name.strip()
    return domain_name
    #print (domain_name)

def doc_check(doc_info, path):
    #in this function, the dataframe that will hold the project_id as well as the length of the document crawled
    #for that id will be created and printed out

    #code below still needs work
    df = pd.DataFrame(doc_info)
    df.columns = ["url_domain_solr", "website", "content"]
    print(df)
    df.to_csv(os.path.join(path, r'aifor_check.csv'))


if __name__ == '__main__':
    #this line is used to extract the json file from solr. rows is set to the total number of rows in the indexed results
    #for ssir, it is 29040
    #solrcon = pysolr.Solr('http://130.159.136.15:8983/solr/ssir3/select?q=*%3A*&rows=50275&wt=json', timeout=10)
    solrcon = pysolr.Solr('http://130.159.136.15:8983/solr/simra/select?q=*%3A*&rows=28751&wt=json', timeout=20)
    results = solrcon.search('*:*')
    docs = results.docs
    pprint.pprint(docs)

    client = MongoClient()
    db2 = client.ESID

    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()

    proj_database_name = ""
    proj_database_url = ""
    proj_database_id = ""

    #url = 'https://www.cycri.org/saaf'

    #domain_extract(url)
    # create a mongo_db collection:
    # test_collection2 = db2['testing']

    #this crawl in solr is from core aiforsdg and aiforsdg_bal. aiforsdg core -  correctly moved in 020322
    new_crawl_230322_simra = db2['new_crawl_simra_230322']

    path = "/ESID_Nikola/ESID-main/ESIDcrawlers/new_data"

    document_check = []
    #new_crawl_test_270122 = db2['aifordgtest1']  # naming this after the date - 23/11/21. Also, the collection in Mongo as ssir3.
    # ssir3 used for ease to match with core. There is no ssir2 collection, but ssir
    # new_crawl_121121 = db2['ssir']
    # db2.test_collection.insert_many(docs)
    # print("inserted")

    # select all the projects from the database that the firstdatasource matches SSIR
    sel_proj = "SELECT * FROM EDSI.Projects where FirstDataSource like 'SIMRA'"

    #sel_proj = "SELECT * FROM EDSI.Projects where FirstDataSource like 'https://www.aiforsdgs.org/all-projects'"
    cursor.execute(sel_proj)
    results = cursor.fetchall()


    for item in docs:
        website = item['url']
        id_title = item['id']
        try:
            content = item['content']
        except:
            content = "no content"
        version = item['_version_']
        boost= item['boost']
        digest = item['digest']
        try:
            title = item['title']
        except:
            title = "no title"
        timestamp = item['tstamp']
        language = item['lang']

        url_domain = domain_extract(website)
        id_title_match = domain_extract(id_title)
        url_trail = url_trailing(website)
        url_body = replace_url_scheme(website)

        for res in results:
            proj_database_name = res[2]
            proj_database_url = res[11]
            proj_database_id = res[0]

            url_root_db = domain_extract(proj_database_url)
            url_trail_db = url_trailing(proj_database_url)
            url_body_db = replace_url_scheme(proj_database_url)
            url_end_part_db = url_trailing_end(proj_database_url)

            if url_trail_db <= 1:
                if url_domain == url_root_db or id_title_match == url_root_db:

                    # insert into the new collection in mongodb
                    # try:
                    new_crawl_230322_simra.insert_one(
                        {
                        "database_url": proj_database_url,
                        "database_project_id": proj_database_id,
                        "projectname": proj_database_name,
                        "version": version,
                        "boost": boost,
                        "content": content,
                        "digest": digest,
                        "title": title,
                        "timestamp": timestamp,
                        "url": website,
                        "language": language

                        }
                    )

            if url_trail_db > 1:
                if url_body == url_body_db:
                    # insert into the new collection in mongodb
                    # try:
                    new_crawl_230322_simra.insert_one(
                        {
                            "database_url": proj_database_url,
                            "database_project_id": proj_database_id,
                            "projectname": proj_database_name,
                            "version": version,
                            "boost": boost,
                            "content": content,
                            "digest": digest,
                            "title": title,
                            "timestamp": timestamp,
                            "url": website,
                            "language": language

                        }
                    )


            print("updated")


        #url_root = url_break_match(website)
        #print (url_root)
        #website_match = url_root

        #print (url_domain)
        #id_title_match = domain_extract(id_title)

        #document_check.append([url_domain, website, content])

        #doc_check(document_check, path)

        #for res in results:
         #   proj_database_name = res[2]
          #  proj_database_url = res[11]
           # proj_database_id = res[0]
            # print (proj_database_url)

            # find the root of the url for matching
            #url_root_db = domain_extract(proj_database_url)
            #print(url_root_db)

            #if url_root_db != 'http':
             #   if url_root_db in website or url_root_db in id_title:

                    #print("website is:", website, "and the id_title is:", id_title)

               # print(proj_database_id)
              #  print(item)

                # insert into the new collection in mongodb
                   # try:
                    #    new_crawl_230222_test.insert_one(
                     #       {
                      #          "database_url": proj_database_url,
                       #         "database_project_id": proj_database_id,
                        #        "projectname": proj_database_name,
                         #       "version": item['_version_'],
                          #      "boost": item['boost'],
                           #     "content": item['content'],
                            #    "digest": item['digest'],
                             #   "title": item['title'],
                              #  "timestamp": item['tstamp'],
                               # "url": item['url'],
                                #"language": item['lang']

                         #   }
                        #)
                    #except:
                     #   print("missing value")
            #document_check.append([url_domain, url_root_db])

               # print("updated")
