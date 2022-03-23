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

def count_ashoka ():
    projects_num = 0
    project_withdesc = 0
    project_no_country = 0

    with open("ashoka2.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")
        #print (row[7])
        #rowlist = []

        for row in reader:
            if row[7] != "" and row[3] != "":
                projects_num = projects_num + 1
                if row [2] != "" or row[4] != "" or row[5] != "" or row[6] != "":
                    project_withdesc = project_withdesc + 1
                    if row[0] == "":
                        project_no_country = project_no_country + 1
                        print (row[1])

    print ("projects number is: ", projects_num)
    print ("Ashoka projects with descriptions: ", project_withdesc)
    print("Ashoka projects with no country: ", project_no_country)
    return projects_num

def count_SSIR():
    chris_count = 0
    arran_count = 0
    godfrey_count = 0
    abhi_count = 0
    grace_count = 0
    holly_count = 0
    total_SSIR = 0
    with open("Christopher_SSIR.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print ("project running")

        for row in reader:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                chris_count = chris_count + 1
        print("Chris count is", chris_count)

    with open("Arran_SSIR.csv", 'r') as file:
        reader2 = csv.reader(file)
        next(reader2, None)
        print ("check")

        for row in reader2:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                arran_count = arran_count + 1
        print("Arran count is", arran_count)

    with open("Abhingya_SSIR.csv", 'r') as file:
        reader3 = csv.reader(file)
        next(reader3, None)
        print ("check")

        for row in reader3:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                abhi_count = abhi_count + 1
        print("Abhi count is", abhi_count)

    with open("Godfrey_SSIR.csv", 'r') as file:
        reader4 = csv.reader(file)
        next(reader4, None)
        print ("check")

        for row in reader4:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                godfrey_count = godfrey_count + 1
        print("Godfrey count is", godfrey_count)

    with open("Grace_SSIR.csv", 'r') as file:
        reader5 = csv.reader(file)
        next(reader5, None)
        print ("check")

        for row in reader5:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                grace_count = grace_count + 1
        print("Grace count is", grace_count)

    with open("Holly_SSIR.csv", 'r') as file:
        reader6 = csv.reader(file)
        next(reader6, None)
        print ("check")

        for row in reader6:
            if row[7] == "project" or row[7] == "Project" or row[7] == "both" or row[7] == "Both":
                holly_count = holly_count + 1
        print("Holly count is", holly_count)

    total_SSIR = chris_count + holly_count + grace_count + godfrey_count + abhi_count + arran_count

    print ("The total SSIR is: ", total_SSIR)
    return total_SSIR

def count_SecuringWater():

    projects_count = 0
    projects_count2 = 0
    projects_with_desc = 0
    projects_with_desc2 = 0


    with open("Godfrey_WaterForFood.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                projects_count = projects_count + 1
                if row[5] != "":
                    projects_with_desc = projects_with_desc + 1

    with open("Abhi_WaterForFood.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                projects_count2 = projects_count2 + 1
                if row[5] != "":
                    projects_with_desc2 = projects_with_desc2 + 1

    total_water_for_food = projects_count + projects_count2
    print("Water for food projects total is: ", total_water_for_food)
    print("Water for food projects with descriptions: ", projects_with_desc + projects_with_desc2)
    return total_water_for_food


def count_Kaplan():

    projects_count = 0
    projects_count2 = 0
    projects_with_desc = 0
    projects_with_desc2 = 0

    with open("Godfrey_kaplan.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                projects_count = projects_count + 1
                if row[2] != "":
                    projects_with_desc = projects_with_desc + 1

    with open("Abhi_Kaplan.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader, None)
        print("project running")
        # print (row[7])
        # rowlist = []

        for row in reader:
            if row[0] != "" and row[1] != "":
                projects_count2 = projects_count2 + 1
                if row[2] != "":
                    projects_with_desc2 = projects_with_desc2 + 1

    total_kaplan = projects_count + projects_count2
    print("Kaplan total is: ", total_kaplan)
    print("Kaplan projects with descriptions: ", projects_with_desc + projects_with_desc2)
    return total_kaplan




ashoka = count_ashoka()
SSIR = count_SSIR()
Securing_Water = count_SecuringWater()
Kaplan = count_Kaplan()

Total_of_projects = ashoka + SSIR + Securing_Water + Kaplan

print ("The total number of projects is: ", Total_of_projects)
