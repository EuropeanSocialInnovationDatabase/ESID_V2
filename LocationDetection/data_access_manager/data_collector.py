"""
Class to collect/ upload data to the Database (MySQL) and MongoDB
"""

import pymongo
import pymysql as MySQLdb
from sshtunnel import SSHTunnelForwarder

from data_access_manager.database_access import *


class DataCollector:

    def __init__(self, ):

        try:
            client = pymongo.MongoClient(serverSelectionTimeoutMS=30000)

            # get the mongoDB database instance
            self.mongo_db = client[MONGO_DB_NAME]

            self.mysql_conn = MySQLdb.connect(host='127.0.0.1',
                                              user=MYSQL_USERNAME,
                                              password=MYSQL_PASS,
                                              database=MYSQL_DB_NAME,
                                              charset='utf8')
            self.mysql_cursor = self.mysql_conn.cursor()
        except:

            # Since the database is hosted at the University, not locally, we need SSH Tunnel to connect.
            # If you want to use this code from the server, not locally from your computer, you do NOT need for a tunnel
            # If you run the code from your laptop, the VPN connection is needed.

            # Create a tunnel to connect to the server from outside with VPN
            self.mongodb_ssh_tunnel_server = SSHTunnelForwarder(
                SERVER_IP,
                ssh_username=SERVER_USERNAME,
                ssh_password=SERVER_PASSWORD,
                # 27017 is the default port for MongoDB
                remote_bind_address=('127.0.0.1', 27017)
            )

            # Start the SSH tunnel server
            self.mongodb_ssh_tunnel_server.start()

            # connect to mongoDB data base
            client = pymongo.MongoClient('127.0.0.1', self.mongodb_ssh_tunnel_server.local_bind_port)

            # get the mongoDB database instance
            self.mongo_db = client[MONGO_DB_NAME]

            # Create a tunnel to connect to the server from outside with VPN (MySql DB)
            self.mysql_ssh_tunnel_server = SSHTunnelForwarder(
                SERVER_IP,
                ssh_username=SERVER_USERNAME,
                ssh_password=SERVER_PASSWORD,
                remote_bind_address=('127.0.0.1', 3306)
            )

            # Start the tunnel server
            self.mysql_ssh_tunnel_server.start()

            # connect to the database
            self.mysql_conn = MySQLdb.connect(user=MYSQL_USERNAME,
                                              password=MYSQL_PASS,
                                              host='127.0.0.1',
                                              port=self.mysql_ssh_tunnel_server.local_bind_port,
                                              database=MYSQL_DB_NAME,
                                              charset='utf8', use_unicode=True, )

            self.mysql_cursor = self.mysql_conn.cursor()

    def get_mongodb_projects_ids(self, collection_name, old_collection=False):
        """
        get text from MongoDB
        :param collection_name: mongoDB collection name
        :return: the text of the project
        """

        if old_collection:
            cursor = self.mongo_db[collection_name]
            ids = [int(p_id) for p_id in cursor.find().distinct('mysql_databaseID')]
        else:
            cursor = self.mongo_db[collection_name]
            ids = [int(p_id) for p_id in cursor.find().distinct('database_project_id')]

        return list(set(ids))

    def get_mysql_projects_ids(self):
        sql = "SELECT DISTINCT Projects_idProjects FROM ProjectLocationNew" \
              " WHERE Version='v2' and DataTrace ='Predicted by Location Algorithm V2.0'"
        self.mysql_cursor.execute(sql)
        res = self.mysql_cursor.fetchall()
        return [x[0] for x in list(set(res)) if len(x) > 0]

    def get_text_mongodb(self, project_id, collection_name, old_collection=False):
        """
        get text from MongoDB
        :param project_id: the ID of the project, can be string.
        :param collection_name: mongoDB collection name
        :param old_collection:
        :return: the text of the project
        """

        all_docs = []
        if not old_collection:
            cursor = self.mongo_db[collection_name]
            found_projects = cursor.find({"database_project_id": int(project_id)})
            for document in found_projects:
                del document['_id']
                all_docs.append(document)

        else:

            # query the DB
            documents = self.mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)})
            documents2 = self.mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)})
            for document in documents:
                all_docs.append(document)

            for document in documents2:
                all_docs.append(document)

            for doc in all_docs:
                doc['database_url'] = doc.get('url', '')
                doc['database_project_id'] = doc.get('mysql_databaseID', '')
                doc['projectname'] = doc.get('name', '')
                doc['content'] = doc.get('translation', '')

        return all_docs

    def create_location_table(self):
        self.mysql_cursor.execute("""
            CREATE TABLE ProjectLocationNew (                
               
               LocationID int NOT NULL AUTO_INCREMENT,               
               LocationType varchar(100) DEFAULT NULL,   
               Address varchar(500) CHARACTER SET utf8 DEFAULT NULL,                              
               CityName varchar(500) CHARACTER SET utf8 DEFAULT NULL,
               CityType varchar(100) CHARACTER SET utf8 DEFAULT NULL,
               CityWiki varchar(100) CHARACTER SET utf8 DEFAULT NULL,
               CityLongitude varchar(100) DEFAULT NULL,
               CityLatitude varchar(100) DEFAULT NULL,                              
               CountryName varchar(1000) CHARACTER SET utf8 DEFAULT NULL,
               CountryLongitude varchar(100) DEFAULT NULL,
               CountryLatitude varchar(100) DEFAULT NULL,
               CountryISOName varchar(100) CHARACTER SET utf8 DEFAULT NULL,
               CountryWiki varchar(100) CHARACTER SET utf8 DEFAULT NULL,                              
               Postcode varchar(100) CHARACTER SET utf8 DEFAULT NULL,
               PhoneContact varchar(100) CHARACTER SET utf8 DEFAULT NULL,
               EmailContact varchar(100) CHARACTER SET utf8 DEFAULT NULL,                                 
               Projects_idProjects int NOT NULL,
               Original_idProjects int DEFAULT NULL,               
               Version varchar(100) DEFAULT 'v2',
               DataTrace varchar(200) DEFAULT NULL,               
               PRIMARY KEY (LocationID)               
             ) 
                """)
        self.mysql_conn.commit()
        print('table created')

    def insert_predictions(self, project_id, location_information):

        def already_exists(project_id, country_name):
            sql = "SELECT * from ProjectLocationNew WHERE " \
                  " Projects_idProjects = %s AND  CountryName = %s" \
                  " AND Version = 'v2' AND DataTrace = 'Predicted by Location Algorithm V2.0'"
            val = (project_id, country_name)

            self.mysql_cursor.execute(sql, val)
            rows = self.mysql_cursor.fetchall()
            if len(rows) > 0:
                return True
            return False

        project_id = int(project_id)

        # if the project does not have a location, insert all empty:
        if len(location_information) == 0:
            sql = f"""
                insert into ProjectLocationNew (
                Projects_idProjects,
                Version,
                DataTrace
                ) VALUES (%s,%s,%s)
                """
            val = (project_id,
                   'v2',
                   'Predicted by Location Algorithm V2.0'
                   )
            self.mysql_cursor.execute('SET NAMES utf8;')
            self.mysql_cursor.execute('SET CHARACTER SET utf8;')
            self.mysql_cursor.execute('SET character_set_connection=utf8;')
            self.mysql_cursor.execute(sql, val)
            self.mysql_conn.commit()

        # iterate over the dataframe and insert the rows one by one. If a project already exists, it will be updated
        for loc_idx, loc_info in enumerate(location_information):

            if loc_idx == 0:
                location_type = 'Main Location'
            else:
                location_type = 'Secondary Location'
            city_name = loc_info.get('city_name', '')
            city_type = loc_info.get('city_type', '')

            city_latitude = loc_info.get('lat_city', '')
            city_longitude = loc_info.get('lon_city', '')

            city_wiki = loc_info.get('wikidata_city', '')

            country_name = loc_info.get('country_name', '')

            country_latitude = loc_info.get('lat_country', '')
            country_longitude = loc_info.get('lon_country', '')

            country_iso_name = loc_info.get('country_ISO3166-1:alpha3', '')
            country_wiki = loc_info.get('wikidata_country', '')

            version = 'v2'
            data_trace = 'Predicted by Location Algorithm V2.0'

            if already_exists(project_id=project_id, country_name=country_name):
                continue

            sql = f"""
                insert into ProjectLocationNew (
                Projects_idProjects,
                LocationType,                
                CityName,
                CityType,
                CityWiki,      
                CityLongitude,      
                CityLatitude,                
                CountryName,
                CountryLongitude,
                CountryLatitude,
                CountryISOName,
                CountryWiki,                
                Version,
                DataTrace                                            
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """

            val = (project_id,
                   location_type,
                   city_name,
                   city_type,
                   city_wiki,
                   city_longitude,
                   city_latitude,
                   country_name,
                   country_longitude,
                   country_latitude,
                   country_iso_name,
                   country_wiki,
                   version,
                   data_trace
                   )

            self.mysql_cursor.execute('SET NAMES utf8;')
            self.mysql_cursor.execute('SET CHARACTER SET utf8;')
            self.mysql_cursor.execute('SET character_set_connection=utf8;')
            self.mysql_cursor.execute(sql, val)
            self.mysql_conn.commit()

    def free_select_sql(self, sql):

        self.mysql_cursor.execute(sql)
        res = self.mysql_cursor.fetchall()

        # Save the SELECT command output
        import csv
        with open('Project_Location_New_coll_DB_tmp.csv', 'w', encoding='utf-8', newline='') as out:
            csv_out = csv.writer(out)
            for row in res:
                csv_out.writerow(row)

        return res


if __name__ == '__main__':
    data_collector = DataCollector()
    location_information = [{
        'city_name': 'Fintry',
        'city_type': 'village',
        'country_name': 'United Kingdom',
        'country_ISO3166-1:alpha3': 'GBR',
        'lat_city': '56.0531944',
        'lon_city': '-4.223376',
        'lat_country': '54.7023545',
        'lon_country': '-3.2765753',
        'wikidata_city': 'Q1026796',
        'wikidata_country': 'Q145'
    }]

    # create the table
    # data_collector.create_location_table()

    # insert a dummy record
    # data_collector.insert_predictions(project_id='43373', location_information=location_information)

    # check all the selected records
    loc = data_collector.free_select_sql('SELECT * FROM ProjectLocationNew')

    # Insert Loc from the Loc Detec algorithm
    # all_docs_old = data_collector.get_text_mongodb(project_id='43373', collection_name='new_crawl_simra2_280322',
    #                                                old_collection=False)
    #
    # all_docs_new = data_collector.get_text_mongodb(project_id='2044', collection_name="crawl20190109_translated",
    #                                                old_collection=True)
