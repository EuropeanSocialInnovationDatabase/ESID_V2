from database_access import *
import codecs
import csv
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import cgi
import MySQLdb

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


# def get_netloc(u):
#   if not u.startswith('http'):
#      u = '//' + u
# return urlparse(u).netloc

if __name__ == '__main__':

    with open("ashoka2.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_links = []
        all_project_ids = []
        #ashoka_projectids = []
        for row in reader:
            if row[7] != "" and row[3] != "":
                if row[4] != "" or row[5] != "" or row[6] != "":
                    link = row[3]
                    corrected_url = print_correct(link)
                    print (corrected_url)
                    right_link = corrected_url
                    country = row[0]
                    description = row[2] + '' + row[4] + '' + row[5] + '' + row[6]
                    title = row[7].replace("'", "''")

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
                        project_insert = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor.execute(project_insert, (title, right_link, 'https://www.ashoka.org/en-gb/our-network?field_network_member_type_value=All&field_country_target_id=All&title=&field_topics_target_id=All&field_link_title=&page=0', 71))
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


                    else:

                        print('Project already exists!')
                        print(title)


                    all_links.append(corrected_url)
                    url_check(corrected_url)
        #location_update()

    with open("Water_For_Food_combined.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_water_links = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                link2 = row[1]
                corrected_url2 = print_correct(link2)
                print (corrected_url2)
                right_link2 = corrected_url2
                country2 = row[4]
                description2 = row[5]
                title2 = row[0].replace("'", "''")

                #print a check here
                print(title2,description2,country2, right_link2)

                db = MySQLdb.connect(host, username, password, database, charset='utf8')
                cursor2 = db.cursor()
                new_project2 = True

                proj_check2 = "SELECT * from Projects where ProjectName like '%" + title2 + "%'"
                cursor2.execute(proj_check2)
                num_rows2 = cursor2.rowcount
                if num_rows2 != 0:
                    new_project2 = False

                url_compare2 = "SELECT * from Projects where ProjectWebpage like '" + right_link2 + "'"
                cursor2.execute(url_compare2)
                num_rows2 = cursor2.rowcount
                if num_rows2 != 0:
                    new_project2 = False



                if new_project2:
                    project_insert2 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                    cursor2.execute(project_insert2, (title2, right_link2, 'https://securingwaterforfood.org/innovators', 73))
                    projectid2 = cursor2.lastrowid
                    print(projectid2)
                    #ashoka_projectids.append(projectid)
                    db.commit()

                    ins_desc2 = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
                    cursor2.execute(ins_desc2, ("Description", description2, str(projectid2)))
                    db.commit()

                    ins_location2 = "Insert into ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)"
                    cursor2.execute(ins_location2, ("Main", country2, str(projectid2)))
                    db.commit()

                else:
                    print('Project already exists!')
                    print(title2)

                all_water_links.append(corrected_url2)
                url_check(corrected_url2)

    with open("Kaplan_combined.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_kaplan_links = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                link3 = row[1]
                corrected_url3 = print_correct(link3)
                print(corrected_url3)
                right_link3 = corrected_url3
                country3 = row[4]
                description3 = row[2]
                title3 = row[0].replace("'", "''")

                #print a check here
                print(title3,description3,country3, right_link3)

                db = MySQLdb.connect(host, username, password, database, charset='utf8')
                cursor3 = db.cursor()
                new_project3 = True

                proj_check3 = "SELECT * from Projects where ProjectName like '%" + title3 + "%'"
                cursor3.execute(proj_check3)
                num_rows3 = cursor3.rowcount
                if num_rows3 != 0:
                    new_project3 = False

                url_compare3 = "SELECT * from Projects where ProjectWebpage like '" + right_link3 + "'"
                cursor3.execute(url_compare3)
                num_rows3 = cursor3.rowcount
                if num_rows3 != 0:
                    new_project3 = False

                if new_project3:
                    project_insert3 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                    cursor3.execute(project_insert3, (title3, right_link3, 'https://www.jmkfund.org/innovation-prize-past-awardees/', 74))
                    projectid3 = cursor3.lastrowid
                    print(projectid3)
                    #ashoka_projectids.append(projectid)
                    db.commit()

                    ins_desc3 = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
                    cursor3.execute(ins_desc3, ("Description", description3, str(projectid3)))
                    db.commit()

                    ins_location3 = "Insert into ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)"
                    cursor3.execute(ins_location3, ("Main", country3, str(projectid3)))
                    db.commit()

                else:
                    print('Project already exists!')
                    print(title3)

                all_kaplan_links.append(corrected_url3)
                url_check(corrected_url3)

    with open("Abhingya_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Abhi_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "":
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link4 = row[8]
                    corrected_url4 = print_correct(link4)
                    print(corrected_url4)
                    right_link4 = corrected_url4
                    #country3 = row[4]
                    #description3 = row[2]
                    title4 = row[6].replace("'", "''")

                    #print a check here
                    print(title4,right_link4)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor4 = db.cursor()
                    new_project4 = True

                    proj_check4 = "SELECT * from Projects where ProjectName like '%" + title4 + "%'"
                    cursor4.execute(proj_check4)
                    num_rows4 = cursor4.rowcount
                    if num_rows4 != 0:
                        new_project4 = False

                    url_compare4 = "SELECT * from Projects where ProjectWebpage like '" + right_link4 + "'"
                    cursor4.execute(url_compare4)
                    num_rows4 = cursor4.rowcount
                    if num_rows4 != 0:
                        new_project4 = False

                    if new_project4:
                        project_insert4 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor4.execute(project_insert4, (title4, right_link4, 'SSIR', 72))
                        projectid4 = cursor4.lastrowid
                        print(projectid4)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title4)

                    all_Abhi_SSIR_links.append(corrected_url4)
                    url_check(corrected_url4)

    with open("Arran_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Arran_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "":
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link5 = row[8]
                    corrected_url5 = print_correct(link5)
                    print(corrected_url5)
                    right_link5 = corrected_url5.replace("'", "''")
                    #country3 = row[4]
                    #description3 = row[2]
                    title5 = row[6].replace("'", "''")

                    #print a check here
                    print(title5,right_link5)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor5 = db.cursor()
                    new_project5 = True

                    proj_check5 = "SELECT * from Projects where ProjectName like '%" + title5 + "%'"
                    cursor5.execute(proj_check5)
                    num_rows5 = cursor5.rowcount
                    if num_rows5 != 0:
                        new_project5 = False

                    url_compare5 = "SELECT * from Projects where ProjectWebpage like '" + right_link5 + "'"
                    cursor5.execute(url_compare5)
                    num_rows5 = cursor5.rowcount
                    if num_rows5 != 0:
                        new_project5 = False

                    if new_project5:
                        project_insert5 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor5.execute(project_insert5, (title5, right_link5, 'SSIR', 72))
                        projectid5 = cursor5.lastrowid
                        print(projectid5)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title5)

                    all_Arran_SSIR_links.append(corrected_url5)
                    url_check(corrected_url5)

    with open("Christopher_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Chris_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row [8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link6 = row[8]
                    corrected_url6 = print_correct(link6)
                    print(corrected_url6)
                    right_link6 = corrected_url6.replace("'", "''")
                    #country3 = row[4]
                    #description3 = row[2]
                    title6 = row[6].replace("'", "''")

                    #print a check here
                    print(title6,right_link6)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor6 = db.cursor()
                    new_project6 = True

                    proj_check6 = "SELECT * from Projects where ProjectName like '%" + title6 + "%'"
                    cursor6.execute(proj_check6)
                    num_rows6 = cursor6.rowcount
                    if num_rows6 != 0:
                        new_project6 = False

                    url_compare6 = "SELECT * from Projects where ProjectWebpage like '" + right_link6 + "'"
                    cursor6.execute(url_compare6)
                    num_rows6 = cursor6.rowcount
                    if num_rows6 != 0:
                        new_project6 = False

                    if new_project6:
                        project_insert6 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor6.execute(project_insert6, (title6, right_link6, 'SSIR', 72))
                        projectid6 = cursor6.lastrowid
                        print(projectid6)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title6)

                    all_Chris_SSIR_links.append(corrected_url6)
                    url_check(corrected_url6)

    with open("Godfrey_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []
        all_Godfrey_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row [8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link7 = row[8]
                    corrected_url7 = print_correct(link7)
                    print(corrected_url7)
                    right_link7 = corrected_url7.replace("'", "''")
                    # country3 = row[4]
                    # description3 = row[2]
                    title7 = row[6].replace("'", "''")

                    # print a check here
                    print(title7, right_link7)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor7 = db.cursor()
                    new_project7 = True

                    proj_check7 = "SELECT * from Projects where ProjectName like '%" + title7 + "%'"
                    cursor7.execute(proj_check7)
                    num_rows7 = cursor7.rowcount
                    if num_rows7 != 0:
                        new_project7 = False

                    url_compare7 = "SELECT * from Projects where ProjectWebpage like '" + right_link7 + "'"
                    cursor7.execute(url_compare7)
                    num_rows7 = cursor7.rowcount
                    if num_rows7 != 0:
                        new_project7 = False

                    if new_project7:
                        project_insert7 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor7.execute(project_insert7, (title7, right_link7, 'SSIR', 72))
                        projectid7 = cursor7.lastrowid
                        print(projectid7)
                        # ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title7)

                    all_Godfrey_SSIR_links.append(corrected_url7)
                    url_check(corrected_url7)

    with open("Grace_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Grace_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row [8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link8 = row[8]
                    corrected_url8 = print_correct(link8)
                    print(corrected_url8)
                    right_link8 = corrected_url8.replace("'", "''")
                    #country3 = row[4]
                    #description3 = row[2]
                    title8 = row[6].replace("'", "''")

                    #print a check here
                    print(title8,right_link8)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor8 = db.cursor()
                    new_project8 = True

                    proj_check8 = "SELECT * from Projects where ProjectName like '%" + title8 + "%'"
                    cursor8.execute(proj_check8)
                    num_rows8 = cursor8.rowcount
                    if num_rows8 != 0:
                        new_project8 = False

                    url_compare8 = "SELECT * from Projects where ProjectWebpage like '" + right_link8 + "'"
                    cursor8.execute(url_compare8)
                    num_rows8 = cursor8.rowcount
                    if num_rows8 != 0:
                        new_project8 = False

                    if new_project8:
                        project_insert8 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor8.execute(project_insert8, (title8, right_link8, 'SSIR', 72))
                        projectid8 = cursor8.lastrowid
                        print(projectid8)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title8)

                    all_Grace_SSIR_links.append(corrected_url8)
                    url_check(corrected_url8)

    with open("Holly_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []
        all_Holly_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row[8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link9 = row[8]
                    corrected_url9 = print_correct(link9)
                    print(corrected_url9)
                    right_link9 = corrected_url9.replace("'", "''")
                    # country3 = row[4]
                    # description3 = row[2]
                    title9 = row[6].replace("'", "''")

                    # print a check here
                    print(title9, right_link9)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor9 = db.cursor()
                    new_project9 = True

                    proj_check9 = "SELECT * from Projects where ProjectName like '%" + title9 + "%'"
                    cursor9.execute(proj_check9)
                    num_rows9 = cursor9.rowcount
                    if num_rows9 != 0:
                        new_project9 = False

                    url_compare9 = "SELECT * from Projects where ProjectWebpage like '" + right_link9 + "'"
                    cursor9.execute(url_compare9)
                    num_rows9 = cursor9.rowcount
                    if num_rows9 != 0:
                        new_project9 = False

                    if new_project9:
                        project_insert9 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor9.execute(project_insert9, (title9, right_link9, 'SSIR', 72))
                        projectid9 = cursor9.lastrowid
                        print(projectid9)
                        # ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title9)

                    all_Holly_SSIR_links.append(corrected_url9)
                    url_check(corrected_url9)

    with open("Trial_Run_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Trial_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row [8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link10 = row[8]
                    corrected_url10 = print_correct(link10)
                    print(corrected_url10)
                    right_link10 = corrected_url10.replace("'", "''")
                    #country3 = row[4]
                    #description3 = row[2]
                    title10 = row[6].replace("'", "''")

                    #print a check here
                    print(title10,right_link10)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor10 = db.cursor()
                    new_project10 = True

                    proj_check10 = "SELECT * from Projects where ProjectName like '%" + title10 + "%'"
                    cursor10.execute(proj_check10)
                    num_rows10 = cursor10.rowcount
                    if num_rows10 != 0:
                        new_project10 = False

                    url_compare10 = "SELECT * from Projects where ProjectWebpage like '" + right_link10 + "'"
                    cursor10.execute(url_compare10)
                    num_rows10 = cursor10.rowcount
                    if num_rows10 != 0:
                        new_project10 = False

                    if new_project10:
                        project_insert10 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor10.execute(project_insert10, (title10, right_link10, 'SSIR', 72))
                        projectid10 = cursor10.lastrowid
                        print(projectid10)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title10)

                    all_Trial_SSIR_links.append(corrected_url10)
                    url_check(corrected_url10)

    with open("Theofani_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Theofani_SSIR_links = []

        for row in reader:
            if row[6] != "" and row[8] != "" and row[8] != 'Nill' and row [8] != 'Nil':
                if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                    link11 = row[8]
                    corrected_url11 = print_correct(link11)
                    print(corrected_url11)
                    right_link11 = corrected_url11.replace("'", "''")
                    #country3 = row[4]
                    #description3 = row[2]
                    title11 = row[6].replace("'", "''")

                    #print a check here
                    print(title11,right_link11)

                    db = MySQLdb.connect(host, username, password, database, charset='utf8')
                    cursor11 = db.cursor()
                    new_project11 = True

                    proj_check11 = "SELECT * from Projects where ProjectName like '%" + title11 + "%'"
                    cursor11.execute(proj_check11)
                    num_rows11 = cursor11.rowcount
                    if num_rows11 != 0:
                        new_project11 = False

                    url_compare11 = "SELECT * from Projects where ProjectWebpage like '" + right_link11 + "'"
                    cursor11.execute(url_compare11)
                    num_rows11 = cursor11.rowcount
                    if num_rows11 != 0:
                        new_project11 = False

                    if new_project11:
                        project_insert11 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources) VALUES (%s,%s,%s,%s)"
                        cursor11.execute(project_insert11, (title11, right_link11, 'SSIR', 72))
                        projectid11 = cursor11.lastrowid
                        print(projectid11)
                        #ashoka_projectids.append(projectid)
                        db.commit()


                    else:
                        print('Project already exists!')
                        print(title11)

                    all_Theofani_SSIR_links.append(corrected_url11)
                    url_check(corrected_url11)

    with open("Skoll_final.csv", 'r',encoding = "ISO-8859-1") as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []
        all_Skoll_links = []

        for row in reader:
            if row[1] != "" and row[7] != "" and row[7] != 'Nill' and row [7] != 'Nil':
                #if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                link12 = row[7]
                corrected_url12 = print_correct(link12)
                print(corrected_url12)
                right_link12 = corrected_url12.replace("'", "''")
                country12 = row[4].encode('utf-8') #added to fix encoding problems before adding in the database
                description12 = row[8] + '' + row[10] + '' + row[11]
                title12 = row[1].replace("'", "''")
                facebook = row[5]
                twitter = row[6]


                #print a check here
                print(title12,right_link12)

                db = MySQLdb.connect(host, username, password, database, charset='utf8')
                cursor12 = db.cursor()
                new_project12 = True

                proj_check12 = "SELECT * from Projects where ProjectName like '%" + title12 + "%'"
                cursor12.execute(proj_check12)
                num_rows12 = cursor12.rowcount
                if num_rows12 != 0:
                    new_project12 = False

                url_compare12 = "SELECT * from Projects where ProjectWebpage like '" + right_link12 + "'"
                cursor12.execute(url_compare12)
                num_rows12 = cursor12.rowcount
                if num_rows12 != 0:
                    new_project12 = False

                if new_project12:
                    project_insert12 = "Insert into Projects (ProjectName,ProjectWebpage,FirstDataSource,DataSources_idDataSources, FacebookPage, ProjectTwitter) VALUES (%s,%s,%s,%s,%s,%s)"
                    cursor12.execute(project_insert12, (title12, right_link12, 'SKOLL', 75, facebook, twitter))
                    projectid12 = cursor12.lastrowid
                    print(projectid12)
                    #ashoka_projectids.append(projectid)
                    db.commit()

                    ins_desc12 = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained) VALUES (%s,%s,%s,NOW())"
                    cursor12.execute(ins_desc12, ("Description", description12, str(projectid12)))
                    db.commit()

                    ins_location12 = "Insert into ProjectLocation (Type,Country,Projects_idProjects) VALUES (%s,%s,%s)"
                    cursor12.execute(ins_location12, ("Main", country12, str(projectid12)))
                    db.commit()



                else:
                    print('Project already exists!')
                    print(title12)

                all_Skoll_links.append(corrected_url12)
                url_check(corrected_url12)



    #print out ashoka's links to a file for crawling later
    with open('ashoka_links', 'w', newline='') as f:
        write = csv.writer(f)
        for row in all_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write.writerow(columns)

    with open('securing_water_links', 'w', newline='') as f:
        write2 = csv.writer(f)
        for row in all_water_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write2.writerow(columns)

    with open('kaplan_links', 'w', newline='') as f:
        write3 = csv.writer(f)
        for row in all_kaplan_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write3.writerow(columns)

    with open('SSIR1_links', 'w', newline='') as f:
        write4 = csv.writer(f)
        for row in all_Abhi_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write4.writerow(columns)

    with open('SSIR2_links', 'w', newline='') as f:
        write5 = csv.writer(f)
        for row in all_Arran_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write5.writerow(columns)

    with open('SSIR3_links', 'w', newline='') as f:
        write6 = csv.writer(f)
        for row in all_Chris_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write6.writerow(columns)

    with open('SSIR4_links', 'w', newline='') as f:
        write7 = csv.writer(f)
        for row in all_Godfrey_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write7.writerow(columns)

    with open('SSIR5_links', 'w', newline='') as f:
        write8 = csv.writer(f)
        for row in all_Grace_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write8.writerow(columns)

    with open('SSIR6_links', 'w', newline='') as f:
        write9 = csv.writer(f)
        for row in all_Holly_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write9.writerow(columns)

    with open('SSIR7_links', 'w', newline='') as f:
        write10 = csv.writer(f)
        for row in all_Trial_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write10.writerow(columns)

    with open('SSIR8_links', 'w', newline='') as f:
        write11 = csv.writer(f)
        for row in all_Theofani_SSIR_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write11.writerow(columns)

    #print out skoll's links to a file for crawling later
    with open('Skoll_links', 'w', newline='') as f:
        write = csv.writer(f)
        for row in all_Skoll_links:
            columns = [c.strip() for c in row.strip(', ').split(',')]
            write.writerow(columns)
