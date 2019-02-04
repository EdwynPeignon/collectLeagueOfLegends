import jobs.APILeagueOfLegends as api_LOL
from jobs.yamlParser import YamlParser
import random
import jobs.elastic_api as elk


# Check if the id of the match are already indexed in Elasticsearch and so in your hard drive
def check_matches_elastic(matches):
    ids_matches = [match[0] for match in matches]
    check_match = elk.check_list_match(ids_matches)
    matches_not_in_elastic = [int(response.get('_id')) for response in check_match['docs'] if not response.get('found')]
    print('Number of matches of the player : {}'.format(len(matches)))
    print('Number already in elastic : {}'.format(len(matches) - len(matches_not_in_elastic)))
    return [match for match in matches if match[0] in matches_not_in_elastic]


def collect_data_player(api, list_players, name, platform, yp):
    print(name, platform)

    matches = api.collect_all_matches(name, platform)
    if matches is None:
        print('No matches for this player maybe he changes his name.')
        return list_players
    if yp.index_elastic:
        matches = check_matches_elastic(matches)

    for match_id, match_platform in matches:
        json_game = api.match_info(match_id, match_platform)
        if json_game is None:
            print("Didn't find match info for game Id: {}".format(match_id))
            continue
        uri_match = False
        uri_timeline = False

        if yp.match_timeline:
            json_timeline = api.match_timeline(match_id, match_platform)
            if json_timeline is None:
                print("Didn't find match timeline for game Id: {}".format(match_id))
                continue
            uri_timeline = api.data_storage(json_game, json_timeline, 'timeLine')

        if yp.match_info:
            uri_match = api.data_storage(json_game, json_game, 'match')

        if yp.index_elastic:
            api.index_master_data(json_game, uri_match, uri_timeline)

        if len(list_players) < size_max:
            for player in json_game['participantIdentities']:
                list_players.add((player['player']['summonerName'], json_game['platformId']))

    print("list_player size : {}".format(len(list_players)))
    return list_players


size_max = 10000
list_players = set()

yp = YamlParser()
print(yp)
api = api_LOL.APILeagueOfLegends(yp)

for player, platform in yp.players:
    list_players = collect_data_player(api, list_players, player, platform, yp)

while True:
    player = random.sample(list_players, 1)[0]
    new_list_player = list_players
    list_players = set()
    for i in new_list_player:
        if i != player:
            list_players.add(i)
    list_players = collect_data_player(api, list_players, player[0], player[1], yp)


