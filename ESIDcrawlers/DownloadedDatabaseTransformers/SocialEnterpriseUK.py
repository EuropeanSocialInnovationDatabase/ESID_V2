#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

from database_access import *
import MySQLdb
import sys
import simplejson
import datetime

#if this is the main program, as this is, then implement this
if __name__ == '__main__':
    #print this to signify program start. It's just a check
    print ("Transforming Social Enterprise UK data")
    #declare variable - fname and assign it the json file name
    fname = "SocialEnterpriseUK.json"
    #open the file for reading, as f
    with codecs.open(fname,"rb",encoding='utf-8') as f:
        #decclare a variable to hold the read file - se_data
        se_data = f.read()
    #print the read data - se_data
    print (se_data)
    #load the data - se_data with simplejson and assign the loaded data to the variable - json_data
    json_data = simplejson.loads(se_data)
    #declare a variable- organisation_type and assign it a string - "Non-profit or Social Enterprise"
    organisation_type = "Non-profit or Social Enterprise"
    #declare a database connection variable - db
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()


    #sql = "INSERT INTO DataSources(`Name`, `Type`, 'URL', DataIsOpen, RelatedToEU, AssociatedProject, " \
    #      "Theme, CountryCoverage, SocialInnovationDef, MainEntities, DataSource,InclusionCriteria) VALUES('Digital Social Innovation Database', " \
    #      "'Network', 'https://www.socialenterprise.org.uk','Open but not downloadable', 'No', null,  " \
    #      "'social enterprises','all, predominantly UK', null," \
    #      "'Organisations', null, 'voluntary participation');"
    #cursor.execute(sql)
    #db.commit()

    #iterate through json_data, which is where the se_data was stored in
    for item in json_data:
        #print the item which is the current iterable, to ensure that it's correct
        print (item)
        #assign the item at this position to the variable - latitude
        latitude = item[1][0][0][0]
        #assign the item at this position to the variable - longitude
        longitude = item[1][0][0][1]
        #print out the longitude, converted to a string, concatenated to the string - "Long"
        print ("Long:"+str(longitude))
        #print out the latitude, converted to a string, concatenated to the string - "Lat"
        print ("Lat:"+str(latitude))
        #assign the item at this position to the variable - name
        name = item[5][0][1][0]
        #print out the string below, concatenated with name
        print (u"Name:" + name)
        #assign the item at the index below to the variable - post
        post  = item[5][3][0][1][0]
        #print out the string - u"Post:", concatenated with the variable - post
        print (u"Post:" + post)
        #if the length of the item at index [5][3] is greater than 1
        if len(item[5][3])>1:
            #assign the variable website with item[5][3][1][1][0]
            website = item[5][3][1][1][0]
            #print out the string - "Web:", concatenated with website, converted to a string
            print ("Web:"+str(website))
        else:
            #else, assign an empty string to the variable - website
            website = ""
        #declare an sql variable - sql_org and assign it an insert query, which inserts the details below into the Actors
        #table. SubType is organisation_type and SourceOriginallyObtained is the string 'Social Enterprise UK', also
        #enter the website from above
        sql_org = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,ActorWebsite," \
                  "DataSources_idDataSources) VALUES (%s,%s,%s,%s,%s,%s)"
        #execute the query
        cursor.execute(sql_org, (name, 'S', organisation_type,
                                 'Social Enterprise UK',
                                 website,  2))
        #declare a variable - org_id_inTable and assign it with cursor.lastrowid, used to set the id aftter the insert
        org_id_inTable = cursor.lastrowid
        #assign this org_id_inTable to the database_id and commit it
        database_id = org_id_inTable
        db.commit()
        #I just converted the table name here from 'Location' to 'ActorLocation' - RA - 12/05/21
        #implement the sql Insert query below and insert the details to the ActorLocation table
        sql_loc = "Insert into ActorLocation (Type,Address,Longitude,Latitude,Actors_idActors) VALUES " \
                  "(%s,%s,%s,%s,%s)"
        cursor.execute(sql_loc,("Headquarters",post,
                                longitude,latitude,database_id))
        db.commit()


