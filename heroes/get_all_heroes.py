from ruamel.yaml import YAML

from nick_bot.datas.OverwatchDB import OverwatchDB
from nick_bot.datas.OverwatchApi import OverwatchApi

yaml = YAML()
config = yaml.load(open("../config/config.yaml"))

overwatch_api = OverwatchApi(config['api'])
overwatch_database: OverwatchDB = OverwatchDB(config['database'])

roles = overwatch_api.get_roles()

heroes = list()
for role in roles:
    role_heroes = overwatch_api.get_heroes_by_role(role['key'])
    heroes += role_heroes

overwatch_database.delete_all_heroes()
overwatch_database.insert_heroes(heroes)
