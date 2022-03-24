#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs

from database_access import *
import MySQLdb
import simplejson

#start the main program here
if __name__ == '__main__':
    #declare variable insertSource and assign it False
    insertSource = False
    #declare variable idDataSource and assign it the value - 56
    idDataSource = 56
    #print the line below to indicate start of program run
    print ("Transforming SI drive data")
    #set fname to the string below, which is the json file name
    fname = "si_drive_1005_bycity.json"
    #open the file in fname for reading, as f
    with codecs.open(fname,"rb",encoding='utf-8') as f:
        #declare a variable - se_data and assign it the read file - f, using the read() function
        se_data = f.read()
    #load the json file and assign it to the variable - json_data
    json_data = simplejson.loads(se_data)
    #organisation_type = "Non-profit or Social Enterprise"
    #declare a database connection variable - db
    db = MySQLdb.connect(host, username, password, database, charset='utf8')
    cursor = db.cursor()
    #if insertSource is True, then insert as below
    if insertSource:
        #declare a database insert query to insert the below into the DataSources Table
        #all entries have been provided as strings here
        insertDataSource = "Insert into DataSources (Name,Type,URL,DataIsOpen,RelatedToEU,AssociatedProject,DataDurationStart,DataDurationEnd,Theme,CountryCoverage,SocialInnovationDef,MainEntities,DataSource)" \
                           "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(insertDataSource,("SI-drive","Database","https://mapping.si-drive.eu/","Open","Yes","SI-Drive","2014-01-01","2018-01-01","Social innovation","all, predominantly EU","EC,2013","Projects,Actors","search and case studies"))
        db.commit()
    #declare a variable - project_overlap and initialise it to 0
    project_overlap = 0
    #declare a variable - url_overlap and initialise it to 0
    url_overlap = 0
    #iterate through json_data
    for item in json_data:
        #assign the value at item['city'] to variable - city, and do same for the rest
        city = item['city']
        city_local = item['city_local']
        country = item['country']
        regioon = item['region']
        longitude = item['lon']
        latitude = item['lat']
        #assign the values at item['projects'] to variable - projects_in_city
        projects_in_city = item['projects']
        #iterate through that variable - projects_in_city, as it is a json object with sub entries
        for pro in projects_in_city:
            #set two variables - newProject and newURL to boolean values - True
            newProject = True
            newURL = True
            #declare variable - projectname_en and assign it with the value at pro['projectname_en'], the iterable
            projectname_en = pro['projectname_en']
            #declare variable - project_desc and assign it with the value at pro['description']
            project_desc = pro['description']
            #if project_desc is equal to None, then assign an empty string to project_desc
            if project_desc == None:
                project_desc = ""
            #check if projectname_en is not None
            if projectname_en!= None:
                #in that case, then assign the below to it, which is just utf-8 encoding and replacements
                projectname_en = projectname_en.encode('utf-8').replace('"','').replace("'",'').replace('%','')
            else:
                #else, that is, if it's None, then assign it the value at projectname_orig
                projectname_en=pro['projectname_orig'].encode('utf-8')
            #print the projectname_en
            print (projectname_en)
            #set the variable -projectname_orig to the value at 'projectname_orig' in the iterable
            projectname_orig = pro['projectname_orig']
            #if there is no entry for projectname_orig, then assign projectname_en to it. This appears to be the original
            #project name, vs the projectname in English - projectname_en
            if projectname_orig==None:
                projectname_orig = projectname_en
            #else, assign the encoded value below to it
            else:
                projectname_orig = projectname_orig.encode('utf-8').replace("'",'').replace('"','')
            #implement the sql select query below to chek if the project is already in the database. Select all where the
            #ProjectName is like projectname_en *or like projectname_orig from the Projects table
            existing_pro = "SELECT * from Projects where ProjectName like '%"+projectname_en+"%' or ProjectName like '%"+projectname_orig+"%'"
            #execute the query
            cursor.execute(existing_pro)
            #declare a variable - rows_affected and assign it the count of the retrieved rows, gotten by cursor.rowcount
            rows_affected = cursor.rowcount
            #if the rows_affected variable is not 0, meaning there are some returned rows, then:
            if rows_affected != 0:
                #increment the project_overlap variable declared above
                project_overlap = project_overlap + 1
                #also, declare a variable - newProject and assign it False. This means the project is not new
                newProject == False

            #create a variable -project_stage and assign it the value at ['projectstage'] of the iterable
            project_stage = pro['projectstage']
            #declare a variable website to hold the value at pro['website'] of the iterable as well
            website = pro['website']
            #if the website is not None, meaning there is a website, then check if there is a matching website from the
            #Projects table
            if website !=None:
                #do this check by executing the sql select query below
                matchingUrl = "SELECT * from Projects where ProjectWebpage like '" + website + "'"
                cursor.execute(matchingUrl)
                #create a variable - rows_affected_url and assign it the rowcount
                rows_affected_url = cursor.rowcount
                #encode the value of website and assign it the variable - website
                website = website.encode('utf-8')
                #if the rows_affected_url is not equal to zero, then increment the value of url_overlap, declared above
                # by 1
                if rows_affected_url != 0:
                    url_overlap = url_overlap + 1
                    #set newURL to False, as the URL already exists
                    newURL = False
            #assign the value ['year'] in the iterable to the variable - year
            year = pro['year']
            #declare date and assign it the year , converted to a string, and concatenated with "-01-01"
            date = str(year) + "-01-01"
            #but if newProject stayed True, then do the following:
            if newProject:
                #print out the projectname, date and website, seperated by space
                print(projectname_en+" "+date+ " "+str(website))
                #declare an insert query to insert into the Projects table the following. Set the FirstDataSource to be equal
                #to the string - "SI-Drive"
                newProjectQuery = "Insert into Projects (ProjectName,DateStart,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}',{4})".format(projectname_en,date,website,"SI-drive",idDataSource)
                #execute the query
                cursor.execute(newProjectQuery)
                #set the project id here, using the cursor.lastrowid
                projectid = cursor.lastrowid
                #commit to the database
                db.commit()
            else:
                #if the project is not new, and newProject had changed above to False, then implement an update query instead
                #update the projects table and set the DateStart to -date-, and update the website and the rest, where the project
                #name matches the project in question
                UpdateProjectQuery = "Update Projects set DateStart='"+date+"', ProjectWebpage='"+website+"',FirstDataSource='"+"SI-drive"+"',DataSources_idDataSources="+idDataSource+" where ProjectName='"+projectname_en+"'"
                cursor.execute(UpdateProjectQuery)
                #set the projectid using the lastrowid
                projectid = cursor.lastrowid
                db.commit()
            #implement another sql insert query to insert into the table - AdditionalProjectData the following -
            #FieldName as string - "Description", and the value being the project_desc.encode('utf-8') and the Projects_
            #idProjects set to projectid, which was derived from lastrowid above
            InsertDesc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES ('{0}','{1}','{2}',NOW())".format("Description",project_desc.encode('utf-8').replace("'",''),str(projectid))
            #execute the query and commit it
            cursor.execute(InsertDesc)
            db.commit()
            #implement another sql query to insert into the ProjectLocation table what is below:Type as "Main", city
            #country, etc, and the Projects_idProjects as projectid
            InsertLocation = "Insert into ProjectLocation (Type,City,Country,Longitude,Latitude,Projects_idProjects) VALUES ('{0}','{1}','{2}',{3},{4},{5})".format("Main",city.encode('utf-8').replace("'",""),country.encode('utf-8').replace("'",""),longitude,latitude,str(projectid))
            #execute and commit
            cursor.execute(InsertLocation)
            db.commit()
            #recall, this is still under the project iteration; set a variable - partner_main and assign it the entry/value
            #at ['partners']['main']
            partner_main = pro['partners']['main']
            #if partner_main is not an empty string, as there are some that are empty strings, then;
            if partner_main != {}:
                #set a variable - main_partner_name and assign it the value at ['name'] under partner_main and replace the
                #' with an empty string
                main_partner_name = partner_main['name'].encode('utf-8').replace("'",'')
                #do the same for main_partner_sector, set to the entry at partner_main['sector']
                main_partner_sector = partner_main['sector']
                #if main_partner_sector is not None, then
                if main_partner_sector!= None:
                    #encode the main_partner_sector and assign this to the variable - main_partner_sector
                    main_partner_sector = main_partner_sector.encode('utf-8')
                #declare a variable - main_partner_country and assign it the value at partner_main[country]
                main_partner_country = partner_main['country']
                #if main_partner_country is not None, that is, it exists, then
                if main_partner_country != None:
                    #encode the value at main_partner_country and assign it to main_partner_country
                    main_partner_country = main_partner_country.encode('utf-8').replace("'", "")
                #declare variable - PartnerExists, and assign it the value - False
                PartnerExists = False
                #declare an sql select query to select all from Actors, where the ActorName matches the main_partner_name
                SelectPartner  = "Select * from Actors where ActorName like '%"+main_partner_name+"%'"
                cursor.execute(SelectPartner)
                #set variable -rows_affected_mainPartner and assign it the rowcount from the select query
                rows_affected_mainPartner = cursor.rowcount
                #if the rows_affected_mainPartner is greater than 0, meaning, there is an Actor that matches the main_
                #partner_name
                if rows_affected_mainPartner>0:
                    #declare a variable - row, to hold the row fetched from the Actor table
                    row = cursor.fetchone()
                    #assign the value at index 0 of that row to partner_id, as that ros is the idActors row in the table
                    parner_id = row[0]
                #else, meaning there is no Actor matching the main_partner_name in the table;
                else:
                    #implement an sql insert query to insert into the Actors table the following.
                    InsertParner = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,DataSources_idDataSources)" \
                                   " Values ('{0}','{1}','{2}','{3}',{4})".format(main_partner_name,"S",main_partner_sector,"SI-Drive",str(idDataSource))
                    #implement the query and commit
                    cursor.execute(InsertParner)
                    db.commit()
                    #set the lastrowid to partner_id
                    parner_id = cursor.lastrowid
                    #declare an sql insert query and insert into ActorLocation table the following - Type, Country and
                    #Actors_idActors
                    ParnerLocation = "Insert into ActorLocation (Type,Country, Actors_idActors) Values('{0}','{1}',{2})".format("Headquarters",main_partner_country,str(parner_id))
                    cursor.execute(ParnerLocation)
                    db.commit()
                #declare another sql insert query -Connection, to insert into Actors_has_Projects the following; partner_id
                #as the Actors_idActors, and the projectid as Projects_idProjects, and the string - "Main Partner" as the
                #organisation role
                Connection = "Insert into Actors_has_Projects (Actors_idActors,Projects_idProjects,OrganisationRole) Values ({0},{1},'{2}')".format(parner_id,projectid,"Main partner")
                cursor.execute(Connection)
                db.commit()
            #in order to take care of the 'others' section of the partners in the json file,declare a variable - other_partners
            #to hold the value at ['partners']['others']
            other_partners = pro['partners']['others']
            #iterate through other_partners
            for o_partner in other_partners:
                #declare a variable - o_partner_name to hold the value at o_partner['name'], encoded and with the ' replaced
                #with an empty string. Do the same for 'sector' and 'country'
                o_partner_name = o_partner['name'].encode('utf-8').replace("'","")
                o_partner_sector = o_partner['sector']
                o_partner_country = o_partner['country']
                #for that iterable in question, declare and implement an sql select query to select all from the Actors table
                #where the ActorName matches the name at o_partner_name
                SelectPartner2 = "Select * from Actors where ActorName like '%" + o_partner_name + "%'"
                #execute the query
                cursor.execute(SelectPartner2)
                #declare a variable - rows_affected_oPartner to hold the rowcount
                rows_affected_oPartner = cursor.rowcount
                #if the rows_affectedoPartner is greater than 0, meaning the other partner is in the Actors table, then
                if rows_affected_oPartner > 0:
                    #fecth one of the rows, and assign it to the variable - row
                    row = cursor.fetchone()
                    #return the value at index 0 of row to the variable -parner_id. This is the idActors column
                    parner_id = row[0]
                else:
                    #else, that is, if there otherpartner is not in the returned result
                    #implement an sql insert query to insert the below into Actors table
                    InsertParner = "Insert into Actors (ActorName,Type,SubType,SourceOriginallyObtained,DataSources_idDataSources)" \
                                   " Values ('{0}','{1}','{2}','{3}',{4})".format(o_partner_name, "S", o_partner_sector, "SI-Drive", str(idDataSource))
                    #execute the query and commit the result
                    cursor.execute(InsertParner)
                    db.commit()
                    #assign the lastrowid to the partner_id
                    parner_id = cursor.lastrowid
                    #insert the partner location into the ActorLocation table using the insert query below
                    ParnerLocation = "Insert into ActorLocation (Type,Country, Actors_idActors) Values('{0}','{1}',{2})".format("Headquarters", o_partner_country, str(parner_id))
                    cursor.execute(ParnerLocation)
                    db.commit()
                try:
                    #declare another sql insert query and insert into table - Actors_has_Projects the following;
                    Connection = "Insert into Actors_has_Projects (Actors_idActors,Projects_idProjects,OrganisationRole) Values ({0},{1},'{2}')".format(str(parner_id), str(projectid), "Other partner")
                    #execute the query and commit
                    cursor.execute(Connection)
                    db.commit()
                #if there is an exception, print the string below
                except Exception:
                    print ("Existing pair")
    #print out the project_overlap and the url_overlap
    print (project_overlap)
    print (url_overlap)



