import yaml


class YamlParser:

    def __init__(self):
        try:
            yaml_config = yaml.load(open('config/config.yaml'))
        except FileNotFoundError:
            print("Verify your config file.")

        if yaml_config.get('api_key') is None:
            print('Please indicate your api key.')
            exit()

        if yaml_config.get('path_storage') is None:
            print('Please indicate your a path to your storage.')
            exit()

        if yaml_config.get('index_elastic') is True:
            if yaml_config.get('elastic') is None:
                print('You have to indicate the location where to communicate '
                      'with elastic often : http://localhost:9200')
                exit()

        self.index_elastic = False if yaml_config.get('index_elastic') is None else yaml_config.get('index_elastic')
        self.since_season = 8 if yaml_config.get('since_season') is None else yaml_config.get('since_season')
        self.match_info = True if yaml_config.get('match_info') is None else yaml_config.get('match_info')
        self.match_timeline = True if yaml_config.get('match_timeline') is None else yaml_config.get('match_timeline')
        self.players = [('Winter Kay', 'EUW1')] if yaml_config.get('players') is None \
            else [(player, platform) for player, platform in yaml_config.get('players').values()]
        self.elastic = yaml_config.get('elastic')
        self.path_storage = yaml_config.get('path_storage')
        self.api_key = yaml_config.get('api_key')
        self.index_name = 'league_of_legends' if yaml_config.get('index_name') is None \
            else yaml_config.get('index_name')
        self.type_name = 'master_data' if yaml_config.get('type_name') is None else yaml_config.get('type_name')

    def __str__(self):
        if self.index_elastic:
            return "Collect match info : {}, collect match timeline : {}\nSince season : {}, players : {}, " \
                   "path to your storage : {}, you're api key : {}\nElastic index name : {}, doc type name : {}"\
                .format(self.match_info, self.match_timeline, self.since_season, self.players,
                        self.path_storage, self.api_key, self.index_name, self.type_name)
        else:
            return "Collect match info : {}, collect match timeline : {}\nSince season : {}, players : {}," \
                   "path to your storage : {}, you're api key : {}".format(self.match_info, self.match_timeline,
                                                                           self.since_season, self.players,
                                                                           self.path_storage, self.api_key)

