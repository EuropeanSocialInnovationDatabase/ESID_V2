import argparse
import os

from tqdm import tqdm

from data_access_manager.data_collector import DataCollector
from location_detect_algorithm.location_detection import LocationDetection


def main(collection_name, projects_files_path=None):
    p_collector = DataCollector()
    loc_detect = LocationDetection()


    tmp = [
        'crawl20190109_translated',
        'crawl20180801_wayback_translated'
     ]
    for collection_name in tmp:
        print(collection_name)
        mysql_ids = p_collector.get_mysql_projects_ids()

        if projects_files_path is None:
            mongo_ids = p_collector.get_mongodb_projects_ids(collection_name, old_collection=True)
            project_ids = set(mongo_ids).difference(mysql_ids)
        elif os.path.exists(projects_files_path):
            with open(projects_files_path) as rdr:
                external_ids = [int(x.strip()) for x in rdr.readlines()]
                project_ids = set(external_ids).difference(mysql_ids)
        else:
            project_ids = []
        for project_id in tqdm(project_ids, "Predicting projects location"):

            project_data = p_collector.get_text_mongodb(project_id=project_id, collection_name=collection_name, old_collection = True)
            loc_info = loc_detect.location_detection_logic(project_data=project_data)

            # This line needs to be activated. However, we stop it while testing to avoid any wrong entry into the database.
            inserted = p_collector.insert_predictions(project_id=project_id, location_information=loc_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', default='All_Collection', help="MongoDB Collection name")
    parser.add_argument('-p', '--projects', default=None,
                        help="Path to a text file of project IDs to predict their locations")
    args = parser.parse_args()

    main(args.collection, args.projects)
