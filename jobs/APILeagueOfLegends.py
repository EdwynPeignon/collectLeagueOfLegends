#!/data/league_of_legend/virtualenvs/leagueOfLegends/bin/python
import time
import requests
import datetime
import json
import os
import jobs.elastic_api as elk_api


class APILeagueOfLegends:

    def __init__(self, yp):
        self.api_key = yp.api_key
        self.path = yp.path_storage
        self.since_season = yp.since_season

    # Get the information of the summoner thanks to his name and his region
    def summoner_info(self, user_name, region='euw1'):
        api_request = 'https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}'.format(region, user_name)
        return self.send_request(self.format_request(api_request))

    # Get all the match history of the player thanks to his account and region
    def summoner_match_history(self, account_id, region='euw1', **kwargs):
        api_request = 'https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}'.format(region, account_id)
        return self.send_request(self.format_request(api_request, **kwargs))

    # Summoner match history send hundred matches so we have to repeat the operation to get all the match since the
    # latest season
    def collect_all_matches(self, name, platform):
        sum_info = self.summoner_info(name, platform)
        if sum_info is None:
            return None
        else:
            account_id = sum_info['accountId']

        index = 0
        bool_season = True
        matches = list()

        while bool_season:
            response = self.summoner_match_history(account_id, beginIndex=index, endIndex=(index + 100))
            for match in response['matches']:
                if match['season'] >= self.since_season:
                    matches.append((match["gameId"], match['platformId']))
                else:
                    bool_season = False
            index += 100

        return matches

    @staticmethod
    # Epoch times to datetime format
    def epoch_mill_date(epoch):
        s = epoch / 1000
        return datetime.datetime.fromtimestamp(s).strftime('%Y/%m/%d %H:%M:%S')

    # Get all the match information
    def match_info(self, match_id, region='euw1', **kwargs):
        api_request = 'https://{}.api.riotgames.com/lol/match/v4/matches/{}'.format(region, match_id)
        return self.send_request(self.format_request(api_request, **kwargs))

    # Get the match timeline
    def match_timeline(self, match_id, region='euw1', **kwargs):
        api_request = 'https://{}.api.riotgames.com/lol/match/v4/timelines/by-match/{}'.format(region, match_id)
        return self.send_request(self.format_request(api_request, **kwargs))

    # Add all the arguments to the query GET
    def format_request(self, api_request, **kwargs):
        api_request += '?'
        for key, value in kwargs.items():
            api_request += '{}={}&'.format(key, value)
        return api_request + 'api_key=' + self.api_key

    def send_request(self, api_request):
        response = requests.get(api_request)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(response.headers)
            time.sleep(int(response.headers['Retry-After']) + 1)
            return self.send_request(api_request)
        elif response.status_code == 404:
            print('Data not found : {}'.format(api_request))
            return None
        elif response.status_code == 403:
            print('Access Forbidden check the validity of your api key : {}'.format(api_request))
            exit()
        elif response.status_code == 500 or response.status_code == 503:
            print('Problem from the server check the status for the servers.')
        else:
            print('problem undefined here the api request : {}'.format(api_request))
            print('Here is the error {}'.format(response))
            exit()

    def index_master_data(self, json_game, bool_match, bool_timeline):
        uri_match = '/{}/season_{}/queue_{}/match/match_{}.json'.format(json_game['platformId'],
                                                                        json_game['seasonId'],
                                                                        json_game['queueId'],
                                                                        json_game['gameId']) if bool_match else ''
        uri_timeline = '/{}/season_{}/queue_{}/timeLine/timeLine_{}.json'.format(json_game['platformId'],
                                                                                 json_game['seasonId'],
                                                                                 json_game['queueId'],
                                                                                 json_game['gameId']) \
            if bool_timeline else ''

        json_elastic = {"champion100": [i['championId'] for i in json_game['participants'] if i['teamId'] == 100],
                        "champion200": [i['championId'] for i in json_game['participants'] if i['teamId'] == 200],
                        "player100": [i['player']['summonerName'] for i in json_game['participantIdentities'] if
                                      json_game['participants'][i['participantId'] - 1]['teamId'] == 100],
                        "player200": [i['player']['summonerName'] for i in json_game['participantIdentities'] if
                                      json_game['participants'][i['participantId'] - 1]['teamId'] == 200],
                        "queueId": json_game['queueId'],
                        "remake": json_game['gameDuration'] < 280,
                        "gameDuration": json_game['gameDuration'],
                        "date": self.epoch_mill_date(json_game['gameCreation']),
                        "gameVersion": json_game['gameVersion'],
                        "platform": json_game['platformId'],
                        "season": json_game['seasonId'],
                        "win": 100 if json_game['participants'][0]['stats']['win'] else 200,
                        "uri_match": uri_match,
                        "uri_timeLine": uri_timeline
                        }
        response = elk_api.index_json(json_elastic, json_game['gameId'])
        if response['result'] != 'created' and response['result'] != 'updated':
            print(response)
            print('Error indexing elk : {}'.format(json_game['gameId']))

    def data_storage(self, json_match, json_write, type_json):
        directory = '{}{}/season_{}/queue_{}/{}/'\
            .format(self.path, json_match['platformId'], json_match['seasonId'], json_match['queueId'], type_json)
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except Exception as e:
                print(e)
        try:
            path = '{}{}_{}.json'.format(directory, type_json, json_match['gameId'])
            with open(path, 'w') as f:
                    json.dump(json_write, f, ensure_ascii=False)
            return True
        except Exception as e:
            print('Error : {} \n storage game Id : {}'.format(e, json_match['gameId']))
            exit()
