from pymongo import MongoClient
import MySQLdb
import pandas as pd
from database_access import *
from os import listdir
from os.path import isfile, join
import os


def comp_frames():
    #df1 = pd.read_csv("/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/Uncrawled_aiforsdglinks.csv", names=['url'], quotechar="'", skipinitialspace=True)
    #df2 = pd.read_csv("/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/Uncrawled_aiforsdglinks2.csv", names=['match'])

    df1 = pd.read_csv("/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/Uncrawled_ssirfinal1.csv")
    df2 = pd.read_csv("/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/Final_Uncrawled_ssirfinal2.csv")

    #merge to create dataframe that holds links common to both dataframes
    df3 = df1.merge(df2, how='inner', indicator=False)
    
    #df3 = pd.merge(df1, df2, left_on=df1['url'], right_on=df2['match'], how='inner')

    print(df3)
    df3.to_csv(os.path.join(path, r'Uncrawled_ssir_updated.csv'))


if  __name__ == '__main__':
    path = "/ESID_Nikola/ESID-main/ESIDcrawlers/new_data"

    df = pd.read_csv("/ESID_Nikola/ESID-main/ESIDcrawlers/new_data/ssir_final2_140322.csv")
    print(df.head())

    df_uncrawled = df.loc[df['Document Length'] <= 1000]

    #count of the number of cells with zeros
    count_zeros = (df['Document Length'] == 0).sum()
    count_1000 =(df['Document Length'] <= 1000).sum()
    #count of projects with count less than or equal to 500
    count_200 = (df['Document Length'] <= 200).sum()

    print('Count of zeros in Column  Document Length : ', count_zeros)
    print('Count of projects with count less than or equal to 200 : ',count_200)
    print('Count of projects with count less than or equal to 1000: ',count_1000)

    print (df_uncrawled.head())
    #print (df_uncrawled[['Project_id','url']])

    #to get the uncrawled urls
    df_uncrawled_urls = df_uncrawled['url']

    #to get the uncrawled urls and project_ids
    df_uncrawled_projects = df_uncrawled[['Project_id','url']]
    print (df_uncrawled_projects)
    print(df_uncrawled_urls)

    #print out uncrawled urls into csv after each crawl
    #df_uncrawled_urls.to_csv(os.path.join(path, r'Final_Uncrawled_ssirfinal2.csv'))

    #Call function to compare uncrawled urls files
    comp_frames()

