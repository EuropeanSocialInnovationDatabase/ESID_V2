import re
from collections import Counter

import networkx as nx
import nltk
import numpy as np
import pandas as pd
import tldextract
from flair.data import Sentence
from flair.models import SequenceTagger
from nltk.corpus import stopwords
from sklearn.cluster import MeanShift

from data_access_manager.sql_db_interface import LocationDBManager


class LocationDetection:
    # To map some county names to their full name
    mapper = {
        "us": "United States",
        "u.s.": "United States",
        'usa': "United States",
        'uk': "United Kingdom",
        'ca': 'Canada',
        'ksa': "Saudi Arabia",
        'uae': 'United Arab Emirates',
        'de': "Germany",
        'es': "Spain",
        'co': 'Colombia'

    }

    # list of words where the location page could be located.
    keywords = ['about', 'contact', 'contacto', 'aboutus']

    # domains to ignore as they do NOT refer  to a county name

    pass_ext = ['io', 'cc', 'ai', 'me', 're', 'co', 'nu', 'ag']

    # continent_names to be ignored when paser by the NER model
    continent_names = ['africa', 'antarctica', 'asia', 'oceania', 'europe', 'europe union', 'americas', 'europe',
                       'east', 'south', 'west', 'north', 'upper', 'lower', 'st.']

    # External CSV file contains country names and their ISO code
    df = pd.read_csv('data/City-Region-Locations.csv', encoding='iso-8859-1')

    # function to convert country name to ISO code (based on a CSV file)
    country2code = df[['country_iso_code', 'country_name']].drop_duplicates().to_dict('records')
    country2code = {x['country_iso_code']: x['country_name'] for x in country2code}

    # collect popular loc names (cities and counties) from a CSV file. Then convert all to a small letter
    df_locs = pd.read_csv('data/worldcities_clean.csv', encoding='iso-8859-1')
    all_gt_locs = list(set([x.lower() for x in df_locs.city.tolist()] + [x.lower() for x in df_locs.country.tolist()]))

    # NLTK stopwords
    cachedStopWords = stopwords.words("english")

    # RE expression to remove stopwords
    pattern = re.compile(r'\b(' + r'|'.join(cachedStopWords) + r')\b\s*')

    # accepted cities:
    accepted_cities_types = ['administrative', 'city', 'town', 'village', 'residential', 'island', 'hamlet',
                             'suburb', 'region', 'government', 'state']

    # initialize the location detection model
    def __init__(self):
        # # load NER tagger model
        # # https://huggingface.co/flair/ner-english-ontonotes-large
        self.tagger = SequenceTagger.load("flair/ner-english-large")
        # tagger = SequenceTagger.load("dslim/bert-large-NER")

        # Clustering algorithm to identify when a project is spread over different counties
        self.ms = MeanShift(bandwidth=None, bin_seeding=True)

        # Location database to save country information instead of requesting the online API everytime.
        self.loc_db_mng = LocationDBManager(database_path='data/locationdb.db')

    def filter_project_pages(self, project_data, top_x=10):

        """
        When a project has many ULRs in MongoDB, we have to filter them. This function is to filter these pages and to
        take only the first level pages after the home page.
        :param project_data: a dictionary of the project webpages as collected from MongoDB
        :param top_x: number of minimum pages to be included. The URLs are sorted by their length.
        :returns a list of the selected pages content
        """

        if isinstance(project_data, dict):
            project_data = [project_data]
        all_data_filtered = []
        url_len_dict = {}

        # check all the URLs and get only the home page and first level pages
        for idx, sample in enumerate(project_data):
            url = sample.get('url')
            text = sample['content']

            # if a page has no text, ignore the URL
            if not text:
                continue

            # clean the ULR to get its length
            if url:
                url_len_dict[idx] = len(url)
                url = sample['url'].replace('https://', '').replace('http://', '')
                if url.endswith('/'):
                    url = url[:-1]

                # if a URL is from the home page or the first sub-page OR has one of the keywords, like (About us,
                # contact us, contacto) add it to the list
                if len(url.split('/')) <= 2 or [x for x in self.keywords if x in url]:
                    if sample not in all_data_filtered:
                        all_data_filtered.append(sample)
            else:
                # if no ULR was detected, return the same input
                if sample not in all_data_filtered:
                    all_data_filtered.append(sample)

        if all_data_filtered and url_len_dict:
            shortest_sample = all_data_filtered[(min(zip(url_len_dict.keys(), url_len_dict.values()))[0])]
            sample_with_keywords = [p for p in all_data_filtered if [w for w in self.keywords if w in p['url']]]
            if sample_with_keywords:
                sample_with_keywords.append(shortest_sample)
                return sample_with_keywords

        # if no home page and no second level page, take only the page with the shortest URL
        if not all_data_filtered:
            min_idx = min(zip(url_len_dict.keys(), url_len_dict.values()))[0]
            all_data_filtered.append(project_data[min_idx])

        # if a project has a huge number of pages with take the top short top_x pages
        if len(all_data_filtered) > top_x:
            new_all_data_filtered = [p['url'] for p in all_data_filtered]
            x = {x: len(x) for x in new_all_data_filtered}
            enhanced_p = [k for k, v in sorted(x.items(), key=lambda item: item[1])][:top_x]
            return [y for y in all_data_filtered if y['url'] in enhanced_p]
        else:
            return all_data_filtered

    def correlated_cities(self, city_name):
        """
        function to link a city name with candidate countries. If the input was Glasgow, it will tell that Glasgow
        related to the UK and the US.
        :param city_name: the query city name
        :return dictionary of correlated countries and for each country, the city importance (based on the API).
        """

        # get city information from the location API (the API checks locally in a local database. If it does not exists,
        # it checks for the location information online).
        # we get only the first 4 candidate countries of a locations
        city_info = self.loc_db_mng.get_location_info(city_name)[:4]
        d = [
            (x['address'].get('country', '').lower(), ((len(city_info) - idx) / (idx + 1)) * x.get('importance', 0))
            for idx, x in enumerate(city_info)]
        corr_dict = dict()
        for a, b in d:
            if a in corr_dict:
                corr_dict[a] += b
            else:
                corr_dict[a] = b
        return corr_dict

    def build_graph(self, detected_countries, detected_cities):
        """
        function to build the locations graph
        :param detected_countries: list of the detected_countries in the project text
        :param detected_cities: list of the detected_cities in the project text
        : returns a directed graph
        """

        # initiate an empty graph
        grf = nx.DiGraph()

        # add the countries as nodes to the graph, with type "country".
        for src, src_freq in detected_countries.items():
            grf.add_node(src, type_='country', weight=src_freq)

        # add the cities as nodes to the graph, with type "city".
        for src, src_freq in detected_cities.items():
            if src not in grf:
                grf.add_node(src, type_='city', weight=src_freq)

        # add links between the city and its correlated countries based on the city correlation function
        for src_city, src_imp in detected_cities.items():
            cors_countries = self.correlated_cities(src_city)

            for cor_country, cor_country_weight in cors_countries.items():
                if cor_country not in grf:
                    # if county not in the graph, but we have a city related to it, give it a frq of 0.5
                    grf.add_node(cor_country, type_='country', weight=detected_countries.get(cor_country, 0.5))

                if not grf.has_edge(src_city, cor_country):
                    grf.add_edge(src_city, cor_country, weight=round(cor_country_weight, 2))

        return grf

    def cluster_candidate_countries(self, best_countries):
        """
        function to cluster candidate countries based on their probability.
        If a project has the following distribution:
        {
        "spain":100,
        "USA":96,
        "UK":95,
        "india":45,
        "France"33,
        "China":3
        }
        This function will cluster these countries and will tell that the project is in Spain, USA and UK, as their
        numbers are close to each other and they are the highest numbers.
        """

        def find_max_cluster_id(clustering_dict):
            max_cluster_id = 0
            best_id = 0
            for cluster_id, samples in clustering_dict.items():
                if samples[0][1] > max_cluster_id:
                    best_id = cluster_id
                    max_cluster_id = samples[0][1]
            return best_id

        try:
            X = list(best_countries.values())
            self.ms.fit(np.reshape(X, (-1, 1)))
        except:
            # if we face an exception while clustering --> take only the first country
            return [(k, v) for k, v in best_countries.items()][:1]

        clustering_dict = {}
        for (c, w), cat in zip(best_countries.items(), self.ms.labels_):
            if cat in clustering_dict:
                clustering_dict[cat].append((c, w))
            else:
                clustering_dict[cat] = [(c, w)]

        best_cluster_id = find_max_cluster_id(clustering_dict)
        return clustering_dict[best_cluster_id]

    @staticmethod
    def get_candidate_countries(grf, all_detected_cities):
        """
        Function to weight each country node on  the graph grf and return a sorted dictionary of countries with
        their scores
        :param grf: the locations graph
        : param all_detected_cities: a list of the detected cities in the project pages.
        """

        data = {}
        # for each node of type "country" do the following
        for node_name in grf.nodes:
            if grf.nodes[node_name]['type_'] == 'country':

                # get the country name
                country_cities = grf.in_edges(node_name, data=True)

                # get the country weight
                country_freq = grf.nodes[node_name].get('weight', 1)

                # if the country has cities, go on.
                if country_cities:
                    # for each city of this country get the following:
                    for city_info in country_cities:
                        # city name
                        city_name = city_info[0]
                        # city weight based on the location API
                        city_weight = city_info[2]['weight']
                        # city freq based on the text mention
                        city_freq = all_detected_cities.get(city_name, 1)

                        # accumulated the wright of each country based on the following formula:

                        # 70% of the city weight * city freq + 30% of the country freq

                        if node_name not in data:
                            data[node_name] = 0.7 * city_weight * city_freq + 0.3 * country_freq
                        else:
                            data[node_name] += 0.7 * city_weight * city_freq + 0.3 * country_freq
                else:
                    # weight the county only by its freq if does not have any city
                    data[node_name] = country_freq

                # finally, weight each country by its frequency.
                data[node_name] = data[node_name] * country_freq

        # sort the country nodes based on their weights.
        data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
        return data

    def find_locations_ner(self, text):
        """
        Function used NER to identify the location entities
        """

        detected_locs = {}
        # using NLTK split the text to sentences
        sentences = nltk.sent_tokenize(text)
        sentences = list(dict.fromkeys(sentences))

        # for each sentence, find the NE locations
        for s in sentences:
            sentence = Sentence(s)
            try:
                self.tagger.predict(sentence)
            except:
                continue

            # filter the entities to get only the LOC ones. (apply some cleaning to the detected NE)
            for entity in sentence.get_spans('ner'):
                if entity.tag in ['LOC'] and len(entity.text) >= 2:
                    entity_txt = self.pattern.sub('', entity.text)
                    entity_txt = re.sub(r'[0-9]+', ' ', entity_txt)
                    entity_txt = entity_txt.strip().lower()
                    if not entity_txt or len(entity_txt) <= 2:
                        continue

                    entity_txt = self.mapper.get(entity_txt.lower(), entity_txt)

                    if set(entity_txt.lower().split()).intersection(self.continent_names):
                        continue

                    if entity_txt not in detected_locs:
                        detected_locs[entity_txt] = 1
                    else:
                        detected_locs[entity_txt] = detected_locs[entity_txt] + 1

        detected_locs_matcher = {w: text.lower().count(w) for w in self.all_gt_locs if w in text.lower().split()}

        keys = set(detected_locs.keys()).union(detected_locs_matcher.keys())
        output = {k: max(detected_locs.get(k, float('-inf')), detected_locs_matcher.get(k, float('-inf'))) for k in
                  keys}

        output_sorted = {k: v for k, v in sorted(output.items(), key=lambda item: item[1], reverse=True)}
        return output_sorted

    def recover_country_from_url(self, url):
        """
        function to get the country name from its url prefix. for example, if URL is https://XXXXX.es --> Spain
        """

        # get country by code:
        def get_country_by_iso_code(country_code):
            return self.country2code.get(country_code.upper(), '')

        def get_url_suffix(url):
            if url:
                return tldextract.extract(url).suffix.lower().split('.')[-1]
            return 'com'

        suff = get_url_suffix(url)
        if suff in self.pass_ext:
            return ''
        return get_country_by_iso_code(get_url_suffix(url))

    @staticmethod
    def find_countries(e_data, detected_locs):
        """
        Function to get the locations from type "country" from the detected locations.
        """
        detected_countries = {}
        for c, fq in detected_locs.items():
            if c not in e_data:
                continue
            for x in e_data[c]:
                if isinstance(x['extratags'], dict) and x['extratags'].get('linked_place') == 'country':
                    country_name = x.get('address').get('country').lower()
                    if country_name in detected_countries:
                        detected_countries[country_name] = detected_countries[country_name] + fq
                    else:
                        detected_countries[country_name] = fq
        return detected_countries

    @staticmethod
    def find_cities(all_detected_countries, detected_locs):
        """
        Function to get the locations from type "city" from the detected locations.
        """
        all_detected_cities = {}
        for k, v in detected_locs.items():
            if k not in all_detected_countries:
                all_detected_cities[k] = v
        return all_detected_cities

    @staticmethod
    def get_candidate_cities(g, best_country, detected_cities):
        """
        Once the contry/countries list is defined, this function finds the best city of each country based on
        the location graphy
        """
        if best_country:
            candidate_cities = {}
            for connected_city in g.in_edges(best_country, data=True):
                city_name = connected_city[0]
                city_weight = connected_city[2].get('weight', 0)
                city_freq = detected_cities.get(city_name, 0)
                if city_name not in candidate_cities:
                    candidate_cities[city_name] = city_weight * city_freq
            candidate_cities = {k: v for k, v in
                                sorted(candidate_cities.items(), key=lambda item: item[1], reverse=True)}
            return candidate_cities
        return {}

    def location_detection_logic(self, project_data):

        """
        This function manages the logic of location detection algorithm
        """

        # select a few number of web pages from the project pages to find the location information. Max 10 pages
        pages = self.filter_project_pages(project_data=project_data, top_x=10)

        detected_locs = dict()
        suffix_country = ''

        # iterate over the project pages to loc for locations
        for page_idx, page in enumerate(pages):

            # find the project URL to check the URL suffix
            suffix_country = self.recover_country_from_url(url=pages[0]['url'])
            suffix_country = suffix_country.lower()

            # extract the text of the project taking only the first 10K words (to avoid huge text processing)
            if len(page.get('content', '').split()) > 10000:
                page['content'] = ' '.join(page.get('content', '').split()[:10000])

            # find NE loc in the project text and accumulate them for each page in the project
            sub_detected_locs = self.find_locations_ner(page.get('content', ''))
            detected_locs = dict(Counter(sub_detected_locs) + Counter(detected_locs))
            detected_locs = {self.mapper.get(k.lower(), k.lower()): v for k, v in detected_locs.items()}

        # e_data will hold the information of each loc from the loc API.
        e_data = dict()
        # for each detected loc --> find loc info.
        for element, freq in detected_locs.items():
            try:
                country_info_list = self.loc_db_mng.get_location_info(element)
            except:
                continue
            if country_info_list:
                e_data[element] = country_info_list

        # filter the detected locations into countries and cities
        all_detected_cities, all_detected_countries = dict(), dict()
        detected_countries = self.find_countries(e_data, detected_locs)
        all_detected_countries = dict(Counter(detected_countries) + Counter(all_detected_countries))

        detected_cities = self.find_cities(all_detected_countries, detected_locs)
        all_detected_cities = dict(Counter(detected_cities) + Counter(all_detected_cities))

        # build the location graph
        G = self.build_graph(all_detected_countries, all_detected_cities)
        # over weight the node if we have a suffix
        if suffix_country and detected_countries and suffix_country in G:
            G.nodes[suffix_country]['weight'] = G.nodes[suffix_country]['weight'] * 100

        # find candidate countries
        best_countries = self.get_candidate_countries(G, all_detected_cities)
        # cluster them based on their probability
        final_countries = self.cluster_candidate_countries(best_countries)

        # get the cities of the candidate countries
        final_result = []
        for country in final_countries:
            cities = list(self.get_candidate_cities(G, best_country=country[0], detected_cities=all_detected_cities))
            if cities:
                city = cities[0]
            else:
                city = ''
            if country[0] or city:
                final_result.append((country[0], city))

        result = []

        # build the country information (lat, lon, capital, iso, etc.)
        for country, city in final_result:
            city_info = None
            if city:
                cities_info = e_data.get(city)
                for c in cities_info:
                    if c.get('address', {}).get('country', '').lower() == country:
                        city_info = c
                        break
                    # else:
                    #     print('We should BE here never!!!')

            country_info = e_data.get(country, self.loc_db_mng.get_location_info(country))[0]
            city_type = city_info.get('type', '') if city_info else ''
            city_type = city_type if city_type in self.accepted_cities_types else ''

            result.append({
                'city_name': city_info.get('display_name', ',').split(',')[0] if city_type and city_info else '',
                'city_type': city_type,
                'country_name': country_info.get('display_name') if country_info else '',
                'country_ISO3166-1:alpha3': country_info['extratags'].get('ISO3166-1:alpha3') or country_info[
                    'extratags'].get('not:ISO3166-1:alpha3'),

                'lat_city': city_info.get('lat', '') if city_type and city_info else '',
                'lon_city': city_info.get('lon', '') if city_type and city_info else '',

                'lat_country': country_info.get('lat', '') if country_info else '',
                'lon_country': country_info.get('lon', '') if country_info else '',

                'wikidata_city': city_info.get('extratags', dict()).get('wikidata') if city_type and city_info else '',
                'wikidata_country': country_info.get('extratags', dict()).get('wikidata') if country_info else '',

            })
        return result
