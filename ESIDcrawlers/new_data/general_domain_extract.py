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
    #result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    #result = url.replace("https://", "").replace("http://", "").replace("www.","")
    result = '{uri.netloc}/'.format(uri=parsed_uri)
    #url_end = url.split("/")[-3:]
    url_end = url.split("/")[3:]
    print('result is', result)
    print(url_end)
    print('The length of the URL is:' ,len(url_end))
    #return result

def domain_extract(url):
    ext = tldextract.extract(url)
    domain_name = ext.domain
    domain_name = domain_name.strip()
    #return domain_name
    print (ext)
    print (domain_name)

if  __name__ == '__main__':
    #url = "https://www.facebook.com/CIRSYS"
    #url = "//www.upch.edu.pe/bioinformatic/anemia/app"
    #url = "https://www.cais.usc.edu/wp-content/uploads/2017/07/IAAI_2014.pdf"
    #url = "http://www.amanda-care.com"
    #url = "http://ialab.com.ar"
    #url = "https://five.ai/ "
    url = "https://research.csiro.au/spark/"
    domain_extract(url)
    url_break_match(url)