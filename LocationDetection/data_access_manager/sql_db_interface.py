import json
import sqlite3

from geopy.geocoders import Nominatim


class LocationDBManager:
    def __init__(self, database_path):
        self.database_path = database_path
        self.geolocator = Nominatim(user_agent='geoapiExercises', timeout=10)

    def sqlite_select(self, table, cols, conds=dict(), sort_by=str()):
        conn = sqlite3.connect(self.database_path)
        if conds:
            if len(conds) > 1:
                where_cond = ' AND '.join(f'LOWER({cond})=LOWER(:{cond})' for cond in conds.keys())
            else:
                where_cond = ' '.join(f'LOWER({cond})=LOWER(:{cond})' for cond in conds.keys())
        else:
            where_cond = ' 1=1 '

        sql = f'SELECT {", ".join(cols)} FROM {table} WHERE {where_cond}'

        if sort_by:
            sql = sql + f' order by {sort_by} DESC '
        result = conn.cursor().execute(sql, conds)
        return self.get_list_of_dict(keys=cols, list_of_tuples=result)

    @staticmethod
    def get_list_of_dict(keys, list_of_tuples):
        """
        This function will accept keys and list_of_tuples as args and return list of dicts
        """
        list_of_dict = [dict(zip(keys, values)) for values in list_of_tuples]
        return list_of_dict

    def sqlite_insert(self, table, rows, replace_existing=False):
        conn = sqlite3.connect(self.database_path)
        cols = ', '.join('"{}"'.format(col) for col in rows.keys())
        vals = ', '.join(':{}'.format(col) for col in rows.keys())
        replace = ''
        if replace_existing:
            replace = 'OR REPLACE'
        sql = f'INSERT {replace} INTO "{table}" ({cols}) VALUES ({vals})'

        affected_rows = conn.cursor().execute(sql, rows)
        conn.commit()
        return affected_rows.rowcount

    def get_city_info_online(self, query):
        locations = self.geolocator.geocode(query, exactly_one=False, language='en', namedetails=False,
                                            addressdetails=True,
                                            extratags=True, )
        if locations:
            locs_row = [l.raw for l in locations]
            locs_row_sorted = sorted(locs_row, key=lambda d: d['importance'], reverse=True)
            return locs_row_sorted
        return []

    def get_location_info(self, q_loc):
        q_loc = q_loc.lower()

        already_exists_loc = self.sqlite_select(table='location_info',
                                                cols=['loc_name', 'loc_info'], conds={'loc_name': q_loc})

        if already_exists_loc:
            return json.loads(already_exists_loc[0]['loc_info'])
        else:
            # query online:
            loc_info = self.get_city_info_online(q_loc)
            if loc_info:
                rows = {
                    'loc_name': q_loc,
                    'loc_info': json.dumps(loc_info)
                }
                self.sqlite_insert(table='location_info', rows=rows, replace_existing=True)
            return loc_info


# if __name__ == "__main__":
#     loc_db_mng = LocationDBManager(database_path='data/locationdb.db')
#     info = loc_db_mng.get_location_info(q_loc='Syria')
#     print(info)
