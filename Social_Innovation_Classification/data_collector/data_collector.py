"""
Class to collect/ upload data to the Database (MySQL) and MongoDB
"""

import pymysql as MySQLdb
import pandas as pd
import pymongo
# from sshtunnel import SSHTunnelForwarder
from tqdm import tqdm

from database_access import host, username, password, database
from text_processing.text_processing_unit import TextProcessingUnit
from utils import clean_text, get_list_of_dict
import warnings

warnings.filterwarnings("ignore")

class DataCollector:
    # SERVER_IP = "*.*.*.*"
    MONGO_DB = "***"
    # SERVER_USERNAME = "****"
    # SERVER_PASSWORD = "****"

    # MYSQL_DB = "*******"
    # MYSQL_USER = "******"
    # MYSQL_PASS = "*******"

    def __init__(self):
        # self.mongodb_ssh_tunnel_server = None
        # self.mysql_ssh_tunnel_server = None

        # Since the database is hosted at the University, not locally, we need SSH Tunnel to connect.
        # If you want to use this code from the server, not locally from your computer, you do NOT need for a tunnel
        # If you run the code from your laptop, the VPN connection is needed.

        # # Create a tunnel to connect to the server from outside with VPN
        # self.mongodb_ssh_tunnel_server = SSHTunnelForwarder(
        #     self.SERVER_IP,
        #     ssh_username=self.SERVER_USERNAME,
        #     ssh_password=self.SERVER_PASSWORD,
        #     # 27017 is the default port for MongoDB
        #     remote_bind_address=('127.0.0.1', 27017)
        # )

        # Start the SSH tunnel server
        # self.mongodb_ssh_tunnel_server.start()

        # connect to mongoDB data base
        client = pymongo.MongoClient(serverSelectionTimeoutMS=30000)  # '127.0.0.1', #self.mongodb_ssh_tunnel_server.local_bind_port)

        # get the mongoDB database instance
        self.mongo_db = client[self.MONGO_DB]

        # # Create a tunnel to connect to the server from outside with VPN (MySql DB)
        # self.mysql_ssh_tunnel_server = SSHTunnelForwarder(
        #     self.SERVER_IP,
        #     ssh_username=self.SERVER_USERNAME,
        #     ssh_password=self.SERVER_PASSWORD,
        #     remote_bind_address=('127.0.0.1', 3306)
        # )

        # Start the tunnel server
        # self.mysql_ssh_tunnel_server.start()

        # connect to the database
        # self.mysql_conn = pymysql.connect(user=self.MYSQL_USER,
        #                                   password=self.MYSQL_PASS,
        #                                   host='127.0.0.1',
        #                                   port=3306, #self.mysql_ssh_tunnel_server.local_bind_port,
        #                                   database=self.MYSQL_DB)

        self.mysql_conn = MySQLdb.connect(host=host,
                                          user=username,
                                          password=password,
                                          database=database,
                                          charset='utf8')

        self.mysql_cursor = self.mysql_conn.cursor()

        # Instance from TextProcessingUnit; used to pre-process the text text
        self.text_processing_unit = TextProcessingUnit()

    def _get_text_mongodb(self, project_id, do_postprocessing=True):
        """
        get text from MongoDB
        :param project_id: the ID of the project, can be string.
        :param do_postprocessing: to clean the text afterward
        :return: the text of the project
        """

        # query the DB
        documents = self.mongo_db.crawl20190109_translated.find({"mysql_databaseID": str(project_id)},
                                                                no_cursor_timeout=True).batch_size(100)

        # This part of code is like Nikola's code.(ApplyModels.py)

        # Since the project is split into chunks, we iterate over these chunks and append them to a list
        # Append all text chunks into a list
        document_text = []
        for doc in documents:
            txt = doc.get('translation', '')
            # concatenate the translated texts stored in txt to documents_text, adding to that long document_text string
            document_text.append(txt)

        # I don't know why 350 threshold is set, I used exactly as mentioned in Nikola's code.
        if len(document_text) < 350 or "domain sale" in document_text:

            documents2 = self.mongo_db.crawl20180801_wayback_translated.find({"mysql_databaseID": str(project_id)},
                                                                             no_cursor_timeout=True).batch_size(100)

            for doc in documents2:
                document_text.append(doc.get('text', ''))

        # After we collect the code parts, we joint them into one piece of text
        text = '\n\n'.join(document_text)

        # clean the text if the do_postprocessing flag is active
        if text and do_postprocessing:
            text = clean_text(text)

        return text

    def _get_text_mysql(self, project_id, do_postprocessing=True):
        """
        get text from MySQl DB
        :param project_id: the ID of the project, can be string.
        :param do_postprocessing: to clean the text afterward
        :return: the text of the project
        """

        sql = f"""
        SELECT distinct(value) from AdditionalProjectData where Projects_idProjects={project_id}
        """

        self.mysql_cursor.execute(sql)
        list_of_tuples = self.mysql_cursor.fetchall()

        # Function to convert the output into a list of dicts. Each dict has the following keys
        output = get_list_of_dict(keys=['text'], list_of_tuples=list_of_tuples)

        mysql_text = ' '.join([x.get('text', '') for x in output]).strip()

        # Clean the text if the do_postprocessing flag is active
        if do_postprocessing:
            mysql_text = clean_text(mysql_text)

        return {
            'mysql_text': mysql_text,
            'project_id': str(project_id)
        }

    def load_training_set(self, project_ids=None, top_x=None):
        """
        Function to load the dataset from MySQL database.
         It selects from table "esid_prediction" the projects that have been annotated by human
        """

        sql = """
        SELECT
        Project_id,
        CriterionActors,
        CriterionInnovativeness,
        CriterionObjectives,
        CriterionOutputs         
        FROM esid_prediction WHERE AnnSource='HUMAN'         
        """

        if project_ids and isinstance(project_ids, list):
            sql = sql + f" AND Project_id IN ({','.join([str(x) for x in project_ids])})"

        if top_x and isinstance(top_x, int):
            sql = sql + f' limit {top_x}'

        self.mysql_cursor.execute(sql)
        list_of_tuples = self.mysql_cursor.fetchall()

        # converts the output into a list of dicts
        projects = get_list_of_dict(keys=[
            'Project_id',
            'CriterionActors',
            'CriterionInnovativeness',
            'CriterionObjectives',
            'CriterionOutputs'
        ],
            list_of_tuples=list_of_tuples)

        # extract the projects' text from the DB (from MySQL and MongoDB)
        for project in tqdm(projects, 'getting projects text from the DB'):
            project_id = project['Project_id']
            project['text'] = self.get_project_text(project_id)

        # return projects: which is a list of dict. each element has 6 keys, they are:
        # 'Project_id',
        # 'CriterionActors',
        # 'CriterionInnovativeness',
        # 'CriterionObjectives',
        # 'CriterionOutputs'
        # 'text'

        return pd.DataFrame(projects)

    def load_testing_set(self, project_ids=None):
        """
        Load the testing set from the esid_prediction table on the MySQL database.
        It returns a list of project IDs and their corresponding text.
        """

        # get the project IDs from a list provided by the user
        if not project_ids:
            all_p_sql = "SELECT distinct(idProjects) FROM EDSI_WESAM.Projects"
            training_p_sql = "SELECT Project_id FROM esid_prediction WHERE AnnSource='HUMAN'"
            self.mysql_cursor.execute(all_p_sql)
            all_p_ids = [str(x[0]) for x in self.mysql_cursor.fetchall()]

            self.mysql_cursor.execute(training_p_sql)
            training_p_ids = [str(x[0]) for x in self.mysql_cursor.fetchall()]
            project_ids = set(all_p_ids).difference(training_p_ids)

        projects = []
        # Extract the text of the testing projects
        for project_id in tqdm(project_ids, 'Getting projects text from the DB'):
            text = self.get_project_text(project_id)
            projects.append({'Project_id': project_id, 'text': text})

        return pd.DataFrame(projects)

    def get_project_text(self, project_id):
        """
        Function to extract the project text from MySQL and MongoDB
        """

        # extract text from MySQL
        project_info = self._get_text_mysql(project_id, do_postprocessing=True)

        # extract text from MongoDB
        mongodb_text = self._get_text_mongodb(project_id, do_postprocessing=True)

        # Store the project into info a dict called "project_info".
        project_info['mongodb_text'] = mongodb_text

        # reduce the project text and save it to the dict
        project_info['reducedText'] = self.text_processing_unit.shorten_text(
            mysqldb_text=project_info['mysql_text'],
            mongodb_text=project_info['mongodb_text'])

        # return only the reduced text of the project.
        return project_info['reducedText']

    def project_already_exists(self, project_id, run_name):
        sql = f'SELECT * FROM esid_prediction ' \
              f'WHERE Project_id ="' + str(project_id) + '" AND expName="' + run_name + '"'
        self.mysql_cursor.execute(sql)
        rows = self.mysql_cursor.fetchall()
        if len(rows) > 0:
            return True
        return False

    def create_esid_predictions_table(self):
        self.mysql_cursor.execute("""
                CREATE TABLE esid_prediction (
                 Project_id TEXT,
                 CriterionObjectives TEXT,
                 CriterionActors TEXT,
                 CriterionOutputs TEXT,
                 CriterionInnovativeness TEXT,
                 Social_Innovation_overall TEXT,
                 AnnSource TEXT,
                 ModelName TEXT,
                 expName TEXT
                )
                """)
        self.mysql_conn.commit()
        print('table created')

    def insert_predictions(self, df_prediction):
        """
        function to save the classifier's output to the database
        param: df_prediction: is a dataframe contains the prediction result.
        The dataframe has the following columns:
        Project_id, CriterionObjectives, CriterionActors, CriterionOutputs, CriterionInnovativeness
        """

        projects_inserted_counter = 0
        projects_updated_counter = 0
        projects_failed = []

        # iterate over the dataframe and insert the rows one by one. If a project already exists, it will be updated
        for index, row in tqdm(df_prediction.iterrows(), "Inserting predictions into the DB"):
            Project_id = row['Project_id']
            CriterionObjectives = row['CriterionObjectives']
            CriterionActors = row['CriterionActors']
            CriterionOutputs = row['CriterionOutputs']
            CriterionInnovativeness = row['CriterionInnovativeness']
            Social_Innovation_overall = '-1'
            AnnSource = row['AnnSource']
            ModelName = row['ModelName']
            expName = row['expName']

            if self.project_already_exists(project_id=Project_id, run_name=expName):
                sql = f"""
                UPDATE esid_prediction 
                SET                
                CriterionObjectives='{CriterionObjectives}',
                CriterionActors='{CriterionActors}',
                CriterionOutputs='{CriterionOutputs}',
                CriterionInnovativeness='{CriterionInnovativeness}',
                Social_Innovation_overall='{Social_Innovation_overall}',
                AnnSource='{AnnSource}',
                ModelName='{ModelName}'                
                WHERE
                Project_id='{Project_id}' and expName='{expName}' 
                """
            else:
                sql = f"""
                insert into esid_prediction (
                Project_id,
                CriterionObjectives,
                CriterionActors,
                CriterionOutputs,
                CriterionInnovativeness,      
                Social_Innovation_overall,      
                AnnSource,
                ModelName,
                expName
                ) VALUES (
                '{Project_id}',
                '{CriterionObjectives}',
                '{CriterionActors}',
                '{CriterionOutputs}',
                '{CriterionInnovativeness}',
                '{Social_Innovation_overall}',
                '{AnnSource}',
                '{ModelName}',
                '{expName}'
                )        
                """
            try:
                rows = self.mysql_cursor.execute(sql)

                if 'update' in sql.lower():
                    projects_updated_counter += rows
                else:
                    projects_inserted_counter += rows

            except:
                projects_failed.append(Project_id)
        try:
            self.mysql_conn.commit()
        except:
            return 0, len(df_prediction)
        return projects_inserted_counter, projects_updated_counter, projects_failed

    def free_select_sql(self, sql):
        self.mysql_cursor.execute(sql)
        res = self.mysql_cursor.fetchall()
        df = pd.DataFrame(res)
        # df.to_csv('tmp123.csv')
        print(f'Done!. The table has {len(df)} items!')
        return res


if __name__ == '__main__':
    data_collector = DataCollector()
    # data_collector.load_testing_set()
    data_collector.free_select_sql('select project_id from esid_prediction')
